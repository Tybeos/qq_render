"""
QQ Render
Core Constants
    Description:
        Application-wide constants, enums, and pass definitions
        for render node generation.
"""

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
