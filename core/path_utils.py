"""
Path Utilities
    Description:
        Functions for path operations including existence checks for files
        and image sequences, and generating relative output paths.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

from ..vendor.fileseq.src import FileSequence
from ..vendor.fileseq.src.exceptions import FileSeqException

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

_SEQUENCE_PATTERN = re.compile(r"[#@]+|%\d*d|\$F\d*")

version_regex = re.compile(r"(v\d{1,3})", re.IGNORECASE)
version_number_regex = re.compile(r"v(\d+)$", re.IGNORECASE)


def build_base_path(project_name: str, layer_name: str) -> str:
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

    base_path = "//../render/render_master/{project_name}/{result}/{result}.####.exr".format(
        project_name=project_name,
        result=result)
    logger.debug("Built base path %s from project %s layer %s", base_path, project_name, layer_name)
    return base_path


def build_camera_export_path(project_name: str) -> str:
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

    export_path = "//../render/render_master/{project_name}/{filename}".format(
        project_name=project_name,
        filename=filename)
    logger.debug("Built camera export path %s from project %s", export_path, project_name)
    return export_path


def path_exists(path: Path) -> bool:
    """Checks if a file or image sequence exists on disk."""
    path_str = str(path)

    if _SEQUENCE_PATTERN.search(path_str):
        try:
            FileSequence.findSequenceOnDisk(path_str)
            logger.debug("Sequence exists at %s", path)
            return True
        except FileSeqException:
            logger.debug("Sequence not found at %s", path)
            return False

    exists = path.exists()
    logger.debug("Path %s exists: %s", path, exists)
    return exists


def resolve_relative_path(blend_path: Path, relative_path: str) -> Path:
    """Resolves a Blender relative path to an absolute path."""
    if relative_path.startswith("//"):
        relative_path = relative_path[2:]

    resolved = (blend_path.parent / relative_path).resolve()
    logger.debug("Resolved %s relative to %s as %s", relative_path, blend_path, resolved)
    return resolved



