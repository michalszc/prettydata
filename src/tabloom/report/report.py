"""Ordered PDF reports combining text and existing Table/Chart visuals."""

from __future__ import annotations

from io import BytesIO
from math import isfinite
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from tabloom.chart import Chart
from tabloom.report.page_composer import _PageComposer
from tabloom.report.render_text import _render_text
from tabloom.report.text_block import _TextBlock
from tabloom.report.visual_block import _VisualBlock
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
    Text typography is configurable per block. Visuals fill the printable width
    by default; select fractional width or original sizing on each add method.
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
        self._elements: list[_TextBlock | _VisualBlock | None] = []

    def add_text(  # noqa: PLR0913 - explicit, discoverable typography controls
        self,
        text: str,
        *,
        font_family: str = "DejaVu Sans",
        font_size: float = 12,
        font_weight: str | int = "normal",
        font_style: Literal["normal", "italic", "oblique"] = "normal",
        color: str | None = None,
        align: Literal["left", "center", "right"] = "left",
        line_spacing: float = 1.5,
        space_after: float = 12,
    ) -> Report:
        """Append text to the report in insertion order.

        Args:
            text: A nonempty string. Paragraphs are wrapped and paginated
                within the configured paper size and margins when saving.
            font_family: An installed matplotlib font family or generic alias.
            font_size: Positive font size in points; defaults to 12.
            font_weight: Matplotlib font weight such as normal, bold, or 700.
            font_style: Matplotlib font style: normal, italic, or oblique.
            color: Matplotlib color; None uses the report theme's foreground.
            align: Horizontal alignment: left, center, or right.
            line_spacing: Line-height multiplier; finite and at least 1.
            space_after: Nonnegative space after this block in points.

        Returns:
            This report, allowing method chaining.

        Raises:
            TypeError: A text argument or styling option has an invalid type.
            ValueError: Text, typography, color, or spacing is invalid, or the
                requested font family is unavailable.
        """
        block = _TextBlock(
            text,
            font_family=font_family,
            font_size=font_size,
            font_weight=font_weight,
            font_style=font_style,
            color=color,
            align=align,
            line_spacing=line_spacing,
            space_after=space_after,
        )
        self._elements.append(block)
        return self

    def _add_visual(
        self,
        visual: Any,
        expected: type[Table | Chart],
        resize: Literal["full", "original"] | float,
    ) -> Report:
        if not isinstance(visual, expected):
            message = f"Expected a Tabloom {expected.__name__}."
            raise TypeError(message)
        self._elements.append(_VisualBlock(visual, resize))
        return self

    def add_table(
        self, table: Table, *, resize: Literal["full", "original"] | float = "full"
    ) -> Report:
        """Append a table to be rendered from its current data when saving.

        Args:
            table: A Table instance to place in the nearest available space.
                The table stays intact and moves to a new page if needed.
            resize: Full printable width by default ("full"), a width fraction
                in (0, 1], or "original" to keep native size where it fits.
                Aspect ratio is preserved; page height may limit the width.

        Returns:
            This report, allowing method chaining.

        Raises:
            TypeError: The input is not a Table or resize has an invalid type.
            ValueError: The resize policy or width fraction is invalid.
        """
        return self._add_visual(table, Table, resize)

    def add_chart(
        self, chart: Chart, *, resize: Literal["full", "original"] | float = "full"
    ) -> Report:
        """Append a chart without taking ownership of its figure.

        Args:
            chart: A Chart instance. Its current figure is exported at save
                time, and the original dimensions and layout are preserved.
            resize: Full printable width by default ("full"), a width fraction
                in (0, 1], or "original" to keep native size where it fits.
                Aspect ratio is preserved; page height may limit the width.

        Returns:
            This report, allowing method chaining.

        Raises:
            TypeError: The input is not a Chart or resize has an invalid type.
            ValueError: The resize policy or width fraction is invalid.
        """
        return self._add_visual(chart, Chart, resize)

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

    def _write_text(self, composer: _PageComposer, block: _TextBlock) -> None:
        """Wrap text and render only the lines that fit the current page."""
        line_height = block.font_size * block.line_spacing
        if line_height > composer.content_height:
            message = "The printable page area is too small for report text."
            raise ValueError(message)
        lines = _wrap_lines(block.text, composer.content_width / 72, block.font)
        offset = 0
        while offset < len(lines):
            capacity = int((composer.remaining_height + 1e-6) / line_height)
            if capacity < 1:
                composer.new_page()
                capacity = int((composer.remaining_height + 1e-6) / line_height)
            chunk = lines[offset : offset + capacity]
            composer.add_pdf(
                _render_text(chunk, composer.content_width, block, self._theme),
                space_after=(
                    block.space_after if offset + len(chunk) == len(lines) else 0
                ),
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
                self._write_text(
                    composer,
                    _TextBlock(self.title, font_size=24, font_weight="bold"),
                )
            for element in self._elements:
                if element is None:
                    composer.request_break()
                elif isinstance(element, _TextBlock):
                    self._write_text(composer, element)
                else:
                    with BytesIO() as buffer:
                        with PdfPages(buffer) as pdf:
                            if isinstance(element.visual, Table):
                                self._write_table(pdf, element.visual)
                            else:
                                self._write_chart(pdf, element.visual)
                        composer.add_pdf(buffer.getvalue(), resize=element.resize)
            composer.save(path)
