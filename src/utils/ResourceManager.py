# src/utils/ResourceManager.py
"""Utility helper – resolves paths to data/assets inside the project."""
from __future__ import annotations

from pathlib import Path


def _project_root() -> Path:
    """Return the project root folder (parent of 'src')."""
    return Path(__file__).resolve().parent.parent.parent


def get_data_path(filename: str) -> str:
    """
    Return an absolute path to *src/data/<filename>*.

    Args:
        filename: File name located in *src/data/*.

    Returns:
        Absolute path as string.
    """
    return str(_project_root() / "src" / "data" / filename)
