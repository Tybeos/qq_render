"""
Panels Module
    Description:
        Registers all UI panel classes for the addon.
"""

import logging

from . import view_layer_list
from . import main_panel

logger = logging.getLogger(__name__)

modules = [
    view_layer_list,
    main_panel,
]


def register():
    """Registers all panel modules."""
    for module in modules:
        module.register()
    logger.debug("Registered %d panel modules", len(modules))


def unregister():
    """Unregisters all panel modules."""
    for module in reversed(modules):
        module.unregister()
    logger.debug("Unregistered panel modules")
