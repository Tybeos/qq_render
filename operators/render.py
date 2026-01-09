"""
Render Operators
    Description:
        Operators for rendering animations in Blender with output file checks.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import bpy

from ..core.path_utils import (
    build_camera_export_path,
    path_exists,
    resolve_relative_path,
)

if TYPE_CHECKING:
    from bpy.types import Context, Event

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class QQ_RENDER_OT_render_animation_execute(bpy.types.Operator):
    """Executes render animation without confirmation check."""

    bl_idname = "qq_render.render_animation_execute"
    bl_label = "Render Animation Execute"
    bl_description = "Execute animation render"
    bl_options = {"INTERNAL"}

    def execute(self, context: Context) -> set[str]:
        """Executes the render animation operator."""
        scene = context.scene

        if scene.qq_render_export_camera:
            bpy.ops.qq_render.export_camera_execute()
            logger.debug("Exported camera before render")

        bpy.ops.render.render("INVOKE_DEFAULT", animation=True, use_viewport=True)
        logger.debug("Started animation render for frames %d-%d", scene.frame_start, scene.frame_end)
        return {"FINISHED"}


class QQ_RENDER_OT_check_and_render(bpy.types.Operator):
    """Checks for existing render outputs and renders animation with confirmation."""

    bl_idname = "qq_render.check_and_render"
    bl_label = "qq Render Animation"
    bl_description = "Check for existing outputs and render active scene"
    bl_options = {"REGISTER"}

    def invoke(self, context: Context, event: Event) -> set[str]:
        """Checks for existing files and shows confirmation dialog if needed."""
        if not bpy.data.filepath:
            self.report({"WARNING"}, "Project is not saved. Please save the project first.")
            logger.warning("Render cancelled - project is not saved")
            return {"CANCELLED"}

        scene = context.scene

        if scene.qq_render_update_paths:
            bpy.ops.qq_render.update_output_paths()
            logger.debug("Updated output paths before render check")

        if not scene.use_nodes or not scene.node_tree:
            logger.debug("No compositor nodes, proceeding with render")
            return bpy.ops.qq_render.render_animation_execute()

        tree = scene.node_tree
        blend_path = Path(bpy.data.filepath)
        project_name = blend_path.stem
        existing_paths = []
        file_output_count = 0

        if scene.qq_render_export_camera:
            camera_relative_path = build_camera_export_path(project_name)
            camera_path = resolve_relative_path(blend_path, camera_relative_path)
            if path_exists(camera_path):
                existing_paths.append(str(camera_path))
                logger.debug("Found existing camera export at %s", camera_path)

        for node in tree.nodes:
            if node.type == "OUTPUT_FILE":
                file_output_count += 1
                base_path_str = node.base_path
                resolved = resolve_relative_path(blend_path, base_path_str)

                if path_exists(resolved):
                    existing_paths.append(str(resolved))
                    logger.debug("Found existing output at %s", resolved)

        if file_output_count == 0:
            self.report({"WARNING"}, "No File Output nodes found")
            logger.warning("Render cancelled - no File Output nodes found")
            return {"CANCELLED"}

        if existing_paths:
            props = context.window_manager.qq_confirm_dialog
            props.file_paths.clear()

            for path in existing_paths:
                item = props.file_paths.add()
                item.path = path

            props.callback_operator = "qq_render.render_animation_execute"
            props.title = "Render outputs already exist:"

            bpy.ops.qq_render.overwrite_confirm("INVOKE_DEFAULT")
            logger.debug("Showing overwrite confirm for %d paths", len(existing_paths))
            return {"FINISHED"}

        logger.debug("No existing outputs found, proceeding with render")
        return bpy.ops.qq_render.render_animation_execute()

    def execute(self, context: Context) -> set[str]:
        """Fallback execute method."""
        return bpy.ops.qq_render.render_animation_execute()


_CLASSES = [
    QQ_RENDER_OT_render_animation_execute,
    QQ_RENDER_OT_check_and_render,
]


def register() -> None:
    """Registers operator classes."""
    for cls in _CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.qq_render_export_camera = bpy.props.BoolProperty(
        name="Export Camera",
        description="Export camera to Alembic before rendering",
        default=False
    )

    bpy.types.Scene.qq_render_update_paths = bpy.props.BoolProperty(
        name="Update Output Paths",
        description="Update File Output node paths before rendering",
        default=True
    )

    logger.debug("Registered %d operator classes", len(_CLASSES))


def unregister() -> None:
    """Unregisters operator classes."""
    del bpy.types.Scene.qq_render_update_paths
    del bpy.types.Scene.qq_render_export_camera

    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered operator classes")
