"""
View Layer List
    Description:
        UIList for displaying and managing view layers in the panel.
"""

import logging

import bpy

logger = logging.getLogger(__name__)


def get_sorted_view_layers(scene):
    """Returns view layers sorted by qq_render_sort_order."""
    return sorted(scene.view_layers, key=lambda vl: vl.qq_render_sort_order)


def get_view_layer_sort_position(scene, view_layer):
    """Returns the position of a view layer in sorted order."""
    sorted_layers = get_sorted_view_layers(scene)
    for idx, vl in enumerate(sorted_layers):
        if vl == view_layer:
            return idx
    return -1


def has_duplicate_sort_orders(scene):
    """Checks if any view layers have duplicate sort order values."""
    orders = [vl.qq_render_sort_order for vl in scene.view_layers]
    return len(orders) != len(set(orders))


class QQ_RENDER_UL_vl_list(bpy.types.UIList):
    """UIList for displaying view layers with render toggle."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        """Draws a single view layer item in the list."""
        scene = context.scene
        sorted_layers = get_sorted_view_layers(scene)
        current_pos = get_view_layer_sort_position(scene, item)
        is_first = current_pos == 0
        is_last = current_pos == len(sorted_layers) - 1

        row = layout.row(align=True)

        arrows = row.row(align=True)
        arrows.alignment = "LEFT"

        up_sub = arrows.row(align=True)
        up_sub.enabled = not is_first
        move_up = up_sub.operator("qq_render.vl_move_up", text="", icon="SORT_DESC")
        move_up.layer_name = item.name

        down_sub = arrows.row(align=True)
        down_sub.enabled = not is_last
        move_down = down_sub.operator("qq_render.vl_move_down", text="", icon="SORT_ASC")
        move_down.layer_name = item.name

        row.separator()

        row.prop(item, "name", text="", emboss=False, translate=False)

        if context.scene.render.engine == "CYCLES" and hasattr(item, "cycles"):
            row.prop(item.cycles, "denoising_store_passes", text="", icon="SHADERFX")

        row.prop(item, "qq_render_use_composite", text="", icon="NODE_COMPOSITING")
        row.prop(item, "use", text="", icon="RESTRICT_RENDER_OFF" if item.use else "RESTRICT_RENDER_ON")

    def filter_items(self, context, data, propname):
        """Sorts view layers by qq_render_sort_order."""
        view_layers = getattr(data, propname)

        flt_flags = [self.bitflag_filter_item] * len(view_layers)

        sorted_indices = sorted(range(len(view_layers)), key=lambda i: view_layers[i].qq_render_sort_order)

        flt_neworder = [0] * len(view_layers)
        for new_pos, old_idx in enumerate(sorted_indices):
            flt_neworder[old_idx] = new_pos

        return flt_flags, flt_neworder


classes = [
    QQ_RENDER_UL_vl_list,
]


def register():
    """Registers UIList classes and properties."""
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.ViewLayer.qq_render_use_composite = bpy.props.BoolProperty(
        name="Use Composite",
        description="Include this view layer in composite output",
        default=True
    )

    bpy.types.ViewLayer.qq_render_sort_order = bpy.props.IntProperty(
        name="Sort Order",
        description="Order of this view layer in composite chain",
        default=0
    )

    logger.debug("Registered %d UIList classes", len(classes))


def unregister():
    """Unregisters UIList classes and properties."""
    del bpy.types.ViewLayer.qq_render_use_composite
    del bpy.types.ViewLayer.qq_render_sort_order

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered UIList classes")
