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
        """Sorts view layers by qq_render_order custom property."""
        view_layers = getattr(data, propname)
        flt_flags = [self.bitflag_filter_item] * len(view_layers)

        order_values = []
        for vl in view_layers:
            order_values.append(vl.get("qq_render_order", 0))

        flt_neworder = sorted(range(len(view_layers)), key=lambda i: order_values[i])

        logger.debug("Filtered view layers with order %s", flt_neworder)
        return flt_flags, flt_neworder


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
