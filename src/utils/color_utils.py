"""Utility functions for color manipulation.

Provides functions to adjust color brightness, contrast, and other
properties. Supports both three- and six-character HEX color strings.
"""


def _normalize_hex(hex_color: str) -> str:
    """Return a normalized 6-character hex string without the leading '#'.

    Accepts either 3- or 6-character hex color strings. A ``ValueError`` is
    raised if the provided color is of any other length.
    """

    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    elif len(hex_color) != 6:
        raise ValueError("hex_color must be 3 or 6 hex digits")
    return hex_color


def adjust_color(hex_color: str, offset: int = -10) -> str:
    """Adjust a hex color by adding/subtracting from each RGB component."""

    hex_color = _normalize_hex(hex_color)

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r_new = max(0, min(255, r + offset))
    g_new = max(0, min(255, g + offset))
    b_new = max(0, min(255, b + offset))

    return f"#{r_new:02X}{g_new:02X}{b_new:02X}"


def get_contrasting_text_color(hex_color: str) -> str:
    """Return '#FFFFFF' or '#000000' for readable text on a color."""

    hex_color = _normalize_hex(hex_color)

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    brightness = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255

    return "#FFFFFF" if brightness < 0.5 else "#000000"

