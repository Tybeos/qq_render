"""
Export Operators
    Description:
        Operators for exporting scene elements like cameras
        to external formats such as Alembic.
"""

import logging
from pathlib import Path

import bpy

logger = logging.getLogger(__name__)


def get_export_path(context, filename):
    """Returns export path based on blend file location or temp directory."""
    if bpy.data.filepath:
        blend_dir = Path(bpy.data.filepath).parent
        export_dir = blend_dir / "export"
    else:
        export_dir = Path(bpy.app.tempdir) / "export"

    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = export_dir / filename
    logger.debug("Generated export path %s", export_path)
    return export_path


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

    def execute(self, context):
        """Executes the camera export operator."""
        scene = context.scene
        camera = scene.camera

        if not camera:
            self.report({"ERROR"}, "No active camera in scene")
            return {"CANCELLED"}

        project_name = Path(bpy.data.filepath).stem if bpy.data.filepath else "untitled"
        filename = "{}_camera.abc".format(project_name)
        export_path = get_export_path(context, filename)

        original_selection = context.selected_objects.copy()
        original_active = context.view_layer.objects.active

        bpy.ops.object.select_all(action="DESELECT")
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
            self.report({"INFO"}, "Camera exported to {}".format(export_path))
            logger.debug("Exported camera %s to %s", camera.name, export_path)

        except Exception as e:
            self.report({"ERROR"}, "Export failed: {}".format(str(e)))
            logger.error("Camera export failed: %s", str(e))
            return {"CANCELLED"}

        finally:
            bpy.ops.object.select_all(action="DESELECT")
            for obj in original_selection:
                obj.select_set(True)
            context.view_layer.objects.active = original_active

        return {"FINISHED"}


classes = [
    QQ_RENDER_OT_export_camera,
]


def register():
    """Registers export operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    logger.debug("Registered %d export operator classes", len(classes))


def unregister():
    """Unregisters export operator classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    logger.debug("Unregistered export operator classes")
