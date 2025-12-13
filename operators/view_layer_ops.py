"""
View Layer Operators
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


class QQ_RENDER_OT_view_layer_add(bpy.types.Operator):
    """Adds a new view layer."""

    bl_idname = "qq_render.view_layer_add"
    bl_label = "Add View Layer"
    bl_description = "Add a new view layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Executes the add view layer operator."""
        scene = context.scene
        new_layer = scene.view_layers.new(name="ViewLayer")
        context.window.view_layer = new_layer
        self.report({"INFO"}, "Added view layer: {}".format(new_layer.name))
        logger.debug("Added new view layer %s", new_layer.name)
        return {"FINISHED"}


class QQ_RENDER_OT_view_layer_remove(bpy.types.Operator):
    """Removes the selected view layer."""

    bl_idname = "qq_render.view_layer_remove"
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


class QQ_RENDER_OT_view_layer_move(bpy.types.Operator):
    """Moves the selected view layer up or down in the order."""

    bl_idname = "qq_render.view_layer_move"
    bl_label = "Move View Layer"
    bl_description = "Move the selected view layer up or down in the order"
    bl_options = {"REGISTER", "UNDO"}

    direction: bpy.props.EnumProperty(
        name="Direction",
        items=[
            ("UP", "Up", "Move view layer up"),
            ("DOWN", "Down", "Move view layer down"),
        ],
        default="UP"
    )

    @classmethod
    def poll(cls, context):
        """Checks if the scene has view layers."""
        return len(context.scene.view_layers) > 1

    def execute(self, context):
        """Executes the move view layer operator."""
        scene = context.scene
        view_layers = scene.view_layers
        active_vl = context.window.view_layer
        num_layers = len(view_layers)

        idx = None
        for i, vl in enumerate(view_layers):
            if vl == active_vl:
                idx = i
                break

        if idx is None:
            return {"CANCELLED"}

        if self.direction == "UP" and idx > 0:
            view_layers.move(idx, idx - 1)
            logger.debug("Moved view layer %s from %d to %d", active_vl.name, idx, idx - 1)
        elif self.direction == "DOWN" and idx < num_layers - 1:
            view_layers.move(idx, idx + 1)
            logger.debug("Moved view layer %s from %d to %d", active_vl.name, idx, idx + 1)

        return {"FINISHED"}


class QQ_RENDER_OT_view_layer_copy(bpy.types.Operator):
    """Copies the active view layer settings to clipboard."""

    bl_idname = "qq_render.view_layer_copy"
    bl_label = "Copy View Layer Settings"
    bl_description = "Copy the active view layer settings"

    def execute(self, context):
        """Executes the copy view layer settings operator."""
        view_layer = context.window.view_layer
        scene = context.scene

        scene.qq_render_clipboard_passes = {}

        for attr in dir(view_layer):
            if attr.startswith("use_pass_"):
                scene.qq_render_clipboard_passes[attr] = getattr(view_layer, attr)

        if hasattr(view_layer, "cycles"):
            scene.qq_render_clipboard_cycles = {
                "denoising_store_passes": view_layer.cycles.denoising_store_passes,
                "use_denoising": view_layer.cycles.use_denoising,
            }
        else:
            scene.qq_render_clipboard_cycles = {}

        scene.qq_render_clipboard_source = view_layer.name

        self.report({"INFO"}, "Copied settings from: {}".format(view_layer.name))
        logger.debug("Copied view layer settings from %s", view_layer.name)
        return {"FINISHED"}


class QQ_RENDER_OT_view_layer_paste(bpy.types.Operator):
    """Pastes the clipboard settings to the active view layer."""

    bl_idname = "qq_render.view_layer_paste"
    bl_label = "Paste View Layer Settings"
    bl_description = "Paste the clipboard settings to the active view layer"

    @classmethod
    def poll(cls, context):
        """Checks if clipboard has data."""
        scene = context.scene
        return hasattr(scene, "qq_render_clipboard_passes") and scene.qq_render_clipboard_passes

    def execute(self, context):
        """Executes the paste view layer settings operator."""
        view_layer = context.window.view_layer
        scene = context.scene

        for attr, value in scene.qq_render_clipboard_passes.items():
            if hasattr(view_layer, attr):
                setattr(view_layer, attr, value)

        if hasattr(view_layer, "cycles") and scene.qq_render_clipboard_cycles:
            for attr, value in scene.qq_render_clipboard_cycles.items():
                if hasattr(view_layer.cycles, attr):
                    setattr(view_layer.cycles, attr, value)

        self.report({"INFO"}, "Pasted settings to: {}".format(view_layer.name))
        logger.debug("Pasted view layer settings to %s", view_layer.name)
        return {"FINISHED"}


classes = [
    QQ_RENDER_OT_view_layer_add,
    QQ_RENDER_OT_view_layer_remove,
    QQ_RENDER_OT_view_layer_move,
    QQ_RENDER_OT_view_layer_copy,
    QQ_RENDER_OT_view_layer_paste,
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
