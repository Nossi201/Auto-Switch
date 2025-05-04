# 'src/utils/color_utils.py'
"""
Utility functions for color manipulation.
Provides functions to adjust color brightness, contrast, and other properties.
"""


def adjust_color(hex_color, offset=-10):
    """
    Adjusts a hex color by adding/subtracting from each RGB component.

    Args:
        hex_color: Hex color string (e.g. '#4287f5')
        offset: Amount to adjust RGB values (+/-)

    Returns:
        str: New hex color string
    """
    hex_color = hex_color.lstrip('#')

    # Parse RGB components
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Adjust and clamp values
    r_new = max(0, min(255, r + offset))
    g_new = max(0, min(255, g + offset))
    b_new = max(0, min(255, b + offset))

    # Return new hex color
    return f"#{r_new:02X}{g_new:02X}{b_new:02X}"


def get_contrasting_text_color(hex_color):
    """
    Determines whether white or black text should be used on a given background color.

    Args:
        hex_color: Hex color string (e.g. '#4287f5')

    Returns:
        str: '#FFFFFF' for white or '#000000' for black
    """
    hex_color = hex_color.lstrip('#')

    # Parse RGB components
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Calculate perceived brightness (ITU-R BT.709)
    brightness = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255

    # Use white text on dark backgrounds, black text on light backgrounds
    return '#FFFFFF' if brightness < 0.5 else '#000000'