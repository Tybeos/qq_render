"""
QQ Render
Main Panel
    Description:
        Main UI panel for QQ Render addon in the View Layer properties.
"""

import logging

import bpy

logger = logging.getLogger(__name__)


class QQ_RENDER_PT_main_panel(bpy.types.Panel):
    """Main panel for QQ Render in View Layer properties."""

    bl_label = "QQ Render"
    bl_idname = "QQ_RENDER_PT_main_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "view_layer"
    bl_order = 0

    def draw(self, context):
        """Draws the main panel content."""
        layout = self.layout
        logger.debug("Drawing main panel")


class QQ_RENDER_PT_output_panel(bpy.types.Panel):
    """Output generation subpanel."""

    bl_label = "Output"
    bl_idname = "QQ_RENDER_PT_output_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "view_layer"
    bl_parent_id = "QQ_RENDER_PT_main_panel"
    bl_order = 1

    def draw(self, context):
        """Draws the output panel with generation controls."""
        layout = self.layout
        scene = context.scene

        view_layer_count = len(scene.view_layers)
        renderable_count = sum(
            1 for vl in scene.view_layers
            if getattr(vl, "use", None) or getattr(vl, "use_for_render", True)
        )

        row = layout.row()
        row.label(text="View Layers: {} ({} renderable)".format(view_layer_count, renderable_count))

        layout.separator()

        row = layout.row()
        row.prop(scene, "qq_render_clear_nodes")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("qq_render.generate_nodes", icon="NODE")

        logger.debug("Drew output panel with %d view layers", view_layer_count)


class QQ_RENDER_PT_info_panel(bpy.types.Panel):
    """Information and status subpanel."""

    bl_label = "Info"
    bl_idname = "QQ_RENDER_PT_info_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "view_layer"
    bl_parent_id = "QQ_RENDER_PT_main_panel"
    bl_order = 2
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        """Draws the info panel with current settings."""
        layout = self.layout
        scene = context.scene

        col = layout.column(align=True)
        col.label(text="Engine: {}".format(scene.render.engine))
        col.label(text="File: {}".format(bpy.path.basename(bpy.data.filepath) or "Not Saved"))

        logger.debug("Drew info panel")


classes = [
    QQ_RENDER_PT_main_panel,
    QQ_RENDER_PT_output_panel,
    QQ_RENDER_PT_info_panel,
]


def register():
    """Registers panel classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    logger.debug("Registered %d panel classes", len(classes))


def unregister():
    """Unregisters panel classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered panel classes")
