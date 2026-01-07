"""
Blender Addon
    Description:
        Generates compositor render nodes based on view layers.
        Creates File Output nodes with proper pass connections.
"""

from __future__ import annotations

bl_info = {
    "name": "qq Render",
    "author": "Tobias Petruj",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "Properties > View Layer",
    "description": "Generate render compositor nodes from view layers",
    "category": "Render",
}

import logging
from types import ModuleType

from .core.logger_config import setup_logging

logger = logging.getLogger(__name__)

_modules: list[ModuleType] = []


def register() -> None:
    """Registers all addon classes and modules."""
    setup_logging()

    from . import operators
    from . import ui

    _modules.extend([operators, ui])

    for module in _modules:
        module.register()

    logger.debug("qq Render addon registered with %d modules", len(_modules))


def unregister() -> None:
    """Unregisters all addon classes and modules."""
    for module in reversed(_modules):
        module.unregister()

    _modules.clear()
    logger.debug("qq Render addon unregistered")


if __name__ == "__main__":
    register()
