"""
Operators Tools
    Description:
        Utility functions for compositor node creation and manipulation.
"""

import logging
from pathlib import Path

import bpy

from ..core.constants import NODE_COLORS, FILE_OUTPUT_DEFAULTS, DENOISE_PASSES, SKIP_PASSES

logger = logging.getLogger(__name__)


def get_renderable_view_layers(scene):
    """Returns list of view layers that are enabled for rendering, sorted by qq_render_order."""
    renderable = []

    for view_layer in scene.view_layers:
        if hasattr(view_layer, "use"):
            use_render = view_layer.use
        else:
            use_render = getattr(view_layer, "use_for_render", True)

        if use_render:
            renderable.append(view_layer)

    renderable.sort(key=lambda vl: vl.qq_render_order)

    logger.debug("Found %d renderable view layers", len(renderable))
    return renderable


def get_output_base_path(scene, view_layer):
    """Generates the output path for a view layer."""
    if not bpy.data.filepath:
        base_path = "//render/{layer}/{layer}_###.exr".format(layer=view_layer.name)
        logger.debug("Using default path %s (file not saved)", base_path)
        return base_path

    blend_path = Path(bpy.data.filepath)
    file_name = blend_path.stem
    base_path = "//../render/{file}/{layer}/{layer}_###.exr".format(
        file=file_name,
        layer=view_layer.name
    )
    logger.debug("Generated output path %s for view layer %s", base_path, view_layer.name)
    return base_path


def setup_compositor(scene):
    """Enables compositor nodes"""
    scene.use_nodes = True
    logger.debug("Compositor enabled for scene %s", scene.name)
    return scene.node_tree


def clear_nodes(tree):
    """Removes all nodes from the compositor."""
    for node in tree.nodes:
        tree.nodes.remove(node)
    logger.debug("Cleared all compositor nodes")


def count_visible_sockets(sockets) -> int:
    return sum(1 for socket in sockets if socket.enabled)


def estimate_node_height(node):
    """Estimates node height based on visible sockets."""
    socket_height = 22
    header_height = 40
    minimum_height = 80

    if node.hide:
        return header_height

    socket_count = max(count_visible_sockets(node.inputs), count_visible_sockets(node.outputs))

    return socket_count*socket_height + minimum_height


def estimate_lowest_node_position(tree):
    """Estimates lowest node position based on visible sockets."""
    if not tree.nodes:
        return 0

    min_bottom = min(node.location.y -  estimate_node_height(node) for node in tree.nodes)
    logger.debug("Found lowest node bottom at Y=%d", min_bottom)
    return min_bottom


def get_lowest_node_position(tree):
    """Returns the Y position below the lowest node in the tree."""
    if not tree.nodes:
        return 0

    min_bottom = min(node.location.y - node.dimensions.y for node in tree.nodes)
    logger.debug("Found lowest node bottom at Y=%d", min_bottom)
    return min_bottom


def create_render_layers_node(tree, view_layer, location):
    """Creates a Render Layers node for the specified view layer."""
    node = tree.nodes.new(type="CompositorNodeRLayers")
    node.layer = view_layer.name
    node.location = location
    node.use_custom_color = True
    node.color = NODE_COLORS["render_layers"]
    logger.debug("Created Render Layers node for view layer %s at %s", view_layer.name, location)
    return node


def create_file_output_node(tree, name, location, base_path):
    """Creates a File Output node with EXR multilayer format."""
    node = tree.nodes.new(type="CompositorNodeOutputFile")
    node.name = name
    node.label = name
    node.location = location
    node.use_custom_color = True
    node.color = NODE_COLORS["file_output"]
    node.width = 300

    node.format.file_format = FILE_OUTPUT_DEFAULTS["format"]
    node.format.color_depth = FILE_OUTPUT_DEFAULTS["color_depth"]
    node.format.exr_codec = FILE_OUTPUT_DEFAULTS["codec"]
    node.base_path = base_path

    node.inputs.clear()
    logger.debug("Created File Output node %s at %s", name, location)
    return node


def connect_enabled_passes(tree, render_layers_node, file_output_node):
    """Connects all enabled passes from Render Layers to File Output."""
    for output in render_layers_node.outputs:
        if not output.enabled:
            continue

        if output.name in SKIP_PASSES:
            continue

        file_output_node.file_slots.new(name=output.name)

        for input_socket in file_output_node.inputs:
            if input_socket.name == output.name:
                tree.links.new(output, input_socket)
                break

    logger.debug("Connected passes from %s to %s", render_layers_node.name, file_output_node.name)


def create_denoise_node(tree, name, location):
    """Creates a Denoise node."""
    node = tree.nodes.new(type="CompositorNodeDenoise")
    node.name = name
    node.label = name
    node.location = location
    node.hide = True
    node.use_custom_color = True
    node.color = NODE_COLORS["denoise"]
    logger.debug("Created Denoise node %s at %s", name, location)
    return node


def connect_denoised_passes(tree, render_layers_node, file_output_node, denoise_x_offset=300):
    """Connects passes with denoise nodes for applicable passes."""
    denoise_y_offset = 0
    rl_x = render_layers_node.location[0]
    rl_y = render_layers_node.location[1]

    has_denoising_data = (
        render_layers_node.outputs.get("Denoising Normal") and
        render_layers_node.outputs.get("Denoising Normal").enabled and
        render_layers_node.outputs.get("Denoising Albedo") and
        render_layers_node.outputs.get("Denoising Albedo").enabled
    )

    for output in render_layers_node.outputs:
        if not output.enabled:
            continue

        if output.name in SKIP_PASSES:
            continue

        file_output_node.file_slots.new(name=output.name)
        target_input = None

        for input_socket in file_output_node.inputs:
            if input_socket.name == output.name:
                target_input = input_socket
                break

        if not target_input:
            continue

        should_denoise = output.name in DENOISE_PASSES and has_denoising_data

        if should_denoise:
            denoise_node = create_denoise_node(
                tree,
                name="Denoise_{}".format(output.name),
                location=(rl_x + denoise_x_offset, rl_y + denoise_y_offset)
            )

            tree.links.new(output, denoise_node.inputs[0])
            tree.links.new(render_layers_node.outputs["Denoising Normal"], denoise_node.inputs[1])
            tree.links.new(render_layers_node.outputs["Denoising Albedo"], denoise_node.inputs[2])
            tree.links.new(denoise_node.outputs[0], target_input)

            denoise_y_offset -= 30
        else:
            tree.links.new(output, target_input)

    logger.debug("Connected denoised passes from %s to %s", render_layers_node.name, file_output_node.name)
