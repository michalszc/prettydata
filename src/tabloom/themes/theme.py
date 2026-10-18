"""Immutable color configuration shared by tables, charts, and reports."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class _Theme:
    """Colors for a figure background, typography, table cells, and data series."""

    background: str
    foreground: str
    muted: str
    grid: str
    header_background: str
    header_color: str
    rows: tuple[str, str]
    palette: tuple[str, ...]
