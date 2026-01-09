"""
Export Panel
    Description:
        Standalone UI panel for export operations in the View Layer properties.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from bpy.types import Context

logger = logging.getLogger(__name__)


class QQ_RENDER_PT_export_panel(bpy.types.Panel):
    """Standalone export panel in View Layer properties."""

    bl_label = "qq Export"
    bl_idname = "QQ_RENDER_PT_export_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "view_layer"
    bl_order = 1

    def draw(self, context: Context) -> None:
        """Draws the export panel content."""
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.5
        row.operator("qq_render.export_camera", icon="OUTLINER_OB_CAMERA")


_CLASSES = [
    QQ_RENDER_PT_export_panel,
]


def register() -> None:
    """Registers export panel classes."""
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    logger.debug("Registered %d export panel classes", len(_CLASSES))


def unregister() -> None:
    """Unregisters export panel classes."""
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered export panel classes")
