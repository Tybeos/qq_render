"""
Generate Axis Operators
    Description:
        Creates axis empties from selected objects with copied animation.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from bpy.types import Context, Object

logger = logging.getLogger(__name__)

_SUPPORTED_TYPES = {"MESH", "CURVE", "SURFACE", "ARMATURE", "LATTICE"}


def _get_all_children(obj: Object) -> list[Object]:
    """Returns all children of an object recursively."""
    children = []
    for child in obj.children:
        children.append(child)
        children.extend(_get_all_children(child))
    return children


def _create_axis_for_object(context: Context, obj: Object) -> Object:
    """Creates an axis empty parented to the given object with copied animation."""
    empty = bpy.data.objects.new("%s.axis" % obj.name, None)
    empty.empty_display_type = "PLAIN_AXES"

    context.collection.objects.link(empty)

    empty.parent = obj
    empty.matrix_parent_inverse = obj.matrix_world.inverted()

    if obj.animation_data and obj.animation_data.action:
        empty.animation_data_create()
        empty.animation_data.action = obj.animation_data.action.copy()
        empty.animation_data.action.name = "%s.axis" % obj.animation_data.action.name

    logger.debug("Created axis empty %s parented to %s", empty.name, obj.name)
    return empty


class QQ_RENDER_OT_generate_axis(bpy.types.Operator):
    """Creates axis empties from selected objects with copied animation."""

    bl_idname = "qq_render.generate_axis"
    bl_label = "Generate Axis"
    bl_description = "Create axis empties from selected objects with copied animation"
    bl_options = {"REGISTER", "UNDO"}

    include_children: bpy.props.BoolProperty(
        name="Include Children",
        description="Also create axis empties for all child objects",
        default=False
    )

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Checks if there are selected supported objects."""
        return any(obj.type in _SUPPORTED_TYPES for obj in context.selected_objects)

    def execute(self, context: Context) -> set[str]:
        """Creates axis empties for all selected supported objects."""
        objects_to_process = set()

        for obj in context.selected_objects:
            if obj.type in _SUPPORTED_TYPES:
                objects_to_process.add(obj)

            if self.include_children:
                for child in _get_all_children(obj):
                    if child.type in _SUPPORTED_TYPES:
                        objects_to_process.add(child)

        if not objects_to_process:
            self.report({"WARNING"}, "No supported objects selected")
            return {"CANCELLED"}

        created_count = 0
        for obj in objects_to_process:
            _create_axis_for_object(context, obj)
            created_count += 1

        self.report({"INFO"}, "Created %d axis empties" % created_count)
        logger.debug("Generated %d axis empties from selected objects", created_count)
        return {"FINISHED"}


_CLASSES = [
    QQ_RENDER_OT_generate_axis,
]


def register() -> None:
    """Registers generate axis operator classes."""
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    logger.debug("Registered %d generate axis operator classes", len(_CLASSES))


def unregister() -> None:
    """Unregisters generate axis operator classes."""
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered generate axis operator classes")
