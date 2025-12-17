"""
Export Panel
    Description:
        Standalone UI panel for export operations in the View Layer properties.
"""

import logging

import bpy

logger = logging.getLogger(__name__)


class QQ_RENDER_PT_export_panel(bpy.types.Panel):
    """Standalone export panel in View Layer properties."""

    bl_label = "qq Export"
    bl_idname = "QQ_RENDER_PT_export_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "view_layer"
    bl_order = 1

    def draw(self, context):
        """Draws the export panel content."""
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.scale_y = 1.5
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
