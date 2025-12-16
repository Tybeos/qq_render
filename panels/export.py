"""
Export Panel
    Description:
        Collapsible UI panel for export operations under the Update Path button.
"""

import logging

import bpy

logger = logging.getLogger(__name__)


class QQ_RENDER_PT_export_panel(bpy.types.Panel):
    """Collapsible export sub-panel nested inside main qq Render panel."""

    bl_label = "Export"
    bl_idname = "QQ_RENDER_PT_export_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "view_layer"
    bl_parent_id = "QQ_RENDER_PT_main_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        """Draws the export panel content."""
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.scale_y = 1.2
        row.operator("qq_render.export_camera", icon="OUTLINER_OB_CAMERA")

        logger.debug("Drew export panel")


classes = [
    QQ_RENDER_PT_export_panel,
]


def register():
    """Registers export panel classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    logger.debug("Registered %d export panel classes", len(classes))


def unregister():
    """Unregisters export panel classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered export panel classes")
