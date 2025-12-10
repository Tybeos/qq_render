"""
QQ Render
Render Nodes Operators
    Description:
        Operators for generating compositor render nodes
        based on view layers and their enabled passes.
"""

import logging
from pathlib import Path

import bpy

from ..core.constants import (
    NODE_COLORS,
    FILE_OUTPUT_DEFAULTS,
    RenderEngine,
)

logger = logging.getLogger(__name__)


class NodeTreeBuilder:
    """Builds compositor node trees for render output."""

    def __init__(self, scene):
        """Initializes builder with the target scene."""
        self.scene = scene
        self.tree = None
        self.links = None

    def setup_compositor(self):
        """Enables compositor nodes and gets the node tree."""
        self.scene.use_nodes = True
        self.tree = self.scene.node_tree
        self.links = self.tree.links
        logger.debug("Compositor enabled for scene %s", self.scene.name)

    def clear_nodes(self):
        """Removes all nodes from the compositor."""
        for node in self.tree.nodes:
            self.tree.nodes.remove(node)
        logger.debug("Cleared all compositor nodes")

    def create_render_layers_node(self, view_layer, location):
        """Creates a Render Layers node for the specified view layer."""
        node = self.tree.nodes.new(type="CompositorNodeRLayers")
        node.layer = view_layer.name
        node.location = location
        node.use_custom_color = True
        node.color = NODE_COLORS["render_layers"]
        logger.debug("Created Render Layers node for view layer %s at %s", view_layer.name, location)
        return node

    def create_file_output_node(self, name, location, base_path):
        """Creates a File Output node with EXR multilayer format."""
        node = self.tree.nodes.new(type="CompositorNodeOutputFile")
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

    def create_composite_node(self, location):
        """Creates a Composite output node."""
        node = self.tree.nodes.new(type="CompositorNodeComposite")
        node.location = location
        logger.debug("Created Composite node at %s", location)
        return node

    def create_viewer_node(self, location):
        """Creates a Viewer node."""
        node = self.tree.nodes.new(type="CompositorNodeViewer")
        node.location = location
        logger.debug("Created Viewer node at %s", location)
        return node

    def connect_enabled_passes(self, render_layers_node, file_output_node):
        """Connects all enabled passes from Render Layers to File Output."""
        connected_count = 0

        for output in render_layers_node.outputs:
            if not output.enabled:
                continue

            if output.name in ("Image", "Alpha"):
                continue

            file_output_node.file_slots.new(name=output.name)

            for input_socket in file_output_node.inputs:
                if input_socket.name == output.name:
                    self.links.new(output, input_socket)
                    connected_count += 1
                    break

        logger.debug("Connected %d passes from %s to %s", connected_count, render_layers_node.name, file_output_node.name)
        return connected_count

    def connect_image_output(self, render_layers_node, composite_node, viewer_node):
        """Connects the Image output to Composite and Viewer nodes."""
        image_output = render_layers_node.outputs.get("Image")
        if not image_output:
            logger.warning("No Image output found on render layers node")
            return

        self.links.new(image_output, composite_node.inputs["Image"])
        self.links.new(image_output, viewer_node.inputs["Image"])
        logger.debug("Connected Image output to Composite and Viewer")


def get_output_base_path(scene, view_layer):
    """Generates the output path for a view layer."""
    blend_path = Path(bpy.data.filepath)

    if not bpy.data.filepath:
        base_path = "//render/{layer}/{layer}_###.exr".format(layer=view_layer.name)
        logger.debug("Using default path %s (file not saved)", base_path)
        return base_path

    file_name = blend_path.stem
    base_path = "//../render/{file}/{layer}/{layer}_###.exr".format(
        file=file_name,
        layer=view_layer.name
    )
    logger.debug("Generated output path %s for view layer %s", base_path, view_layer.name)
    return base_path


def get_renderable_view_layers(scene):
    """Returns list of view layers that are enabled for rendering."""
    renderable = []

    for view_layer in scene.view_layers:
        use_render = getattr(view_layer, "use", None) or getattr(view_layer, "use_for_render", True)
        if use_render:
            renderable.append(view_layer)

    logger.debug("Found %d renderable view layers", len(renderable))
    return renderable


class QQ_RENDER_OT_generate_nodes(bpy.types.Operator):
    """Generates compositor nodes for all renderable view layers."""

    bl_idname = "qq_render.generate_nodes"
    bl_label = "Generate Render Nodes"
    bl_description = "Generate File Output nodes for each view layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Executes the node generation operator."""
        scene = context.scene
        view_layers = get_renderable_view_layers(scene)

        if not view_layers:
            self.report({"WARNING"}, "No renderable view layers found")
            return {"CANCELLED"}

        builder = NodeTreeBuilder(scene)
        builder.setup_compositor()
        builder.clear_nodes()

        node_y_offset = 0
        output_x_position = 600

        composite_node = builder.create_composite_node((output_x_position + 400, 300))
        viewer_node = builder.create_viewer_node((output_x_position + 400, 100))

        first_rl_node = None

        for i, view_layer in enumerate(view_layers):
            rl_location = (0, node_y_offset)
            fo_location = (output_x_position, node_y_offset)

            rl_node = builder.create_render_layers_node(view_layer, rl_location)
            if first_rl_node is None:
                first_rl_node = rl_node

            base_path = get_output_base_path(scene, view_layer)
            fo_node = builder.create_file_output_node(
                name="{}_Output".format(view_layer.name),
                location=fo_location,
                base_path=base_path
            )

            builder.connect_enabled_passes(rl_node, fo_node)

            node_y_offset -= 400

        if first_rl_node:
            builder.connect_image_output(first_rl_node, composite_node, viewer_node)

        self.report({"INFO"}, "Generated nodes for {} view layers".format(len(view_layers)))
        logger.debug("Node generation completed for %d view layers", len(view_layers))
        return {"FINISHED"}


classes = [
    QQ_RENDER_OT_generate_nodes,
]


def register():
    """Registers operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    logger.debug("Registered %d operator classes", len(classes))


def unregister():
    """Unregisters operator classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered operator classes")
