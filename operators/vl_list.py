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


def get_max_sort_order(scene):
    """Returns the highest sort order value among all view layers."""
    if not scene.view_layers:
        return -1
    return max(vl.qq_render_sort_order for vl in scene.view_layers)


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

        next_order = get_max_sort_order(scene) + 1

        bpy.ops.scene.view_layer_add(type="COPY")

        new_layer = context.window.view_layer
        new_layer.qq_render_sort_order = next_order

        self.report({"INFO"}, "Added view layer: {} (copied from {})".format(new_layer.name, source_layer.name))
        logger.debug("Added new view layer %s with sort_order %d copied from %s", new_layer.name, next_order, source_layer.name)
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


view_layer_clipboard = {
    "passes": {},
    "cycles": {},
    "eevee": {},
    "source": None,
}


def ensure_unique_sort_orders(scene):
    """Ensures all view layers have unique sort order values."""
    orders = [vl.qq_render_sort_order for vl in scene.view_layers]
    if len(orders) != len(set(orders)):
        for idx, vl in enumerate(scene.view_layers):
            vl.qq_render_sort_order = idx
        logger.debug("Initialized sort orders for %d view layers", len(scene.view_layers))


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


def swap_sort_orders(layer_a, layer_b):
    """Swaps sort order values between two view layers."""
    order_a = layer_a.qq_render_sort_order
    order_b = layer_b.qq_render_sort_order
    layer_a.qq_render_sort_order = order_b
    layer_b.qq_render_sort_order = order_a


class QQ_RENDER_OT_vl_move_up(bpy.types.Operator):
    """Moves the view layer up in the sort order."""

    bl_idname = "qq_render.vl_move_up"
    bl_label = "Move View Layer Up"
    bl_description = "Move this view layer up in the composite order"
    bl_options = {"REGISTER", "UNDO"}

    layer_name: bpy.props.StringProperty(name="Layer Name")

    @classmethod
    def poll(cls, context):
        """Checks if the operator can be executed."""
        return len(context.scene.view_layers) > 1

    def execute(self, context):
        """Executes the move up operator."""
        scene = context.scene
        ensure_unique_sort_orders(scene)

        view_layer = scene.view_layers.get(self.layer_name)

        if not view_layer:
            self.report({"WARNING"}, "View layer not found")
            return {"CANCELLED"}

        sorted_layers = get_sorted_view_layers(scene)
        current_pos = get_view_layer_sort_position(scene, view_layer)

        if current_pos <= 0:
            return {"CANCELLED"}

        prev_layer = sorted_layers[current_pos - 1]
        swap_sort_orders(view_layer, prev_layer)

        for area in context.screen.areas:
            area.tag_redraw()

        logger.debug("Moved view layer %s up from position %d", self.layer_name, current_pos)
        return {"FINISHED"}


class QQ_RENDER_OT_vl_move_down(bpy.types.Operator):
    """Moves the view layer down in the sort order."""

    bl_idname = "qq_render.vl_move_down"
    bl_label = "Move View Layer Down"
    bl_description = "Move this view layer down in the composite order"
    bl_options = {"REGISTER", "UNDO"}

    layer_name: bpy.props.StringProperty(name="Layer Name")

    @classmethod
    def poll(cls, context):
        """Checks if the operator can be executed."""
        return len(context.scene.view_layers) > 1

    def execute(self, context):
        """Executes the move down operator."""
        scene = context.scene
        ensure_unique_sort_orders(scene)

        view_layer = scene.view_layers.get(self.layer_name)

        if not view_layer:
            self.report({"WARNING"}, "View layer not found")
            return {"CANCELLED"}

        sorted_layers = get_sorted_view_layers(scene)
        current_pos = get_view_layer_sort_position(scene, view_layer)

        if current_pos < 0 or current_pos >= len(sorted_layers) - 1:
            return {"CANCELLED"}

        next_layer = sorted_layers[current_pos + 1]
        swap_sort_orders(view_layer, next_layer)

        for area in context.screen.areas:
            area.tag_redraw()

        logger.debug("Moved view layer %s down from position %d", self.layer_name, current_pos)
        return {"FINISHED"}


