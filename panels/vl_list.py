"""
View Layer List
    Description:
        UIList for displaying and managing view layers in the panel.
"""

import logging

import bpy

logger = logging.getLogger(__name__)


class QQ_RENDER_UL_vl_list(bpy.types.UIList):
    """UIList for displaying view layers with render toggle."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        """Draws a single view layer item in the list."""
        row = layout.row(align=True)
        row.prop(item, "name", text="", emboss=False, translate=False)

        if context.scene.render.engine == "CYCLES" and hasattr(item, "cycles"):
            row.prop(item.cycles, "denoising_store_passes", text="", icon="SHADERFX")

        row.prop(item, "qq_render_use_composite", text="", icon="NODE_COMPOSITING")
        row.prop(item, "use", text="", icon="RESTRICT_RENDER_OFF" if item.use else "RESTRICT_RENDER_ON")


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

    logger.debug("Registered %d UIList classes", len(classes))


def unregister():
    """Unregisters UIList classes and properties."""
    del bpy.types.ViewLayer.qq_render_use_composite

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered UIList classes")
