"""
Operators Module
    Description:
        Registers all operator classes for the addon.
"""

from __future__ import annotations

import logging

from . import render_nodes
from . import vl_list_ops
from . import export_camera
from . import render

logger = logging.getLogger(__name__)

_MODULES = [
    vl_list_ops,
    render_nodes,
    export_camera,
    render,
]


def register() -> None:
    """Registers all operator modules."""
    for module in _MODULES:
        module.register()
    logger.debug("Registered %d operator modules", len(_MODULES))


def unregister() -> None:
    """Unregisters all operator modules."""
    for module in reversed(_MODULES):
        module.unregister()
    logger.debug("Unregistered operator modules")