class QQ_RENDER_OT_vl_list_copy(bpy.types.Operator):
    """Copies the active view layer settings to clipboard."""

    bl_idname = "qq_render.vl_list_copy"
    bl_label = "Copy View Layer Settings"
    bl_description = "Copy the active view layer settings"

    def execute(self, context):
        """Executes the copy view layer settings operator."""
        view_layer = context.window.view_layer

        view_layer_clipboard["passes"] = {}
        for attr in dir(view_layer):
            if attr.startswith("use_pass_") or attr in ["use_solid", "use_ao", "material_override", "samples", "pass_alpha_threshold"]:
                try:
                    view_layer_clipboard["passes"][attr] = getattr(view_layer, attr)
                except (AttributeError, TypeError):
                    pass

        if hasattr(view_layer, "cycles"):
            view_layer_clipboard["cycles"] = {}
            for attr in dir(view_layer.cycles):
                if not attr.startswith("_") and attr != "rna_type":
                    try:
                        value = getattr(view_layer.cycles, attr)
                        if not callable(value):
                            view_layer_clipboard["cycles"][attr] = value
                    except (AttributeError, TypeError):
                        pass

        if hasattr(view_layer, "eevee"):
            view_layer_clipboard["eevee"] = {}
            for attr in dir(view_layer.eevee):
                if not attr.startswith("_") and attr != "rna_type":
                    try:
                        value = getattr(view_layer.eevee, attr)
                        if not callable(value):
                            view_layer_clipboard["eevee"][attr] = value
                    except (AttributeError, TypeError):
                        pass

        view_layer_clipboard["source"] = view_layer.name

        self.report({"INFO"}, "Copied settings from: {}".format(view_layer.name))
        logger.debug("Copied view layer settings from %s", view_layer.name)
        return {"FINISHED"}


class QQ_RENDER_OT_vl_list_paste(bpy.types.Operator):
    """Pastes the clipboard settings to the active view layer."""

    bl_idname = "qq_render.vl_list_paste"
    bl_label = "Paste View Layer Settings"
    bl_description = "Paste the clipboard settings to the active view layer"

    @classmethod
    def poll(cls, context):
        """Checks if clipboard has data."""
        return view_layer_clipboard["source"] is not None

    def execute(self, context):
        """Executes the paste view layer settings operator."""
        view_layer = context.window.view_layer

        for attr, value in view_layer_clipboard["passes"].items():
            if hasattr(view_layer, attr):
                try:
                    setattr(view_layer, attr, value)
                except (AttributeError, TypeError):
                    pass

        if hasattr(view_layer, "cycles") and view_layer_clipboard["cycles"]:
            for attr, value in view_layer_clipboard["cycles"].items():
                if hasattr(view_layer.cycles, attr):
                    try:
                        setattr(view_layer.cycles, attr, value)
                    except (AttributeError, TypeError):
                        pass

        if hasattr(view_layer, "eevee") and view_layer_clipboard["eevee"]:
            for attr, value in view_layer_clipboard["eevee"].items():
                if hasattr(view_layer.eevee, attr):
                    try:
                        setattr(view_layer.eevee, attr, value)
                    except (AttributeError, TypeError):
                        pass

        self.report({"INFO"}, "Pasted settings to: {}".format(view_layer.name))
        logger.debug("Pasted view layer settings to %s", view_layer.name)
        return {"FINISHED"}


classes = [
    QQ_RENDER_OT_vl_list_add,
    QQ_RENDER_OT_vl_list_remove,
    QQ_RENDER_OT_vl_move_up,
    QQ_RENDER_OT_vl_move_down,
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
