"""
Render Operators
    Description:
        Operators for rendering animations in Blender.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from bpy.types import Context

logger = logging.getLogger(__name__)


class QQ_RENDER_OT_render_animation(bpy.types.Operator):
    """Renders the active scene as an animation."""

    bl_idname = "qq_render.render_animation"
    bl_label = "QQ Render Animation"
    bl_description = "Render active scene"
    bl_options = {"REGISTER"}

    def execute(self, context: Context) -> set[str]:
        """Executes the render animation operator."""
        bpy.ops.render.render(animation=True, use_viewport=True)
        logger.debug("Started animation render")
        return {"FINISHED"}


_CLASSES = [
    QQ_RENDER_OT_render_animation,
]


def register() -> None:
    """Registers operator classes."""
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    logger.debug("Registered %d operator classes", len(_CLASSES))


def unregister() -> None:
    """Unregisters operator classes."""
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered operator classes")
