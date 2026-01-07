"""
Core Tools
    Description:
        Utility functions for compositor node creation, manipulation,
        and view layer management.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import bpy

from .constants import NODE_COLORS, FILE_OUTPUT_DEFAULTS

if TYPE_CHECKING:
    from bpy.types import (
        BackgroundImage,
        CompositorNode,
        CompositorNodeOutputFile,
        CompositorNodeRLayers,
        Node,
        NodeSocket,
        NodeTree,
        Scene,
        ViewLayer,
    )

logger = logging.getLogger(__name__)


def get_sorted_view_layers(scene: Scene) -> list[ViewLayer]:
    """Returns view layers sorted by qq_render_sort_order."""
    sorted_layers = sorted(scene.view_layers, key=lambda vl: vl.qq_render_sort_order)
    logger.debug("Got %d sorted view layers", len(sorted_layers))
    return sorted_layers


def get_view_layer_sort_position(scene: Scene, view_layer: ViewLayer) -> int:
    """Returns the position of a view layer in sorted order."""
    sorted_layers = get_sorted_view_layers(scene)
    for idx, vl in enumerate(sorted_layers):
        if vl == view_layer:
            logger.debug("View layer %s is at position %d", view_layer.name, idx)
            return idx
    logger.debug("View layer %s not found in sorted list", view_layer.name)
    return -1


def ensure_unique_sort_orders(scene: Scene) -> None:
    """Ensures all view layers have unique sort order values."""
    orders = [vl.qq_render_sort_order for vl in scene.view_layers]
    if len(orders) != len(set(orders)):
        for idx, vl in enumerate(scene.view_layers):
            vl.qq_render_sort_order = idx
        logger.debug("Initialized sort orders for %d view layers", len(scene.view_layers))


def swap_sort_orders(layer_a: ViewLayer, layer_b: ViewLayer) -> None:
    """Swaps sort order values between two view layers."""
    order_a = layer_a.qq_render_sort_order
    order_b = layer_b.qq_render_sort_order
    layer_a.qq_render_sort_order = order_b
    layer_b.qq_render_sort_order = order_a
    logger.debug("Swapped sort orders between %s and %s", layer_a.name, layer_b.name)


def get_renderable_view_layers(scene: Scene) -> list[ViewLayer]:
    """Returns list of view layers that are enabled for rendering, sorted by sort order."""
    renderable = []

    for view_layer in scene.view_layers:
        if hasattr(view_layer, "use"):
            use_render = view_layer.use
        else:
            use_render = getattr(view_layer, "use_for_render", True)

        if use_render:
            renderable.append(view_layer)

    renderable.sort(key=lambda vl: vl.qq_render_sort_order)

    logger.debug("Found %d renderable view layers sorted by order", len(renderable))
    return renderable


def setup_compositor(scene: Scene) -> NodeTree:
    """Enables compositor nodes."""
    scene.use_nodes = True
    logger.debug("Compositor enabled for scene %s", scene.name)
    return scene.node_tree


def clear_nodes(tree: NodeTree) -> None:
    """Removes all nodes from the compositor."""
    for node in tree.nodes:
        tree.nodes.remove(node)
    logger.debug("Cleared all compositor nodes")


def count_visible_sockets(sockets: list[NodeSocket]) -> int:
    """Counts enabled sockets in a socket collection."""
    return sum(1 for socket in sockets if socket.enabled)


def estimate_node_height(node: Node) -> int:
    """Estimates node height based on visible sockets."""
    socket_height = 22
    header_height = 40
    minimum_height = 80

    if node.hide:
        return header_height

    socket_count = max(count_visible_sockets(node.inputs), count_visible_sockets(node.outputs))

    return socket_count * socket_height + minimum_height


def estimate_lowest_node_position(tree: NodeTree) -> float:
    """Estimates lowest node position based on visible sockets."""
    if not tree.nodes:
        return 0

    min_bottom = min(node.location.y - estimate_node_height(node) for node in tree.nodes)
    logger.debug("Found lowest node bottom at Y=%d", min_bottom)
    return min_bottom


def get_lowest_node_position(tree: NodeTree) -> float:
    """Returns the Y position below the lowest node in the tree."""
    if not tree.nodes:
        return 0

    min_bottom = min(node.location.y - node.dimensions.y for node in tree.nodes)
    logger.debug("Found lowest node bottom at Y=%d", min_bottom)
    return min_bottom


def create_render_layers_node(
    tree: NodeTree,
    view_layer: ViewLayer,
    location: tuple[float, float]) -> CompositorNodeRLayers:
    """Creates a Render Layers node for the specified view layer."""
    node = tree.nodes.new(type="CompositorNodeRLayers")
    node.layer = view_layer.name
    node.location = location
    node.use_custom_color = True
    node.color = NODE_COLORS["render_layers"]
    logger.debug("Created Render Layers node for view layer %s at %s", view_layer.name, location)
    return node


def create_file_output_node(
    tree: NodeTree,
    name: str,
    location: tuple[float, float],
    base_path: str) -> CompositorNodeOutputFile:
    """Creates a File Output node with EXR multilayer format."""
    node = tree.nodes.new(type="CompositorNodeOutputFile")
    node.name = name
    node.label = name
    node.location = location
    node.use_custom_color = True
    node.color = NODE_COLORS["file_output"]
    node.width = 300

    node.format.file_format = FILE_OUTPUT_DEFAULTS["format"]
    node.format.color_depth = FILE_OUTPUT_DEFAULTS["color_depth"]
    node.format.exr_codec = FILE_OUTPUT_DEFAULTS["codec"]
    node.base_path = base_path

    node.inputs.clear()
    logger.debug("Created File Output node %s at %s", name, location)
    return node


def create_denoise_node(
    tree: NodeTree,
    name: str,
    location: tuple[float, float]) -> CompositorNode:
    """Creates a Denoise node."""
    node = tree.nodes.new(type="CompositorNodeDenoise")
    node.name = name
    node.label = name
    node.location = location
    node.hide = True
    node.use_custom_color = True
    node.color = NODE_COLORS["denoise"]
    logger.debug("Created Denoise node %s at %s", name, location)
    return node


def create_image_node(
    tree: NodeTree,
    bg_image: BackgroundImage,
    location: tuple[float, float]) -> CompositorNode:
    """Creates an Image node from a background image object."""
    node = tree.nodes.new(type="CompositorNodeImage")
    node.image = bg_image.image
    node.location = location
    node.use_custom_color = True
    node.color = NODE_COLORS.get("image", (0.3, 0.3, 0.3))

    bg_user = bg_image.image_user

    node.frame_start = bg_user.frame_start
    node.frame_offset = bg_user.frame_offset
    node.frame_duration = bg_user.frame_duration
    node.use_auto_refresh = bg_user.use_auto_refresh
    node.use_cyclic = bg_user.use_cyclic

    logger.debug("Created Image node from background %s at %s", bg_image.image.name, location)
    return node


def create_alpha_over_node(
    tree: NodeTree,
    location: tuple[float, float],
    name: str = "Alpha_Over") -> CompositorNode:
    """Creates a single Alpha Over node."""
    node = tree.nodes.new(type="CompositorNodeAlphaOver")
    node.name = name
    node.label = name
    node.location = location
    node.use_custom_color = True
    node.color = NODE_COLORS.get("alpha_over", (0.4, 0.4, 0.4))
    logger.debug("Created Alpha Over node %s at %s", name, location)
    return node


def create_composite_node(
    tree: NodeTree,
    location: tuple[float, float]) -> CompositorNode:
    """Creates a Composite output node."""
    node = tree.nodes.new(type="CompositorNodeComposite")
    node.location = location
    node.use_custom_color = True
    node.color = NODE_COLORS.get("composite", (0.3, 0.5, 0.3))
    logger.debug("Created Composite node at %s", location)
    return node


def create_viewer_node(
    tree: NodeTree,
    location: tuple[float, float]) -> CompositorNode:
    """Creates a Viewer output node."""
    node = tree.nodes.new(type="CompositorNodeViewer")
    node.location = location
    node.use_custom_color = True
    node.color = NODE_COLORS.get("viewer", (0.55, 0.33, 0.17))
    logger.debug("Created Viewer node at %s", location)
    return node


def create_vector_invert_group(
    tree: NodeTree,
    location: tuple[float, float],
    name: str) -> CompositorNode:
    """Creates a Z-up to Y-up conversion node group with Y inversion."""
    group = bpy.data.node_groups.new(name=name, type="CompositorNodeTree")

    group_input = group.nodes.new(type="NodeGroupInput")
    group_input.location = (-400, 0)
    group_input.name = "Group Input"

    group_output = group.nodes.new(type="NodeGroupOutput")
    group_output.location = (400, 0)
    group_output.name = "Group Output"

    separate_xyz = group.nodes.new(type="CompositorNodeSeparateXYZ")
    separate_xyz.location = (-200, 0)
    separate_xyz.name = "Separate XYZ"

    multiply = group.nodes.new(type="CompositorNodeMath")
    multiply.location = (0, 100)
    multiply.operation = "MULTIPLY"
    multiply.inputs[1].default_value = -1.0
    multiply.name = "Multiply"
    multiply.use_clamp = False

    combine_xyz = group.nodes.new(type="CompositorNodeCombineXYZ")
    combine_xyz.location = (200, 0)
    combine_xyz.name = "Combine XYZ"

    group.interface.new_socket(name="Vector", in_out="INPUT", socket_type="NodeSocketVector")
    group.interface.new_socket(name="Vector", in_out="OUTPUT", socket_type="NodeSocketVector")

    group.links.new(group_input.outputs[0], separate_xyz.inputs[0])
    group.links.new(separate_xyz.outputs[0], combine_xyz.inputs[0])
    group.links.new(separate_xyz.outputs[1], multiply.inputs[0])
    group.links.new(multiply.outputs[0], combine_xyz.inputs[2])
    group.links.new(separate_xyz.outputs[2], combine_xyz.inputs[1])
    group.links.new(combine_xyz.outputs[0], group_output.inputs[0])

    node = tree.nodes.new(type="CompositorNodeGroup")
    node.node_tree = group
    node.name = name
    node.label = name
    node.location = location
    node.hide = True
    logger.debug("Created Vector Invert group node %s at %s", name, location)
    return node
