"""
Blender Addon
    Description:
        Generates compositor render nodes based on view layers.
        Creates File Output nodes with proper pass connections.
"""

from __future__ import annotations

import logging

from . import operators
from . import ui
from .core.logger_config import setup_logging

bl_info = {
    "name": "qq Render",
    "author": "Tobias Petruj",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "Properties > View Layer",
    "description": "Generate render compositor nodes from view layers",
    "category": "Render",
}

logger = logging.getLogger(__name__)

_MODULES = [operators, ui]


def register() -> None:
    """Registers all addon classes and modules."""
    setup_logging()

    for module in _MODULES:
        module.register()

    logger.debug("qq Render addon registered with %d modules", len(_MODULES))


def unregister() -> None:
    """Unregisters all addon classes and modules."""
    for module in reversed(_MODULES):
        module.unregister()

    logger.debug("qq Render addon unregistered")


if __name__ == "__main__":
    register()
