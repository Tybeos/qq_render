"""
View Layer Operators
    Description:
        Operators for managing view layers in the UIList.
"""

import logging

import bpy

logger = logging.getLogger(__name__)

view_layer_clipboard = {
    "passes": {},
    "cycles": {},
    "source": None,
}


def get_sorted_view_layers_for_index(scene):
    """Returns view layers sorted by qq_render_order for index operations."""
    return sorted(scene.view_layers, key=lambda vl: vl.get("qq_render_order", 0))


def get_active_view_layer_index(self):
    """Returns the index of the active view layer in the sorted list."""
    try:
        view_layer = bpy.context.window.view_layer
        sorted_layers = get_sorted_view_layers_for_index(self)
        for idx, vl in enumerate(sorted_layers):
            if vl == view_layer:
                return idx
    except (AttributeError, RuntimeError):
        pass
    return 0


def set_active_view_layer_index(self, value):
    """Sets the active view layer by index in the sorted list."""
    try:
        sorted_layers = get_sorted_view_layers_for_index(self)
        if 0 <= value < len(sorted_layers):
            bpy.context.window.view_layer = sorted_layers[value]
            logger.debug("Set active view layer to %s", sorted_layers[value].name)
    except (AttributeError, RuntimeError):
        pass


def get_next_order_value(scene):
    """Returns the next available order value for a new view layer."""
    max_order = 0
    for vl in scene.view_layers:
        order = vl.get("qq_render_order", 0)
        if order > max_order:
            max_order = order
    return max_order + 1


def initialize_order_values(scene):
    """Initializes order values for view layers that don't have them set."""
    needs_init = all(vl.get("qq_render_order", 0) == 0 for vl in scene.view_layers)
    if needs_init and len(scene.view_layers) > 1:
        for idx, vl in enumerate(scene.view_layers):
            vl["qq_render_order"] = idx
        logger.debug("Initialized order values for %d view layers", len(scene.view_layers))


class QQ_RENDER_OT_view_layer_add(bpy.types.Operator):
    """Adds a new view layer."""

    bl_idname = "qq_render.view_layer_add"
    bl_label = "Add View Layer"
    bl_description = "Add a new view layer"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        """Executes the add view layer operator."""
        scene = context.scene
        new_order = get_next_order_value(scene)
        new_layer = scene.view_layers.new(name="ViewLayer")
        new_layer["qq_render_order"] = new_order
        context.window.view_layer = new_layer
        self.report({"INFO"}, "Added view layer: {}".format(new_layer.name))
        logger.debug("Added new view layer %s with order %d", new_layer.name, new_order)
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


def get_view_layer_order(view_layer):
    """Returns the order value for a view layer."""
    return view_layer.get("qq_render_order", 0)


def set_view_layer_order(view_layer, value):
    """Sets the order value for a view layer."""
    view_layer["qq_render_order"] = value


def get_sorted_view_layers(scene):
    """Returns view layers sorted by qq_render_order."""
    return sorted(scene.view_layers, key=lambda vl: get_view_layer_order(vl))


class QQ_RENDER_OT_view_layer_move(bpy.types.Operator):
    """Swaps the order value of selected view layer with adjacent layer."""

    bl_idname = "qq_render.view_layer_move"
    bl_label = "Move View Layer"
    bl_description = "Swap the order of selected view layer with adjacent layer in the list"
    bl_options = {"REGISTER", "UNDO"}

    direction: bpy.props.EnumProperty(
        name="Direction",
        items=[
            ("UP", "Up", "Swap order with layer above"),
            ("DOWN", "Down", "Swap order with layer below"),
        ],
        default="UP"
    )

    @classmethod
    def poll(cls, context):
        """Checks if there are at least 2 view layers."""
        return len(context.scene.view_layers) > 1

    def execute(self, context):
        """Swaps order values of current layer with adjacent layer."""
        scene = context.scene
        active_vl = context.window.view_layer

        initialize_order_values(scene)
        sorted_layers = get_sorted_view_layers(scene)

        current_idx = None
        for i, vl in enumerate(sorted_layers):
            if vl == active_vl:
                current_idx = i
                break

        if current_idx is None:
            return {"CANCELLED"}

        if self.direction == "UP" and current_idx > 0:
            swap_idx = current_idx - 1
        elif self.direction == "DOWN" and current_idx < len(sorted_layers) - 1:
            swap_idx = current_idx + 1
        else:
            return {"CANCELLED"}

        swap_vl = sorted_layers[swap_idx]

        current_order = get_view_layer_order(active_vl)
        swap_order = get_view_layer_order(swap_vl)

        set_view_layer_order(active_vl, swap_order)
        set_view_layer_order(swap_vl, current_order)

        logger.debug("Swapped order of %s (%d) with %s (%d)", active_vl.name, swap_order, swap_vl.name, current_order)
        return {"FINISHED"}


class QQ_RENDER_OT_view_layer_copy(bpy.types.Operator):
    """Copies the active view layer settings to clipboard."""

    bl_idname = "qq_render.view_layer_copy"
    bl_label = "Copy View Layer Settings"
    bl_description = "Copy the active view layer settings"

    def execute(self, context):
        """Executes the copy view layer settings operator."""
        view_layer = context.window.view_layer

        view_layer_clipboard["passes"] = {}

        for attr in dir(view_layer):
            if attr.startswith("use_pass_"):
                view_layer_clipboard["passes"][attr] = getattr(view_layer, attr)

        if hasattr(view_layer, "cycles"):
            view_layer_clipboard["cycles"] = {
                "denoising_store_passes": view_layer.cycles.denoising_store_passes,
                "use_denoising": view_layer.cycles.use_denoising,
            }
        else:
            view_layer_clipboard["cycles"] = {}

        view_layer_clipboard["source"] = view_layer.name

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
        return bool(view_layer_clipboard["passes"])

    def execute(self, context):
        """Executes the paste view layer settings operator."""
        view_layer = context.window.view_layer

        for attr, value in view_layer_clipboard["passes"].items():
            if hasattr(view_layer, attr):
                setattr(view_layer, attr, value)

        if hasattr(view_layer, "cycles") and view_layer_clipboard["cycles"]:
            for attr, value in view_layer_clipboard["cycles"].items():
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
