"""
QQ Render
Core Constants
    Description:
        Application-wide constants, enums, and pass definitions
        for render node generation.
"""

from enum import Enum


class RenderEngine(Enum):
    """Supported render engines."""
    CYCLES = "CYCLES"
    EEVEE = "BLENDER_EEVEE_NEXT"
    EEVEE_LEGACY = "BLENDER_EEVEE"


class PassCategory(Enum):
    """Categories for organizing render passes."""
    MAIN = "main"
    DATA = "data"
    LIGHT = "light"
    CRYPTOMATTE = "cryptomatte"


CYCLES_PASSES = {
    PassCategory.MAIN: [
        ("use_pass_combined", "Combined"),
    ],
    PassCategory.DATA: [
        ("use_pass_z", "Depth"),
        ("use_pass_mist", "Mist"),
        ("use_pass_normal", "Normal"),
        ("use_pass_position", "Position"),
        ("use_pass_uv", "UV"),
        ("use_pass_vector", "Vector"),
        ("use_pass_object_index", "IndexOB"),
        ("use_pass_material_index", "IndexMA"),
    ],
    PassCategory.LIGHT: [
        ("use_pass_diffuse_direct", "DiffDir"),
        ("use_pass_diffuse_indirect", "DiffInd"),
        ("use_pass_diffuse_color", "DiffCol"),
        ("use_pass_glossy_direct", "GlossDir"),
        ("use_pass_glossy_indirect", "GlossInd"),
        ("use_pass_glossy_color", "GlossCol"),
        ("use_pass_transmission_direct", "TransDir"),
        ("use_pass_transmission_indirect", "TransInd"),
        ("use_pass_transmission_color", "TransCol"),
        ("use_pass_volume_direct", "VolumeDir"),
        ("use_pass_volume_indirect", "VolumeInd"),
        ("use_pass_emit", "Emit"),
        ("use_pass_environment", "Env"),
        ("use_pass_shadow", "Shadow"),
        ("use_pass_ambient_occlusion", "AO"),
    ],
    PassCategory.CRYPTOMATTE: [
        ("use_pass_cryptomatte_object", "CryptoObject"),
        ("use_pass_cryptomatte_material", "CryptoMaterial"),
        ("use_pass_cryptomatte_asset", "CryptoAsset"),
    ],
}

EEVEE_PASSES = {
    PassCategory.MAIN: [
        ("use_pass_combined", "Combined"),
    ],
    PassCategory.DATA: [
        ("use_pass_z", "Depth"),
        ("use_pass_mist", "Mist"),
        ("use_pass_normal", "Normal"),
        ("use_pass_position", "Position"),
        ("use_pass_vector", "Vector"),
    ],
    PassCategory.LIGHT: [
        ("use_pass_diffuse_direct", "DiffLight"),
        ("use_pass_diffuse_color", "DiffCol"),
        ("use_pass_glossy_direct", "SpecLight"),
        ("use_pass_glossy_color", "SpecCol"),
        ("use_pass_emit", "Emit"),
        ("use_pass_environment", "Env"),
        ("use_pass_shadow", "Shadow"),
        ("use_pass_ambient_occlusion", "AO"),
    ],
    PassCategory.CRYPTOMATTE: [
        ("use_pass_cryptomatte_object", "CryptoObject"),
        ("use_pass_cryptomatte_material", "CryptoMaterial"),
        ("use_pass_cryptomatte_asset", "CryptoAsset"),
    ],
}

NODE_COLORS = {
    "file_output": (0.55, 0.33, 0.17),
    "render_layers": (0.30, 0.45, 0.30),
    "denoise": (0.35, 0.35, 0.55),
}

FILE_OUTPUT_DEFAULTS = {
    "format": "OPEN_EXR_MULTILAYER",
    "color_depth": "32",
    "codec": "DWAA",
}
