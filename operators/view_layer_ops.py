"""
View Layer Operators
    Description:
        Operators for managing view layers in the UIList.
"""

import logging

import bpy

logger = logging.getLogger(__name__)


def switch_view_layer(self, context):
    """Callback to switch the active view layer when selection changes."""
    scene = context.scene
    idx = scene.qq_render_active_view_layer_index
    view_layers = scene.view_layers

    if 0 <= idx < len(view_layers):
        context.window.view_layer = view_layers[idx]
        logger.debug("Switched to view layer %s", view_layers[idx].name)


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
        scene.qq_render_active_view_layer_index = len(scene.view_layers) - 1
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
        idx = scene.qq_render_active_view_layer_index
        view_layers = scene.view_layers

        if idx < 0 or idx >= len(view_layers):
            self.report({"WARNING"}, "Invalid view layer selection")
            return {"CANCELLED"}

        layer_name = view_layers[idx].name
        view_layers.remove(view_layers[idx])

        if scene.qq_render_active_view_layer_index >= len(view_layers):
            scene.qq_render_active_view_layer_index = len(view_layers) - 1

        if scene.qq_render_active_view_layer_index >= 0:
            context.window.view_layer = view_layers[scene.qq_render_active_view_layer_index]

        self.report({"INFO"}, "Removed view layer: {}".format(layer_name))
        logger.debug("Removed view layer %s", layer_name)
        return {"FINISHED"}


class QQ_RENDER_OT_view_layer_move(bpy.types.Operator):
    """Moves the selected view layer up or down in the list."""

    bl_idname = "qq_render.view_layer_move"
    bl_label = "Move View Layer"
    bl_description = "Move the selected view layer up or down"
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
        idx = scene.qq_render_active_view_layer_index
        view_layers = scene.view_layers
        num_layers = len(view_layers)

        if self.direction == "UP" and idx > 0:
            scene.qq_render_active_view_layer_index = idx - 1
            logger.debug("Moved selection up to index %d", idx - 1)
        elif self.direction == "DOWN" and idx < num_layers - 1:
            scene.qq_render_active_view_layer_index = idx + 1
            logger.debug("Moved selection down to index %d", idx + 1)

        return {"FINISHED"}


class QQ_RENDER_OT_sync_active_view_layer(bpy.types.Operator):
    """Synchronizes the list selection with the active view layer."""

    bl_idname = "qq_render.sync_active_view_layer"
    bl_label = "Sync Active View Layer"
    bl_description = "Sync list selection with the current active view layer"
    bl_options = {"REGISTER"}

    def execute(self, context):
        """Executes the sync operator."""
        scene = context.scene
        active_vl = context.view_layer

        for idx, vl in enumerate(scene.view_layers):
            if vl == active_vl:
                scene.qq_render_active_view_layer_index = idx
                logger.debug("Synced to view layer %s at index %d", vl.name, idx)
                break

        return {"FINISHED"}


classes = [
    QQ_RENDER_OT_view_layer_add,
    QQ_RENDER_OT_view_layer_remove,
    QQ_RENDER_OT_view_layer_move,
    QQ_RENDER_OT_sync_active_view_layer,
]


def register():
    """Registers view layer operator classes and properties."""
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.qq_render_active_view_layer_index = bpy.props.IntProperty(
        name="Active View Layer Index",
        description="Index of the active view layer in the list",
        default=0,
        update=switch_view_layer
    )

    logger.debug("Registered %d view layer operator classes", len(classes))


def unregister():
    """Unregisters view layer operator classes and properties."""
    del bpy.types.Scene.qq_render_active_view_layer_index

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    logger.debug("Unregistered view layer operator classes")
