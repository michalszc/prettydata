"""Ordered PDF composition using existing Table and Chart renderers."""

from __future__ import annotations

from pathlib import Path
from textwrap import wrap
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties

from tabloom._rendering import _new_figure
from tabloom._themes import _get_theme
from tabloom.chart import Chart
from tabloom.table import Table

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def _check_text(value: Any) -> None:
    if not isinstance(value, str):
        message = "Text must be a string."
        raise TypeError(message)
    if not value.strip():
        message = "Text must not be empty or whitespace only."
        raise ValueError(message)


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


class Report:
    """Compose text, tables, and charts into an ordered multipage PDF.

    Args:
        title: Optional cover-page title. A title alone is a valid report.
        theme: Theme for text and cover pages. Existing visuals retain their
            own themes and any matplotlib customizations.

    Text is wrapped and paginated. Each table or chart occupies its own page
    using its existing dimensions. Objects are retained by reference and their
    current state is used when saving; no external LaTeX is required.
    """

    def __init__(self, title: str | None = None, *, theme: str = "default") -> None:
        self._theme = _get_theme(theme)
        if title is not None:
            _check_text(title)
        self.title = title
        self._elements: list[str | Table | Chart] = []

    def add_text(self, text: str) -> Report:
        """Append a nonempty text section and return this report."""
        _check_text(text)
        self._elements.append(text)
        return self

    def _add_visual(self, visual: Any, expected: type[Table | Chart]) -> Report:
        if not isinstance(visual, expected):
            message = f"Expected a Tabloom {expected.__name__}."
            raise TypeError(message)
        self._elements.append(visual)
        return self

    def add_table(self, table: Table) -> Report:
        """Append a table, rendered from its current data when saved."""
        return self._add_visual(table, Table)

    def add_chart(self, chart: Chart) -> Report:
        """Append a chart without taking ownership of its figure."""
        return self._add_visual(chart, Chart)

    def _write_text(self, pdf: PdfPages, text: str, *, cover: bool = False) -> None:
        width, height = 8.27, 11.69
        font_size = 24 if cover else 12
        top = 0.75 if cover else 0.92
        weight = "semibold" if cover else "normal"
        lines = _wrap_lines(text, width * 0.84, font_size, weight)
        per_page = max(1, int((top - 0.08) * height * 72 / (font_size * 1.5)))
        for start in range(0, len(lines), per_page):
            fig, ax = _new_figure(self._theme, (width, height), font_size)
            try:
                ax.set_axis_off()
                fig.text(
                    0.08,
                    top,
                    "\n".join(lines[start : start + per_page]),
                    va="top",
                    ha="left",
                    fontsize=font_size,
                    linespacing=1.5,
                    color=self._theme.foreground,
                    fontfamily="DejaVu Sans",
                    weight=weight,
                    usetex=False,
                    parse_math=False,
                )
                pdf.savefig(fig)
            finally:
                plt.close(fig)

    def _write_table(self, pdf: PdfPages, table: Table) -> None:
        fig: Figure
        fig, _ = table.render()
        try:
            pdf.savefig(fig, bbox_inches="tight", pad_inches=0.15)
        finally:
            plt.close(fig)

    def save(self, path: str | Path) -> None:
        """Write a PDF; an entirely empty report raises ValueError.

        Tables and charts remain reusable after saving, including when an
        export fails. Rendered table and text figures are closed after use.
        """
        if Path(path).suffix.lower() != ".pdf":
            message = "Reports must be saved with a .pdf extension."
            raise ValueError(message)
        if not self.title and not self._elements:
            message = "Cannot save an empty report; add a title or content."
            raise ValueError(message)
        with PdfPages(path, metadata={"Title": self.title or "Tabloom Report"}) as pdf:
            if self.title:
                self._write_text(pdf, self.title, cover=True)
            for element in self._elements:
                if isinstance(element, str):
                    self._write_text(pdf, element)
                elif isinstance(element, Table):
                    self._write_table(pdf, element)
                else:
                    pdf.savefig(element.fig, bbox_inches="tight", pad_inches=0.15)
