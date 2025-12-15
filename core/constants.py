"""
Core Constants
    Description:
        Application-wide constants, enums, and pass definitions
        for render node generation.
"""

SKIP_PASSES = {
    "Denoising Normal",
    "Denoising Albedo",
    "Denoising Depth"
}

DENOISE_PASSES = {
    "Mist",
    "DiffDir",
    "DiffInd",
    "DiffCol",
    "GlossDir",
    "GlossInd",
    "GlossCol",
    "TransDir",
    "TransInd",
    "TransCol",
    "VolumeDir",
    "VolumeInd",
    "Emit",
    "Env",
    "AO",
    "Shadow Catcher"
}

NODE_COLORS = {
    "file_output": (0.55, 0.33, 0.17),
    "render_layers": (0.30, 0.45, 0.30),
    "denoise": (0.35, 0.35, 0.55),
    "image": (0.30, 0.45, 0.30),
    "composite": (0.55, 0.33, 0.17),
    "viewer": (0.55, 0.33, 0.17)
}

FILE_OUTPUT_DEFAULTS = {
    "format": "OPEN_EXR_MULTILAYER",
    "color_depth": "32",
    "codec": "ZIP",
}
