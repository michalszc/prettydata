"""Wrap report paragraphs using actual matplotlib font metrics."""

from __future__ import annotations

from textwrap import wrap

from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.font_manager import FontProperties


def _wrap_lines(text: str, width: float, font_size: float, weight: str) -> list[str]:
    """Conservatively wrap using the widest actual glyph in the text."""
    renderer = RendererAgg(1, 1, 72)
    font = FontProperties(family="DejaVu Sans", size=font_size, weight=weight)
    glyph_width = max(
        renderer.get_text_width_height_descent(char, font, ismath=False)[0]
        for char in set(text)
        if not char.isspace()
    )
    characters = max(1, int(width * 72 / max(1, glyph_width)))
    lines: list[str] = []
    for paragraph in text.expandtabs(4).split("\n"):
        lines.extend(wrap(paragraph, width=characters, break_on_hyphens=False) or [""])
    return lines
