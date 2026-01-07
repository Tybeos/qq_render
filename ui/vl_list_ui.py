"""
View Layer List UI
    Description:
        UIList for displaying and managing view layers in the panel.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import bpy

from ..core.tools import get_sorted_view_layers, get_view_layer_sort_position

if TYPE_CHECKING:
    from bpy.types import Context, Scene, UILayout, ViewLayer

logger = logging.getLogger(__name__)


class QQ_RENDER_UL_vl_list(bpy.types.UIList):
    """UIList for displaying view layers with render toggle."""

    def draw_item(
        self,
        context: Context,
        layout: UILayout,
        data: Scene,
        item: ViewLayer,
        icon: str,
        active_data: Scene,
        active_propname: str,
        index: int) -> None:
        """Draws a single view layer item in the list."""
        scene = context.scene
        sorted_layers = get_sorted_view_layers(scene)

        try:
            current_pos = get_view_layer_sort_position(scene, item)
        except ValueError:
            current_pos = 0

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

    def filter_items(
        self,
        context: Context,
        data: Scene,
        propname: str) -> tuple[list[int], list[int]]:
        """Sorts view layers by qq_render_sort_order."""
        view_layers = getattr(data, propname)

        flt_flags = [self.bitflag_filter_item] * len(view_layers)

        sorted_indices = sorted(range(len(view_layers)), key=lambda i: view_layers[i].qq_render_sort_order)

        flt_neworder = [0] * len(view_layers)
        for new_pos, old_idx in enumerate(sorted_indices):
            flt_neworder[old_idx] = new_pos

        logger.debug("Filtered and sorted %d view layers", len(view_layers))
        return flt_flags, flt_neworder


_CLASSES = [
    QQ_RENDER_UL_vl_list,
]


def register() -> None:
    """Registers UIList classes and properties."""
    for cls in _CLASSES:
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

    logger.debug("Registered %d UIList classes", len(_CLASSES))


def unregister() -> None:
    """Unregisters UIList classes and properties."""
    del bpy.types.ViewLayer.qq_render_use_composite
    del bpy.types.ViewLayer.qq_render_sort_order

    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered UIList classes")
