"""Ordered PDF reports combining text and existing Table/Chart visuals."""

from __future__ import annotations

from io import BytesIO
from math import isfinite
from pathlib import Path
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from tabloom.chart import Chart
from tabloom.rendering.new_figure import _new_figure
from tabloom.report.fit_pages import _fit_pages
from tabloom.report.wrap_lines import _wrap_lines
from tabloom.table import Table
from tabloom.themes.get_theme import _get_theme
from tabloom.validation.positive import _positive
from tabloom.validation.text import _check_text

if TYPE_CHECKING:
    from matplotlib.figure import Figure


class Report:
    """Compose text, tables, and charts into an ordered multipage PDF.

    Args:
        title: Optional cover-page title. A title alone is a valid report.
        theme: Theme for text and cover pages. Existing visuals retain their
            own themes and any matplotlib customizations.
        figsize: Common paper width and height in inches. Defaults to A4 portrait.
        margin: Printable margin in inches; defaults to 0.6 on every side.

    Text is wrapped and paginated. Each table or chart is fitted to one page
    with its aspect ratio, vector graphics, and searchable text preserved.
    All pages have the same paper dimensions. Objects are retained by reference;
    their current state is used when saving. No external LaTeX is required.
    """

    def __init__(
        self,
        title: str | None = None,
        *,
        theme: str = "default",
        figsize: tuple[float, float] = (8.27, 11.69),
        margin: float = 0.6,
    ) -> None:
        self._theme = _get_theme(theme)
        if title is not None:
            _check_text(title)
        width, height = figsize
        _positive(width, "Page width")
        _positive(height, "Page height")
        if not isfinite(margin) or margin < 0 or 2 * margin >= min(width, height):
            message = "margin must be nonnegative and leave a positive printable area."
            raise ValueError(message)
        self.figsize = (width, height)
        self.margin = margin
        self.title = title
        self._elements: list[str | Table | Chart] = []

    def add_text(self, text: str) -> Report:
        """Append text to the report in insertion order.

        Args:
            text: A nonempty string. Paragraphs are wrapped and paginated
                within the configured paper size and margins when saving.

        Returns:
            This report, allowing method chaining.

        Raises:
            TypeError: The input is not a string.
            ValueError: The input is empty or contains only whitespace.
        """
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
        """Append a table to be rendered from its current data when saving.

        Args:
            table: A Table instance to fit onto a report page.

        Returns:
            This report, allowing method chaining.

        Raises:
            TypeError: The input is not a Table.
        """
        return self._add_visual(table, Table)

    def add_chart(self, chart: Chart) -> Report:
        """Append a chart without taking ownership of its figure.

        Args:
            chart: A Chart instance. Its current figure is exported at save
                time, and the original dimensions and layout are preserved.

        Returns:
            This report, allowing method chaining.

        Raises:
            TypeError: The input is not a Chart.
        """
        return self._add_visual(chart, Chart)

    def _write_text(self, pdf: PdfPages, text: str, *, cover: bool = False) -> None:
        width, height = self.figsize
        font_size = 24 if cover else 12
        top = min(0.75, 1 - self.margin / height) if cover else 1 - self.margin / height
        weight = "semibold" if cover else "normal"
        lines = _wrap_lines(text, width - 2 * self.margin, font_size, weight)
        per_page = max(
            1, int((top - self.margin / height) * height * 72 / (font_size * 1.5))
        )
        for start in range(0, len(lines), per_page):
            fig, ax = _new_figure(self._theme, (width, height), font_size)
            try:
                ax.set_axis_off()
                fig.text(
                    self.margin / width,
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

    def _write_chart(self, pdf: PdfPages, chart: Chart) -> None:
        """Export the chart while restoring layout adjustments made by matplotlib."""
        positions = [
            (
                ax,
                ax.get_position().frozen(),
                ax.get_position(original=True).frozen(),
                ax.get_in_layout(),
            )
            for ax in chart.fig.axes
        ]
        try:
            pdf.savefig(chart.fig, bbox_inches="tight", pad_inches=0.15)
        finally:
            for ax, active, original, in_layout in positions:
                ax.set_position(original, which="original")
                ax.set_position(active, which="active")
                ax.set_in_layout(in_layout)

    def save(self, path: str | Path) -> None:
        """Write a PDF with uniform page dimensions and preserved vector visuals.

        Args:
            path: Destination PDF filename; its parent directory must exist.

        Raises:
            ValueError: The extension is not .pdf or the report has no content
                and no title.

        Tables and charts remain reusable after saving, including when an
        export fails. Rendered table and text figures are closed after use.
        """
        if Path(path).suffix.lower() != ".pdf":
            message = "Reports must be saved with a .pdf extension."
            raise ValueError(message)
        if not self.title and not self._elements:
            message = "Cannot save an empty report; add a title or content."
            raise ValueError(message)
        with BytesIO() as buffer:
            with PdfPages(
                buffer, metadata={"Title": self.title or "Tabloom Report"}
            ) as pdf:
                if self.title:
                    self._write_text(pdf, self.title, cover=True)
                for element in self._elements:
                    if isinstance(element, str):
                        self._write_text(pdf, element)
                    elif isinstance(element, Table):
                        self._write_table(pdf, element)
                    else:
                        self._write_chart(pdf, element)
            _fit_pages(
                buffer,
                path,
                figsize=self.figsize,
                margin=self.margin,
                background=self._theme.background,
            )
