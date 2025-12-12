"""
QQ Render
Render Nodes Operators
    Description:
        Operators for generating compositor render nodes
        based on view layers and their enabled passes.
"""

import logging

import bpy

from . import tools

logger = logging.getLogger(__name__)


class QQ_RENDER_OT_generate_nodes(bpy.types.Operator):
    """Generates compositor nodes for all renderable view layers."""

    bl_idname = "qq_render.generate_nodes"
    bl_label = "Generate Render Nodes"
    bl_description = "Generate File Output nodes for each view layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Executes the node generation operator."""
        scene = context.scene
        view_layers = tools.get_renderable_view_layers(scene)

        if not view_layers:
            self.report({"WARNING"}, "No renderable view layers found")
            return {"CANCELLED"}

        tree = tools.setup_compositor(scene)

        clear_existing = scene.qq_render_clear_nodes

        if clear_existing:
            tools.clear_nodes(tree)
            node_y_offset = 0
        else:
            node_y_offset = tools.get_lowest_node_position(tree)

        output_x_position = 600

        for view_layer in view_layers:
            rl_location = (0, node_y_offset)
            fo_location = (output_x_position, node_y_offset)

            rl_node = tools.create_render_layers_node(tree, view_layer, rl_location)

            base_path = tools.get_output_base_path(scene, view_layer)
            fo_node = tools.create_file_output_node(
                tree,
                name="{}_Output".format(view_layer.name),
                location=fo_location,
                base_path=base_path
            )

            use_denoise = view_layer.cycles.denoising_store_passes if scene.render.engine == "CYCLES" else False

            if use_denoise:
                tools.connect_denoised_passes(tree, rl_node, fo_node)
            else:
                tools.connect_enabled_passes(tree, rl_node, fo_node)

            node_y_offset -= 400

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

    bpy.types.Scene.qq_render_clear_nodes = bpy.props.BoolProperty(
        name="Clear Nodes",
        description="Clear all existing compositor nodes before generating",
        default=True
    )

    logger.debug("Registered %d operator classes", len(classes))


def unregister():
    """Unregisters operator classes."""
    del bpy.types.Scene.qq_render_clear_nodes

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered operator classes")
