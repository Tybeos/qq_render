"""
Confirm Dialog UI
    Description:
        Universal confirmation dialog for overwrite warnings with support
        for single or multiple file paths and callback operator execution.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import bpy
from bpy.props import CollectionProperty, PointerProperty, StringProperty
from bpy.types import PropertyGroup

if TYPE_CHECKING:
    from bpy.types import Context, Event, UILayout

logger = logging.getLogger(__name__)


class QQ_ConfirmFilePath(PropertyGroup):
    """Property group for storing a single file path."""

    path: StringProperty(
        name="Path",
        description="File path to display in confirmation dialog",
        default=""
    )


class QQ_ConfirmDialogProps(PropertyGroup):
    """Property group for confirm dialog settings."""

    file_paths: CollectionProperty(
        type=QQ_ConfirmFilePath,
        name="File Paths",
        description="List of file paths that will be overwritten"
    )

    callback_operator: StringProperty(
        name="Callback Operator",
        description="bl_idname of operator to call on confirmation",
        default=""
    )

    title: StringProperty(
        name="Title",
        description="Dialog title message",
        default="File already exists"
    )


class QQ_RENDER_OT_overwrite_confirm(bpy.types.Operator):
    """Universal confirmation dialog for file overwrite warnings."""

    bl_idname = "qq_render.overwrite_confirm"
    bl_label = "Overwrite Warning"
    bl_description = "Confirm overwriting existing files"
    bl_options = {"INTERNAL"}

    def invoke(self, context: Context, event: Event) -> set[str]:
        """Shows the confirmation dialog centered in Blender window."""
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context: Context) -> None:
        """Draws the confirmation dialog content."""
        layout: UILayout = self.layout
        props = context.window_manager.qq_confirm_dialog

        layout.label(text=props.title)
        layout.separator()

        file_count = len(props.file_paths)
        if file_count == 1:
            layout.label(text=Path(props.file_paths[0].path).name)
        elif file_count > 1:
            layout.label(text="%d files will be overwritten:" % file_count)
            box = layout.box()
            for item in props.file_paths:
                box.label(text=Path(item.path).name)

        layout.separator()
        layout.label(text="Do you want to overwrite?")

    def execute(self, context: Context) -> set[str]:
        """Executes the callback operator on confirmation."""
        props = context.window_manager.qq_confirm_dialog
        op_idname = props.callback_operator

        if not op_idname:
            logger.error("No callback operator specified")
            return {"CANCELLED"}

        try:
            category, name = op_idname.split(".")
            op_func = getattr(getattr(bpy.ops, category), name)
            result = op_func()
            logger.debug("Executed callback operator %s with result %s", op_idname, result)
            return result
        except Exception as e:
            logger.error("Failed to execute callback operator %s: %s", op_idname, e)
            return {"CANCELLED"}


_CLASSES = [
    QQ_ConfirmFilePath,
    QQ_ConfirmDialogProps,
    QQ_RENDER_OT_overwrite_confirm,
]


def register() -> None:
    """Registers confirm dialog classes and properties."""
    for cls in _CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.qq_confirm_dialog = PointerProperty(
        type=QQ_ConfirmDialogProps,
        name="Confirm Dialog",
        description="Properties for confirmation dialog"
    )
    logger.debug("Registered confirm dialog classes")


def unregister() -> None:
    """Unregisters confirm dialog classes and properties."""
    del bpy.types.WindowManager.qq_confirm_dialog

    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered confirm dialog classes")
