"""
Render Menu
    Description:
        Adds custom render items to Blender's Render menu.
"""

from __future__ import annotations

import logging

import bpy

logger = logging.getLogger(__name__)


def _draw_render_menu(self, context):
    """Draws qq render item in the Render menu."""
    self.layout.operator("qq_render.check_and_render", icon="RENDER_ANIMATION")


def register() -> None:
    """Registers render menu items."""
    bpy.types.TOPBAR_MT_render.prepend(_draw_render_menu)
    logger.debug("Registered render menu items")


def unregister() -> None:
    """Unregisters render menu items."""
    bpy.types.TOPBAR_MT_render.remove(_draw_render_menu)
    logger.debug("Unregistered render menu items")
