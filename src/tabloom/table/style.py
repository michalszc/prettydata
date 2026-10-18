"""Validated table-only visual overrides, independent of data and export."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from matplotlib.colors import to_rgba

from tabloom.validation.positive import _positive

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True)
class _TableStyle:
    """Optional cell colors, typography, alignment, and relative column widths."""

    header_background: str | None = None
    header_color: str | None = None
    row_colors: Sequence[str] | None = None
    font_size: float = 11
    cell_alignment: Literal["auto", "left", "center", "right"] = "auto"
    column_widths: Sequence[float] | None = None

    def __post_init__(self) -> None:
        """Validate overrides before any figure or table data is modified."""
        _positive(self.font_size, "Font size")
        if self.cell_alignment not in {"auto", "left", "center", "right"}:
            message = "cell_alignment must be auto, left, center, or right."
            raise ValueError(message)
        if self.row_colors is not None and len(self.row_colors) != 2:
            message = "row_colors must contain two alternating colors."
            raise ValueError(message)
        colors = [self.header_background, self.header_color]
        colors.extend(self.row_colors or ())
        for color in colors:
            if color is not None:
                to_rgba(color)
        for width in self.column_widths or ():
            _positive(width, "Column widths")
