"""
Export Camera Operators
    Description:
        Operators for exporting scene cameras to external formats such as Alembic.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Callable

import bpy

from ..core.path_utils import build_camera_export_path, resolve_relative_path, path_exists

if TYPE_CHECKING:
    from bpy.types import Context, Event

logger = logging.getLogger(__name__)


def _get_export_path(context: Context) -> Path | None:
    """Returns resolved export path for camera or None if project not saved."""
    if not bpy.data.filepath:
        return None

    blend_path = Path(bpy.data.filepath)
    project_name = blend_path.stem
    relative_path = build_camera_export_path(project_name)
    export_path = resolve_relative_path(blend_path, relative_path)
    logger.debug("Camera export path resolved to %s", export_path)
    return export_path


def _export_camera_to_alembic(context: Context, report_func: Callable) -> bool:
    """Exports active camera to Alembic file."""
    scene = context.scene
    camera = scene.camera

    if not camera:
        report_func({"ERROR"}, "No active camera in scene")
        return False

    export_path = _get_export_path(context)
    if not export_path:
        report_func({"WARNING"}, "Project is not saved. Please save the project first.")
        logger.warning("Camera export cancelled - project is not saved")
        return False

    export_path.parent.mkdir(parents=True, exist_ok=True)

    original_selection = [obj for obj in context.selected_objects]
    original_active = context.view_layer.objects.active

    for obj in context.selected_objects:
        obj.select_set(False)
    camera.select_set(True)
    context.view_layer.objects.active = camera

    try:
        bpy.ops.wm.alembic_export(
            filepath=str(export_path),
            start=scene.frame_start,
            end=scene.frame_end,
            selected=True,
            visible_objects_only=False,
            flatten=False,
            uvs=False,
            normals=False,
            vcolors=False,
            orcos=False,
            face_sets=False,
            curves_as_mesh=False,
            export_hair=False,
            export_particles=False,
            export_custom_properties=True,
            use_instancing=False,
            global_scale=1.0,
            triangulate=False,
        )
        report_func({"INFO"}, "Camera exported to %s" % export_path)
        logger.debug("Exported camera %s to %s", camera.name, export_path)
        return True

    except Exception as e:
        report_func({"ERROR"}, "Export failed: %s" % str(e))
        logger.error("Camera export failed: %s", str(e))
        return False

    finally:
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in original_selection:
            obj.select_set(True)
        context.view_layer.objects.active = original_active


class QQ_RENDER_OT_export_camera_execute(bpy.types.Operator):
    """Executes camera export without confirmation check."""

    bl_idname = "qq_render.export_camera_execute"
    bl_label = "Export Camera Execute"
    bl_description = "Execute camera export to Alembic file"
    bl_options = {"INTERNAL"}

    def execute(self, context: Context) -> set[str]:
        """Executes the camera export."""
        success = _export_camera_to_alembic(context, self.report)
        logger.debug("Camera export execute, success: %s", success)
        return {"FINISHED"} if success else {"CANCELLED"}


class QQ_RENDER_OT_export_camera(bpy.types.Operator):
    """Exports active camera with animation to Alembic file."""

    bl_idname = "qq_render.export_camera"
    bl_label = "Export Camera"
    bl_description = "Export active camera with animation to Alembic (.abc) file"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Checks if there is an active camera in the scene."""
        return context.scene.camera is not None

    def invoke(self, context: Context, event: Event) -> set[str]:
        """Checks for existing file and shows confirmation dialog if needed."""
        export_path = _get_export_path(context)

        if not export_path:
            self.report({"WARNING"}, "Project is not saved. Please save the project first.")
            logger.warning("Camera export cancelled - project is not saved")
            return {"CANCELLED"}

        if path_exists(export_path):
            props = context.window_manager.qq_confirm_dialog
            props.file_paths.clear()
            item = props.file_paths.add()
            item.path = str(export_path)
            props.callback_operator = "qq_render.export_camera_execute"
            props.title = "Camera export file already exists:"

            bpy.ops.qq_render.overwrite_confirm("INVOKE_DEFAULT")
            logger.debug("Showing overwrite confirm for %s", export_path)
            return {"FINISHED"}

        logger.debug("Invoke camera export for %s", export_path)
        return self.execute(context)

    def execute(self, context: Context) -> set[str]:
        """Executes the camera export operator."""
        success = _export_camera_to_alembic(context, self.report)
        return {"FINISHED"} if success else {"CANCELLED"}


_CLASSES = [
    QQ_RENDER_OT_export_camera_execute,
    QQ_RENDER_OT_export_camera,
]


def register() -> None:
    """Registers export operator classes."""
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    logger.debug("Registered %d export operator classes", len(_CLASSES))


def unregister() -> None:
    """Unregisters export operator classes."""
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered export operator classes")
