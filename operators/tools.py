"""
QQ Render
Operators Tools
    Description:
        Utility functions for compositor node creation and manipulation.
"""

import logging
from pathlib import Path

import bpy

from ..core.constants import NODE_COLORS, FILE_OUTPUT_DEFAULTS

logger = logging.getLogger(__name__)


def get_renderable_view_layers(scene):
    """Returns list of view layers that are enabled for rendering."""
    renderable = []

    for view_layer in scene.view_layers:
        if hasattr(view_layer, "use"):
            use_render = view_layer.use
        else:
            use_render = getattr(view_layer, "use_for_render", True)

        if use_render:
            renderable.append(view_layer)

    logger.debug("Found %d renderable view layers", len(renderable))
    return renderable


def get_output_base_path(scene, view_layer):
    """Generates the output path for a view layer."""
    if not bpy.data.filepath:
        base_path = "//render/{layer}/{layer}_###.exr".format(layer=view_layer.name)
        logger.debug("Using default path %s (file not saved)", base_path)
        return base_path

    blend_path = Path(bpy.data.filepath)
    file_name = blend_path.stem
    base_path = "//../render/{file}/{layer}/{layer}_###.exr".format(
        file=file_name,
        layer=view_layer.name
    )
    logger.debug("Generated output path %s for view layer %s", base_path, view_layer.name)
    return base_path


def setup_compositor(scene):
    """Enables compositor nodes and returns the node tree."""
    scene.use_nodes = True
    logger.debug("Compositor enabled for scene %s", scene.name)
    return scene.node_tree


def clear_nodes(tree):
    """Removes all nodes from the compositor."""
    for node in tree.nodes:
        tree.nodes.remove(node)
    logger.debug("Cleared all compositor nodes")


def get_lowest_node_position(tree):
    """Returns the Y position below the lowest node in the tree."""
    if not tree.nodes:
        return 0

    min_y = min(node.location.y for node in tree.nodes)
    logger.debug("Found lowest node position at Y=%d", min_y)
    return min_y - 400


def create_render_layers_node(tree, view_layer, location):
    """Creates a Render Layers node for the specified view layer."""
    node = tree.nodes.new(type="CompositorNodeRLayers")
    node.layer = view_layer.name
    node.location = location
    node.use_custom_color = True
    node.color = NODE_COLORS["render_layers"]
    logger.debug("Created Render Layers node for view layer %s at %s", view_layer.name, location)
    return node


def create_file_output_node(tree, name, location, base_path):
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


def connect_enabled_passes(tree, render_layers_node, file_output_node):
    """Connects all enabled passes from Render Layers to File Output."""
    connected_count = 0

    for output in render_layers_node.outputs:
        if not output.enabled:
            continue

        if output.name in ("Image", "Alpha"):
            continue

        file_output_node.file_slots.new(name=output.name)

        for input_socket in file_output_node.inputs:
            if input_socket.name == output.name:
                tree.links.new(output, input_socket)
                connected_count += 1
                break

    logger.debug("Connected %d passes from %s to %s", connected_count, render_layers_node.name, file_output_node.name)
    return connected_count
