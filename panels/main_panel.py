"""
Main Panel
    Description:
        Main UI panel for qq Render addon in the View Layer properties.
"""

import logging

import bpy

logger = logging.getLogger(__name__)


class QQ_RENDER_PT_main_panel(bpy.types.Panel):
    """Main panel for qq Render in View Layer properties."""

    bl_label = "qq Render"
    bl_idname = "QQ_RENDER_PT_main_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "view_layer"
    bl_order = 0

    def draw(self, context):
        """Draws the main panel content."""
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.template_list(
            "QQ_RENDER_UL_vl_list",
            "",
            scene,
            "view_layers",
            scene,
            "qq_render_active_view_layer_index",
            rows=5
        )

        col = row.column(align=True)
        col.operator("qq_render.vl_list_add", icon="ADD", text="")
        col.operator("qq_render.vl_list_remove", icon="REMOVE", text="")
        col.separator()
        col.operator("qq_render.vl_list_copy", icon="COPYDOWN", text="")
        col.operator("qq_render.vl_list_paste", icon="PASTEDOWN", text="")

        layout.separator()

        col = layout.column(align=True)
        col.alignment = "CENTER"
        col.prop(scene, "qq_render_make_y_up")
        col.prop(scene, "qq_render_clear_nodes")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("qq_render.generate_nodes", icon="NODE")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("qq_render.update_output_paths", icon="FILE_REFRESH")

        logger.debug("Drew main panel with %d view layers", len(scene.view_layers))


classes = [
    QQ_RENDER_PT_main_panel,
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
