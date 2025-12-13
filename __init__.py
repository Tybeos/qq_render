"""
Blender Addon
    Description:
        Generates compositor render nodes based on view layers.
        Creates File Output nodes with proper pass connections.
"""

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

from .core.logger_config import setup_logging

logger = logging.getLogger(__name__)

modules = []


def register():
    """Registers all addon classes and modules."""
    setup_logging()

    from . import operators
    from . import panels

    modules.extend([operators, panels])

    for module in modules:
        module.register()

    logger.debug("qq Render addon registered with %d modules", len(modules))


def unregister():
    """Unregisters all addon classes and modules."""
    for module in reversed(modules):
        module.unregister()

    modules.clear()
    logger.debug("qq Render addon unregistered")


if __name__ == "__main__":
    register()
