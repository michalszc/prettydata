"""Render a measured text chunk into a tightly controlled native PDF block."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from tabloom.rendering.new_figure import _new_figure

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tabloom.themes.theme import _Theme


def _render_text(
    lines: Sequence[str], width: float, font_size: float, weight: str, theme: _Theme
) -> bytes:
    """Render wrapped lines at a width and line-box height measured in points.

    Each line reserves 1.5 times the font size. The caller chooses a chunk that
    fits the current report page. Only the temporary rendering figure is closed.
    """
    height = len(lines) * font_size * 1.5
    fig, ax = _new_figure(theme, (width / 72, height / 72), font_size)
    try:
        fig.set_layout_engine(None)
        ax.set_axis_off()
        fig.text(
            0,
            1,
            "\n".join(lines),
            va="top",
            ha="left",
            fontsize=font_size,
            linespacing=1.5,
            color=theme.foreground,
            fontfamily="DejaVu Sans",
            weight=weight,
            usetex=False,
            parse_math=False,
        )
        with BytesIO() as buffer:
            with PdfPages(buffer) as pdf:
                pdf.savefig(fig, bbox_inches=fig.bbox_inches, pad_inches=0)
            return buffer.getvalue()
    finally:
        plt.close(fig)
