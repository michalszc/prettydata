"""Validated typography for a single report text block."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal

from matplotlib.colors import to_rgba
from matplotlib.font_manager import FontProperties, findfont

from tabloom.validation.positive import _positive
from tabloom.validation.text import _check_text


@dataclass(frozen=True)
class _TextBlock:
    """Keep report text and its typography together without global style changes."""

    text: str
    font_family: str = "DejaVu Sans"
    font_size: float = 12
    font_weight: str | int = "normal"
    font_style: Literal["normal", "italic", "oblique"] = "normal"
    color: str | None = None
    align: Literal["left", "center", "right"] = "left"
    line_spacing: float = 1.5
    space_after: float = 12

    def __post_init__(self) -> None:
        """Reject invalid typography before appending content to a report."""
        _check_text(self.text)
        _check_text(self.font_family)
        _positive(self.font_size, "font_size")
        if not isfinite(self.line_spacing) or self.line_spacing < 1:
            message = "line_spacing must be finite and at least 1."
            raise ValueError(message)
        if not isfinite(self.space_after) or self.space_after < 0:
            message = "space_after must be finite and nonnegative."
            raise ValueError(message)
        if self.align not in {"left", "center", "right"}:
            message = "align must be left, center, or right."
            raise ValueError(message)
        if self.color is not None:
            to_rgba(self.color)
        findfont(self.font, fallback_to_default=False)

    @property
    def font(self) -> FontProperties:
        """Use the same font properties for measuring and rendering text."""
        return FontProperties(
            family=self.font_family,
            size=self.font_size,
            weight=self.font_weight,
            style=self.font_style,
        )
