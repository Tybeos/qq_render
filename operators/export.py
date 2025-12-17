"""
Export Operators
    Description:
        Operators for exporting scene elements like cameras
        to external formats such as Alembic.
"""

import logging
from pathlib import Path

import bpy

from ..core.relative_path import build_camera_export_path

logger = logging.getLogger(__name__)


def export_camera_to_alembic(context, report_func):
    """Exports active camera to Alembic file."""
    scene = context.scene
    camera = scene.camera

    if not camera:
        report_func({"ERROR"}, "No active camera in scene")
        return False

    if not bpy.data.filepath:
        report_func({"WARNING"}, "Project is not saved. Please save the project first.")
        logger.warning("Camera export cancelled - project is not saved")
        return False

    blend_path = Path(bpy.data.filepath)
    project_name = blend_path.stem
    relative_path = build_camera_export_path(project_name)
    export_path = bpy.path.abspath(relative_path)
    export_path_obj = Path(export_path)
    export_path_obj.parent.mkdir(parents=True, exist_ok=True)

    original_selection = [obj for obj in context.selected_objects]
    original_active = context.view_layer.objects.active

    for obj in context.selected_objects:
        obj.select_set(False)
    camera.select_set(True)
    context.view_layer.objects.active = camera

    try:
        bpy.ops.wm.alembic_export(
            filepath=str(export_path_obj),
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
        report_func({"INFO"}, "Camera exported to {}".format(export_path_obj))
        logger.debug("Exported camera %s to %s", camera.name, export_path_obj)
        return True

    except Exception as e:
        report_func({"ERROR"}, "Export failed: {}".format(str(e)))
        logger.error("Camera export failed: %s", str(e))
        return False

    finally:
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in original_selection:
            obj.select_set(True)
        context.view_layer.objects.active = original_active


class QQ_RENDER_OT_export_camera_confirm(bpy.types.Operator):
    """Confirmation dialog for overwriting existing camera export."""

    bl_idname = "qq_render.export_camera_confirm"
    bl_label = "Overwrite Warning"
    bl_description = "Overwrite existing camera export file"
    bl_options = {"INTERNAL"}

    def invoke(self, context, event):
        """Shows the confirmation dialog centered in Blender window."""
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        """Draws the confirmation dialog content."""
        layout = self.layout
        export_path = context.window_manager.qq_render_export_path
        layout.label(text="Camera export file already exists:")
        layout.label(text=export_path)
        layout.label(text="Do you want to overwrite it?")

    def execute(self, context):
        """Performs the overwrite export."""
        success = export_camera_to_alembic(context, self.report)
        logger.debug("Overwrite confirmed, success: %s", success)
        return {"FINISHED"} if success else {"CANCELLED"}



class QQ_RENDER_OT_export_camera(bpy.types.Operator):
    """Exports active camera with animation to Alembic file."""

    bl_idname = "qq_render.export_camera"
    bl_label = "Export Camera"
    bl_description = "Export active camera with animation to Alembic (.abc) file"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Checks if there is an active camera in the scene."""
        return context.scene.camera is not None

    def invoke(self, context, event):
        """Checks for existing file and shows confirmation dialog if needed."""
        if not bpy.data.filepath:
            self.report({"WARNING"}, "Project is not saved. Please save the project first.")
            logger.warning("Camera export cancelled - project is not saved")
            return {"CANCELLED"}

        blend_path = Path(bpy.data.filepath)
        project_name = blend_path.stem
        relative_path = build_camera_export_path(project_name)
        export_path = bpy.path.abspath(relative_path)
        export_path_obj = Path(export_path)

        if export_path_obj.exists():
            context.window_manager.qq_render_export_path = str(export_path_obj)
            bpy.ops.qq_render.export_camera_confirm("INVOKE_DEFAULT")
            return {"FINISHED"}

        logger.debug("Invoke camera export for %s", export_path_obj)
        return self.execute(context)

    def execute(self, context):
        """Executes the camera export operator."""
        success = export_camera_to_alembic(context, self.report)
        return {"FINISHED"} if success else {"CANCELLED"}


classes = [
    QQ_RENDER_OT_export_camera_confirm,
    QQ_RENDER_OT_export_camera,
]


def register():
    """Registers export operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.qq_render_export_path = bpy.props.StringProperty(
        name="Export Path",
        description="Temporary storage for export path in confirmation dialog",
        default=""
    )
    logger.debug("Registered %d export operator classes", len(classes))


def unregister():
    """Unregisters export operator classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.WindowManager.qq_render_export_path
    logger.debug("Unregistered export operator classes")
