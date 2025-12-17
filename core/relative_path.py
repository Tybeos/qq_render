"""
Relative Path Utilities
    Description:
        Functions for generating relative output paths for render outputs.
"""

import logging
import re

logger = logging.getLogger(__name__)

version_regex = re.compile(r"(v\d{1,3})", re.IGNORECASE)
version_number_regex = re.compile(r"v(\d+)$", re.IGNORECASE)


def build_base_path(project_name, layer_name):
    """Builds the output base path by inserting layer name before version."""
    match = version_regex.search(project_name)

    if match:
        version_part = match.group(1)
        prefix = project_name[:match.start()]
        prefix = prefix.rstrip(".")
        suffix = project_name[match.end():]
        result = "{prefix}.l.{layer}.{version}{suffix}".format(
            prefix=prefix,
            layer=layer_name,
            version=version_part,
            suffix=suffix
        )
    else:
        result = "{project}.l.{layer}".format(
            project=project_name,
            layer=layer_name
        )

    base_path = "//../render/render_master/{result}/{result}.####.exr".format(result=result)
    logger.debug("Built base path %s from project %s layer %s", base_path, project_name, layer_name)
    return base_path


def build_camera_export_path(project_name):
    """Builds the camera export path with version info extracted from project name."""
    match = version_regex.search(project_name)

    if match:
        version_part = match.group(1)
        prefix = project_name[:match.start()]
        prefix = prefix.rstrip(".")
        suffix = project_name[match.end():]
        filename = "{prefix}.camera.{version}{suffix}.abc".format(
            prefix=prefix,
            version=version_part,
            suffix=suffix
        )
    else:
        filename = "{project}.camera.abc".format(project=project_name)

    export_path = "//../render/render_master/{filename}".format(filename=filename)
    logger.debug("Built camera export path %s from project %s", export_path, project_name)
    return export_path


if __name__ == "__main__":
    print(build_base_path("rendering.v01", "letadlo"))
    print(build_base_path("rendering.v01.test", "letadlo"))
    print(build_base_path("project.v123.final", "background"))
    print(build_base_path("noversion", "layer1"))
    print(build_camera_export_path("rendering.v01"))
    print(build_camera_export_path("rendering.v01.test"))
    print(build_camera_export_path("project.v123.final"))
    print(build_camera_export_path("noversion"))
