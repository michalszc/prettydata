"""Measure table text once for consistent standalone and paginated rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tabloom.rendering.text_size import _text_size
from tabloom.table.format_cell import _display

if TYPE_CHECKING:
    import pandas as pd

    from tabloom.table.style import _TableStyle


class _TableLayout:
    """Ephemeral display strings and measurements derived from the DataFrame."""

    def __init__(
        self,
        frame: pd.DataFrame,
        style: _TableStyle,
        title: str | None,
        figsize: tuple[float, float] | None,
    ) -> None:
        self.rows = [[str(col) for col in frame.columns]]
        self.rows.extend(
            [_display(value) for value in row]
            for row in frame.itertuples(index=False, name=None)
        )
        self.widths = [
            max(
                _text_size(row[col], style.font_size, "bold" if i == 0 else "normal")[0]
                for i, row in enumerate(self.rows)
            )
            for col in range(len(frame.columns))
        ]
        self.heights = [
            max((_text_size(cell, style.font_size)[1] for cell in row), default=0.5)
            for row in self.rows
        ]
        # Report rows reserve measured text height plus proportional padding.
        self.page_heights = [
            height - 14 / 72 + style.font_size * 0.6 / 72 for height in self.heights
        ]
        if style.column_widths is not None:
            if len(style.column_widths) != len(self.widths):
                message = "column_widths must match the number of columns."
                raise ValueError(message)
            total = sum(style.column_widths)
            fractions = [value / total for value in style.column_widths]
            required = max(
                (
                    width / fraction
                    for width, fraction in zip(self.widths, fractions, strict=True)
                ),
                default=0,
            )
            self.widths = [fraction * required for fraction in fractions]
        title_width = _text_size(title, style.font_size + 3)[0] if title else 0
        self.size = figsize or (
            max(3, sum(self.widths) + 0.5, title_width),
            max(1.2, sum(self.heights) + (0.7 if title else 0.3)),
        )
        self.page_padding = 0.3 + (
            _text_size(title, style.font_size + 3)[1] + 16 / 72 if title else 0
        )
        self.natural_height = sum(self.heights) + self.page_padding
