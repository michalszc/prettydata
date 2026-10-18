"""Resolve a supported theme name to immutable visual settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tabloom.themes.presets import _THEMES

if TYPE_CHECKING:
    from tabloom.themes.theme import _Theme


def _get_theme(name: str) -> _Theme:
    """Return a named preset, raising ValueError for unsupported names."""
    if name not in _THEMES:
        message = f"Unknown theme {name!r}; choose default, light, or dark."
        raise ValueError(message)
    return _THEMES[name]
