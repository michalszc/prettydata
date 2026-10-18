"""Render a measured text chunk into a tightly controlled native PDF block."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from tabloom.rendering.new_figure import _new_figure

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tabloom.report.text_block import _TextBlock
    from tabloom.themes.theme import _Theme


def _render_text(
    lines: Sequence[str], width: float, block: _TextBlock, theme: _Theme
) -> bytes:
    """Render wrapped lines at a width and line-box height measured in points.

    Line boxes reflect the block's font size and spacing. The caller chooses a
    chunk that fits the current page. Only the temporary figure is closed.
    """
    height = len(lines) * block.font_size * block.line_spacing
    fig, ax = _new_figure(theme, (width / 72, height / 72), block.font_size)
    try:
        fig.set_layout_engine(None)
        ax.set_axis_off()
        fig.text(
            {"left": 0, "center": 0.5, "right": 1}[block.align],
            1,
            "\n".join(lines),
            va="top",
            ha=block.align,
            multialignment=block.align,
            fontproperties=block.font,
            linespacing=block.line_spacing,
            color=block.color or theme.foreground,
            usetex=False,
            parse_math=False,
        )
        with BytesIO() as buffer:
            with PdfPages(buffer) as pdf:
                pdf.savefig(fig, bbox_inches=fig.bbox_inches, pad_inches=0)
            return buffer.getvalue()
    finally:
        plt.close(fig)
