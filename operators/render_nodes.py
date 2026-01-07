"""
Render Nodes Operators
    Description:
        Operators for generating compositor render nodes
        based on view layers and their enabled passes.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import bpy

from ..core import tools
from ..core.relative_path import build_base_path
from ..core.constants import SKIP_PASSES, DENOISE_PASSES, INVERT_Y_PASSES

if TYPE_CHECKING:
    from bpy.types import (
        BackgroundImage,
        CompositorNode,
        CompositorNodeOutputFile,
        CompositorNodeRLayers,
        Context,
        NodeSocket,
        NodeTree,
        Scene,
    )

logger = logging.getLogger(__name__)


def _has_denoising_data(render_layers_node: CompositorNodeRLayers) -> bool:
    """Checks if render layers node has denoising data outputs enabled."""
    denoising_normal = render_layers_node.outputs.get("Denoising Normal")
    denoising_albedo = render_layers_node.outputs.get("Denoising Albedo")
    return (
        denoising_normal and denoising_normal.enabled and
        denoising_albedo and denoising_albedo.enabled
    )


def _connect_pass_with_denoise(
    tree: NodeTree,
    output: NodeSocket,
    target_input: NodeSocket,
    render_layers_node: CompositorNodeRLayers,
    denoise_location: tuple[float, float]) -> None:
    """Connects a pass through a denoise node."""
    denoise_node = tools.create_denoise_node(
        tree,
        name="Denoise_{}".format(output.name),
        location=denoise_location
    )
    tree.links.new(output, denoise_node.inputs[0])
    tree.links.new(render_layers_node.outputs["Denoising Normal"], denoise_node.inputs[1])
    tree.links.new(render_layers_node.outputs["Denoising Albedo"], denoise_node.inputs[2])
    tree.links.new(denoise_node.outputs[0], target_input)
    logger.debug("Connected pass %s through denoise node", output.name)


def _connect_pass_with_invert(
    tree: NodeTree,
    output: NodeSocket,
    target_input: NodeSocket,
    invert_location: tuple[float, float]) -> None:
    """Connects a pass through a vector invert group for Y-up conversion."""
    invert_group = tools.create_vector_invert_group(
        tree,
        location=invert_location,
        name="Invert_{}".format(output.name)
    )
    tree.links.new(output, invert_group.inputs[0])
    tree.links.new(invert_group.outputs[0], target_input)
    logger.debug("Connected pass %s through invert group", output.name)


def _find_target_input(file_output_node: CompositorNodeOutputFile, slot_name: str) -> NodeSocket | None:
    """Finds the input socket matching the slot name."""
    for input_socket in file_output_node.inputs:
        if input_socket.name == slot_name:
            return input_socket
    return None


def _get_composite_render_layers(
    render_layers_nodes: list[CompositorNodeRLayers],
    scene: Scene) -> list[CompositorNodeRLayers]:
    """Returns render layer nodes that have use_composite enabled, sorted by sort order."""
    nodes = []

    for node in render_layers_nodes:
        view_layer = scene.view_layers.get(node.layer)
        if view_layer and view_layer.qq_render_use_composite:
            nodes.append((node, view_layer.qq_render_sort_order))

    nodes.sort(key=lambda x: x[1])
    sorted_nodes = [node for node, order in nodes]

    logger.debug("Found %d render layer nodes for composite sorted by order", len(sorted_nodes))
    return sorted_nodes


def _get_camera_background_image(scene: Scene) -> BackgroundImage | None:
    """Returns the first visible background image from the active camera."""
    camera = scene.camera

    if not camera:
        logger.debug("No active camera in scene")
        return None

    camera_data = camera.data

    if not camera_data.background_images:
        logger.debug("Camera %s has no background images", camera.name)
        return None

    visible_bg_images = [bg for bg in camera_data.background_images if bg.show_background_image]

    if not visible_bg_images:
        logger.debug("Camera %s has no visible background images", camera.name)
        return None

    bg_image = visible_bg_images[0]

    if bg_image.source != "IMAGE" or not bg_image.image:
        logger.debug("Background image source is not IMAGE or no image assigned")
        return None

    logger.debug("Found background image %s from camera %s", bg_image.image.name, camera.name)
    return bg_image


def _connect_passes(
    tree: NodeTree,
    render_layers_node: CompositorNodeRLayers,
    file_output_node: CompositorNodeOutputFile,
    use_denoise: bool = False,
    make_y_up: bool = False) -> None:
    """Connects all enabled passes from Render Layers to File Output."""
    rl_x = render_layers_node.location[0]
    rl_y = render_layers_node.location[1]

    middle_x_offset = 450
    middle_y_offset = 0

    has_denoise_data = _has_denoising_data(render_layers_node) if use_denoise else False

    for output in render_layers_node.outputs:
        if not output.enabled or output.name in SKIP_PASSES:
            continue

        slot_name = "Beauty" if output.name == "Image" else output.name
        file_output_node.file_slots.new(name=slot_name)
        target_input = _find_target_input(file_output_node, slot_name)

        if not target_input:
            continue

        should_denoise = use_denoise and has_denoise_data and output.name in DENOISE_PASSES
        should_invert = make_y_up and output.name in INVERT_Y_PASSES

        if should_denoise:
            denoise_location = (rl_x + middle_x_offset, rl_y + middle_y_offset)
            _connect_pass_with_denoise(tree, output, target_input, render_layers_node, denoise_location)
            middle_y_offset -= 30
        elif should_invert:
            invert_location = (rl_x + middle_x_offset, rl_y + middle_y_offset)
            _connect_pass_with_invert(tree, output, target_input, invert_location)
            middle_y_offset -= 30
        else:
            tree.links.new(output, target_input)

    logger.debug("Connected passes from %s to %s with use_denoise=%s make_y_up=%s",
                 render_layers_node.name, file_output_node.name, use_denoise, make_y_up)


def _create_alpha_chain(
    tree: NodeTree,
    count: int,
    start_location: tuple[float, float],
    x_offset: int) -> list[CompositorNode]:
    """Creates a chain of Alpha Over nodes and returns them as a list."""
    alpha_nodes = []
    current_x, current_y = start_location

    for i in range(count):
        alpha_node = tools.create_alpha_over_node(
            tree,
            (current_x + (i * x_offset), current_y),
            "Alpha_Over_{}".format(i + 1)
        )
        alpha_nodes.append(alpha_node)

        if i > 0:
            tree.links.new(alpha_nodes[i - 1].outputs[0], alpha_node.inputs[1])

    logger.debug("Created alpha chain with %d nodes", count)
    return alpha_nodes


def _connect_alpha_inputs(
    tree: NodeTree,
    alpha_nodes: list[CompositorNode],
    composite_nodes: list[CompositorNodeRLayers],
    image_node: CompositorNode | None) -> None:
    """Connects render layer nodes and optional image node to alpha chain."""
    has_background = image_node is not None

    if has_background:
        tree.links.new(image_node.outputs["Image"], alpha_nodes[0].inputs[1])
        for i, rl_node in enumerate(composite_nodes):
            if i == 0:
                tree.links.new(rl_node.outputs["Image"], alpha_nodes[0].inputs[2])
            else:
                tree.links.new(rl_node.outputs["Image"], alpha_nodes[i].inputs[2])
    else:
        tree.links.new(composite_nodes[0].outputs["Image"], alpha_nodes[0].inputs[1])
        for i, rl_node in enumerate(composite_nodes[1:], start=1):
            if i == 1:
                tree.links.new(rl_node.outputs["Image"], alpha_nodes[0].inputs[2])
            else:
                tree.links.new(rl_node.outputs["Image"], alpha_nodes[i - 1].inputs[2])

    logger.debug("Connected alpha inputs with background=%s", has_background)


def _build_composite_chain(
    tree: NodeTree,
    scene: Scene,
    composite_nodes: list[CompositorNodeRLayers],
    location: tuple[float, float]) -> CompositorNode | None:
    """Builds composite chain from render layer nodes with optional background image."""
    if not composite_nodes:
        logger.debug("No composite nodes provided")
        return None

    current_x, current_y = location
    x_offset = 200
    viewer_y_offset = -150

    bg_image = _get_camera_background_image(scene)
    image_node = tools.create_image_node(tree, bg_image, (current_x, current_y)) if bg_image else None
    has_background = image_node is not None

    current_x += 800

    total_inputs = len(composite_nodes) + (1 if has_background else 0)
    alpha_count = total_inputs - 1

    composite_x = current_x + (alpha_count * x_offset) + (200 if alpha_count else 0)
    composite_output = tools.create_composite_node(tree, (composite_x, current_y))
    viewer_node = tools.create_viewer_node(tree, (composite_x, current_y + viewer_y_offset))

    if total_inputs == 1:
        source_node = image_node if has_background else composite_nodes[0]
        tree.links.new(source_node.outputs["Image"], composite_output.inputs["Image"])
        tree.links.new(source_node.outputs["Image"], viewer_node.inputs["Image"])
        logger.debug("Connected single source to composite and viewer")
        return composite_output

    alpha_nodes = _create_alpha_chain(tree, alpha_count, (current_x, current_y), x_offset)
    _connect_alpha_inputs(tree, alpha_nodes, composite_nodes, image_node)

    last_alpha = alpha_nodes[-1]
    tree.links.new(last_alpha.outputs["Image"], composite_output.inputs["Image"])
    tree.links.new(last_alpha.outputs["Image"], viewer_node.inputs["Image"])

    logger.debug("Built composite chain with %d inputs at %s", total_inputs, location)
    return composite_output


class QQ_RENDER_OT_generate_nodes(bpy.types.Operator):
    """Generates compositor nodes for all renderable view layers."""

    bl_idname = "qq_render.generate_nodes"
    bl_label = "Generate Render Nodes"
    bl_description = "Generate File Output nodes for each view layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[str]:
        """Executes the node generation operator."""
        scene = context.scene
        view_layers = tools.get_renderable_view_layers(scene)

        if not view_layers:
            self.report({"WARNING"}, "No renderable view layers found")
            return {"CANCELLED"}

        tree = tools.setup_compositor(scene)

        if scene.qq_render_clear_nodes:
            tools.clear_nodes(tree)

        output_x_position = 800
        node_y_offset = tools.get_lowest_node_position(tree) - 50
        node_rl_offset = node_y_offset - 400
        render_layers_nodes = []

        for view_layer in view_layers:
            rl_location = (0, node_rl_offset)
            fo_location = (output_x_position, node_rl_offset)
            rl_node = tools.create_render_layers_node(tree, view_layer, rl_location)
            render_layers_nodes.append(rl_node)

            project_name = Path(bpy.data.filepath).stem if bpy.data.filepath else "untitled"
            base_path = build_base_path(project_name, view_layer.name)
            fo_node = tools.create_file_output_node(
                tree,
                name=view_layer.name,
                location=fo_location,
                base_path=base_path
            )

            use_denoise = view_layer.cycles.denoising_store_passes if scene.render.engine == "CYCLES" else False
            make_y_up = scene.qq_render_make_y_up

            _connect_passes(tree, rl_node, fo_node, use_denoise=use_denoise, make_y_up=make_y_up)

            node_rl_offset = tools.estimate_lowest_node_position(tree) - 50

        composite_render_nodes = _get_composite_render_layers(render_layers_nodes, scene)
        if composite_render_nodes:
            composite_location = (0, node_y_offset)
            _build_composite_chain(tree, scene, composite_render_nodes, composite_location)

        self.report({"INFO"}, "Generated nodes for {} view layers".format(len(view_layers)))
        logger.debug("Node generation completed for %d view layers", len(view_layers))
        return {"FINISHED"}


class QQ_RENDER_OT_update_output_paths(bpy.types.Operator):
    """Updates base paths for all File Output nodes in the compositor."""

    bl_idname = "qq_render.update_output_paths"
    bl_label = "Update Output Paths"
    bl_description = "Update base_path for all File Output nodes based on their names"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[str]:
        """Executes the output path update operator."""
        scene = context.scene

        if not scene.use_nodes or not scene.node_tree:
            self.report({"WARNING"}, "Compositor nodes not enabled")
            return {"CANCELLED"}

        tree = scene.node_tree
        updated_count = 0

        project_name = Path(bpy.data.filepath).stem if bpy.data.filepath else "untitled"

        for node in tree.nodes:
            if node.type == "OUTPUT_FILE":
                layer_name = node.name
                new_base_path = build_base_path(project_name, layer_name)
                node.base_path = new_base_path
                updated_count += 1
                logger.debug("Updated File Output node %s with base_path %s", layer_name, new_base_path)

        if updated_count == 0:
            self.report({"WARNING"}, "No File Output nodes found")
            return {"CANCELLED"}

        self.report({"INFO"}, "Updated {} File Output nodes".format(updated_count))
        logger.debug("Updated base_path for %d File Output nodes", updated_count)
        return {"FINISHED"}


_CLASSES = [
    QQ_RENDER_OT_generate_nodes,
    QQ_RENDER_OT_update_output_paths,
]


def register() -> None:
    """Registers operator classes."""
    for cls in _CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.qq_render_make_y_up = bpy.props.BoolProperty(
        name="Make Y Up",
        description="Invert Position and Normal passes to make Y axis point up",
        default=False
    )

    bpy.types.Scene.qq_render_clear_nodes = bpy.props.BoolProperty(
        name="Clear Nodes",
        description="Clear all existing compositor nodes before generating",
        default=True
    )

    logger.debug("Registered %d operator classes", len(_CLASSES))


def unregister() -> None:
    """Unregisters operator classes."""
    del bpy.types.Scene.qq_render_make_y_up
    del bpy.types.Scene.qq_render_clear_nodes

    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered operator classes")
