"""Ordered PDF reports combining text and existing Table/Chart visuals."""

from __future__ import annotations

from io import BytesIO
from math import isfinite
from pathlib import Path
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from tabloom.chart import Chart
from tabloom.report.page_composer import _PageComposer
from tabloom.report.render_text import _render_text
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
        title: Optional heading on the first page. A title alone is a valid report.
        theme: Theme for report pages and text. Existing visuals retain their
            own themes and any matplotlib customizations.
        figsize: Common paper width and height in inches. Defaults to A4 portrait.
        margin: Printable margin in inches; defaults to 0.6 on every side.

    Content flows into the remaining page space in insertion order. Text wraps
    and paginates; visual blocks remain intact and move to a new page only when
    needed. Aspect ratios, vector graphics, and searchable text are preserved.
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
        self._elements: list[str | Table | Chart | None] = []

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
            table: A Table instance to place in the nearest available space.
                The table stays intact and moves to a new page if needed.

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

    def add_page_break(self) -> Report:
        """Start a new page before the next content element.

        Leading, trailing, and consecutive breaks do not create empty pages.
        To use a separate title page, add a break immediately after constructing
        the report.

        Returns:
            This report, allowing method chaining.
        """
        self._elements.append(None)
        return self

    def _write_text(
        self, composer: _PageComposer, text: str, *, heading: bool = False
    ) -> None:
        """Wrap text and render only the lines that fit the current page."""
        font_size = 24 if heading else 12
        weight = "semibold" if heading else "normal"
        line_height = font_size * 1.5
        if line_height > composer.content_height:
            message = "The printable page area is too small for report text."
            raise ValueError(message)
        lines = _wrap_lines(text, composer.content_width / 72, font_size, weight)
        offset = 0
        while offset < len(lines):
            capacity = int((composer.remaining_height + 1e-6) / line_height)
            if capacity < 1:
                composer.new_page()
                capacity = int((composer.remaining_height + 1e-6) / line_height)
            chunk = lines[offset : offset + capacity]
            composer.add_pdf(
                _render_text(
                    chunk, composer.content_width, font_size, weight, self._theme
                )
            )
            offset += len(chunk)

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
        """Write ordered content into the available space on uniform PDF pages.

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
        if not self.title and not any(
            element is not None for element in self._elements
        ):
            message = "Cannot save an empty report; add a title or content."
            raise ValueError(message)
        with _PageComposer(
            self.figsize,
            self.margin,
            self._theme.background,
            self.title or "Tabloom Report",
        ) as composer:
            if self.title:
                self._write_text(composer, self.title, heading=True)
            for element in self._elements:
                if element is None:
                    composer.request_break()
                elif isinstance(element, str):
                    self._write_text(composer, element)
                else:
                    with BytesIO() as buffer:
                        with PdfPages(buffer) as pdf:
                            if isinstance(element, Table):
                                self._write_table(pdf, element)
                            else:
                                self._write_chart(pdf, element)
                        composer.add_pdf(buffer.getvalue())
            composer.save(path)
