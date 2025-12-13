"""
View Layer Operators
    Description:
        Operators for managing view layers in the UIList.
"""

import logging

import bpy

logger = logging.getLogger(__name__)


def get_sorted_view_layers(scene):
    """Returns view layers sorted by their qq_render_order property."""
    layers = list(scene.view_layers)
    return sorted(layers, key=lambda vl: vl.qq_render_order)


def normalize_view_layer_order(scene):
    """Resets order values to sequential integers starting from 0."""
    sorted_layers = get_sorted_view_layers(scene)
    for idx, layer in enumerate(sorted_layers):
        layer.qq_render_order = idx
    logger.debug("Normalized view layer order for %d layers", len(sorted_layers))


def switch_view_layer(self, context):
    """Callback to switch the active view layer when selection changes."""
    scene = context.scene
    idx = scene.qq_render_active_view_layer_index
    sorted_layers = get_sorted_view_layers(scene)

    if 0 <= idx < len(sorted_layers):
        context.window.view_layer = sorted_layers[idx]
        logger.debug("Switched to view layer %s", sorted_layers[idx].name)


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
        new_layer.qq_render_order = len(scene.view_layers) - 1
        normalize_view_layer_order(scene)
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
        sorted_layers = get_sorted_view_layers(scene)

        if idx < 0 or idx >= len(sorted_layers):
            self.report({"WARNING"}, "Invalid view layer selection")
            return {"CANCELLED"}

        layer_to_remove = sorted_layers[idx]
        layer_name = layer_to_remove.name
        scene.view_layers.remove(layer_to_remove)

        normalize_view_layer_order(scene)

        if scene.qq_render_active_view_layer_index >= len(scene.view_layers):
            scene.qq_render_active_view_layer_index = len(scene.view_layers) - 1

        sorted_layers = get_sorted_view_layers(scene)
        if scene.qq_render_active_view_layer_index >= 0 and sorted_layers:
            context.window.view_layer = sorted_layers[scene.qq_render_active_view_layer_index]

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
        sorted_layers = get_sorted_view_layers(scene)
        num_layers = len(sorted_layers)

        if self.direction == "UP" and idx > 0:
            current_layer = sorted_layers[idx]
            swap_layer = sorted_layers[idx - 1]
            current_layer.qq_render_order, swap_layer.qq_render_order = swap_layer.qq_render_order, current_layer.qq_render_order
            scene.qq_render_active_view_layer_index = idx - 1
            logger.debug("Moved view layer %s up", current_layer.name)
        elif self.direction == "DOWN" and idx < num_layers - 1:
            current_layer = sorted_layers[idx]
            swap_layer = sorted_layers[idx + 1]
            current_layer.qq_render_order, swap_layer.qq_render_order = swap_layer.qq_render_order, current_layer.qq_render_order
            scene.qq_render_active_view_layer_index = idx + 1
            logger.debug("Moved view layer %s down", current_layer.name)

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
        sorted_layers = get_sorted_view_layers(scene)

        for idx, vl in enumerate(sorted_layers):
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

    bpy.types.ViewLayer.qq_render_order = bpy.props.IntProperty(
        name="Render Order",
        description="Order of view layer for rendering",
        default=0
    )

    logger.debug("Registered %d view layer operator classes", len(classes))


def unregister():
    """Unregisters view layer operator classes and properties."""
    del bpy.types.ViewLayer.qq_render_order
    del bpy.types.Scene.qq_render_active_view_layer_index

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    logger.debug("Unregistered view layer operator classes")
