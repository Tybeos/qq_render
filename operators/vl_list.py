"""
View Layer List Operators
    Description:
        Operators for managing view layers in the UIList.
"""

import logging

import bpy

logger = logging.getLogger(__name__)

def get_active_view_layer_index(self):
    """Returns the index of the active view layer in the scene."""
    try:
        view_layer = bpy.context.window.view_layer
        for idx, vl in enumerate(self.view_layers):
            if vl == view_layer:
                return idx
    except (AttributeError, RuntimeError):
        pass
    return 0


def set_active_view_layer_index(self, value):
    """Sets the active view layer by index."""
    try:
        if 0 <= value < len(self.view_layers):
            bpy.context.window.view_layer = self.view_layers[value]
            logger.debug("Set active view layer to %s", self.view_layers[value].name)
    except (AttributeError, RuntimeError):
        pass


class QQ_RENDER_OT_vl_list_add(bpy.types.Operator):
    """Adds a new view layer with settings copied from the active layer."""

    bl_idname = "qq_render.vl_list_add"
    bl_label = "Add View Layer"
    bl_description = "Add a new view layer with settings copied from the active layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Executes the add view layer operator."""
        scene = context.scene
        source_layer = context.window.view_layer

        bpy.ops.scene.view_layer_add(type="COPY")

        new_layer = context.window.view_layer
        self.report({"INFO"}, "Added view layer: {} (copied from {})".format(new_layer.name, source_layer.name))
        logger.debug("Added new view layer %s with settings copied from %s", new_layer.name, source_layer.name)
        return {"FINISHED"}


class QQ_RENDER_OT_vl_list_remove(bpy.types.Operator):
    """Removes the selected view layer."""

    bl_idname = "qq_render.vl_list_remove"
    bl_label = "Remove View Layer"
    bl_description = "Remove the selected view layer"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Checks if removal is possible (at least 2 view layers)."""
        return len(context.scene.view_layers) > 1

    def execute(self, context):
        """Executes the remove view layer operator."""
        scene = context.scene
        view_layers = scene.view_layers
        active_vl = context.window.view_layer

        idx = None
        for i, vl in enumerate(view_layers):
            if vl == active_vl:
                idx = i
                break

        if idx is None:
            self.report({"WARNING"}, "Invalid view layer selection")
            return {"CANCELLED"}

        layer_name = view_layers[idx].name
        view_layers.remove(view_layers[idx])

        new_idx = min(idx, len(view_layers) - 1)
        if new_idx >= 0:
            context.window.view_layer = view_layers[new_idx]

        self.report({"INFO"}, "Removed view layer: {}".format(layer_name))
        logger.debug("Removed view layer %s", layer_name)
        return {"FINISHED"}


class QQ_RENDER_OT_vl_list_copy(bpy.types.Operator):
    """Copies the active view layer settings to clipboard."""

    bl_idname = "qq_render.vl_list_copy"
    bl_label = "Copy View Layer Settings"
    bl_description = "Copy the active view layer settings"

    def execute(self, context):
        """Executes the copy view layer settings operator."""
        bpy.ops.scene.view_layer_copy_settings()
        self.report({"INFO"}, "Copied settings from: {}".format(context.window.view_layer.name))
        logger.debug("Copied view layer settings from %s", context.window.view_layer.name)
        return {"FINISHED"}


class QQ_RENDER_OT_vl_list_paste(bpy.types.Operator):
    """Pastes the clipboard settings to the active view layer."""

    bl_idname = "qq_render.vl_list_paste"
    bl_label = "Paste View Layer Settings"
    bl_description = "Paste the clipboard settings to the active view layer"

    @classmethod
    def poll(cls, context):
        """Checks if clipboard has data."""
        return bpy.ops.scene.view_layer_paste_settings.poll()

    def execute(self, context):
        """Executes the paste view layer settings operator."""
        bpy.ops.scene.view_layer_paste_settings()
        self.report({"INFO"}, "Pasted settings to: {}".format(context.window.view_layer.name))
        logger.debug("Pasted view layer settings to %s", context.window.view_layer.name)
        return {"FINISHED"}


classes = [
    QQ_RENDER_OT_vl_list_add,
    QQ_RENDER_OT_vl_list_remove,
    QQ_RENDER_OT_vl_list_copy,
    QQ_RENDER_OT_vl_list_paste,
]


def register():
    """Registers view layer operator classes and properties."""
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.qq_render_active_view_layer_index = bpy.props.IntProperty(
        name="Active View Layer Index",
        description="Index of the active view layer in the list",
        get=get_active_view_layer_index,
        set=set_active_view_layer_index
    )

    logger.debug("Registered %d view layer operator classes", len(classes))


def unregister():
    """Unregisters view layer operator classes and properties."""
    del bpy.types.Scene.qq_render_active_view_layer_index

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    logger.debug("Unregistered view layer operator classes")
