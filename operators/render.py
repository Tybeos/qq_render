"""
Render Nodes Operators
    Description:
        Operators for generating compositor render nodes
        based on view layers and their enabled passes.
"""

import logging
from pathlib import Path

import bpy

from ..core import tools
from ..core.relative_path import build_base_path

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

        if scene.qq_render_clear_nodes:
            tools.clear_nodes(tree)

        output_x_position = 600
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

            if use_denoise:
                tools.connect_denoised_passes(tree, rl_node, fo_node)
            else:
                tools.connect_enabled_passes(tree, rl_node, fo_node)

            node_rl_offset = tools.estimate_lowest_node_position(tree) - 50

        composite_render_nodes = tools.get_composite_render_layers(render_layers_nodes, scene)
        if composite_render_nodes:
            composite_location = (0, node_y_offset)
            tools.build_composite_chain(tree, scene, composite_render_nodes, composite_location)

        self.report({"INFO"}, "Generated nodes for {} view layers".format(len(view_layers)))
        logger.debug("Node generation completed for %d view layers", len(view_layers))
        return {"FINISHED"}


class QQ_RENDER_OT_update_output_paths(bpy.types.Operator):
    """Updates base paths for all File Output nodes in the compositor."""

    bl_idname = "qq_render.update_output_paths"
    bl_label = "Update Output Paths"
    bl_description = "Update base_path for all File Output nodes based on their names"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
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


classes = [
    QQ_RENDER_OT_generate_nodes,
    QQ_RENDER_OT_update_output_paths,
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
