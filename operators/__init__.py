"""
Operators Module
    Description:
        Registers all operator classes for the addon.
"""

import logging

from . import render
from . import vl_list

logger = logging.getLogger(__name__)

modules = [
    vl_list,
    render,
]


def register():
    """Registers all operator modules."""
    for module in modules:
        module.register()
    logger.debug("Registered %d operator modules", len(modules))


def unregister():
    """Unregisters all operator modules."""
    for module in reversed(modules):
        module.unregister()
    logger.debug("Unregistered operator modules")
