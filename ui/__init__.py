"""
UI Module
    Description:
        Registers all UI panel classes for the addon.
"""

from __future__ import annotations

import logging

from . import confirm_dialog
from . import vl_list_ui
from . import render_panel
from . import export_panel

logger = logging.getLogger(__name__)

_MODULES = [
    confirm_dialog,
    vl_list_ui,
    render_panel,
    export_panel,
]


def register() -> None:
    """Registers all UI modules."""
    for module in _MODULES:
        module.register()
    logger.debug("Registered %d UI modules", len(_MODULES))


def unregister() -> None:
    """Unregisters all UI modules."""
    for module in reversed(_MODULES):
        module.unregister()
    logger.debug("Unregistered UI modules")
