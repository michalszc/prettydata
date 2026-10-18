"""Measure plain multiline text using matplotlib font metrics."""

from __future__ import annotations

from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.font_manager import FontProperties


def _text_size(
    text: str, font_size: float, weight: str = "normal"
) -> tuple[float, float]:
    """Measure plain multiline text in inches using matplotlib's own renderer."""
    renderer = RendererAgg(1, 1, 72)
    font = FontProperties(family="DejaVu Sans", size=font_size, weight=weight)
    lines = text.split("\n")
    width = max(
        renderer.get_text_width_height_descent(line, font, ismath=False)[0]
        for line in lines
    )
    return (width + 12) / (0.84 * 72), (len(lines) * font_size * 1.4 + 14) / 72
