"""
View Layer List
    Description:
        UIList for displaying and managing view layers in the panel.
"""

import logging

import bpy

logger = logging.getLogger(__name__)


class QQ_RENDER_UL_view_layers(bpy.types.UIList):
    """UIList for displaying view layers with render toggle."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        """Draws a single view layer item in the list."""
        row = layout.row(align=True)
        row.prop(item, "name", text="", emboss=False, translate=False)
        row.prop(item, "use", text="", icon="RESTRICT_RENDER_OFF" if item.use else "RESTRICT_RENDER_ON")

    def filter_items(self, context, data, propname):
        """Sorts view layers by qq_render_order property."""
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        filtered = []
        ordered = helper_funcs.sort_items_helper(
            [(idx, item) for idx, item in enumerate(items)],
            lambda x: x[1].qq_render_order,
            False
        )

        return filtered, ordered


classes = [
    QQ_RENDER_UL_view_layers,
]


def register():
    """Registers UIList classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    logger.debug("Registered %d UIList classes", len(classes))


def unregister():
    """Unregisters UIList classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered UIList classes")
