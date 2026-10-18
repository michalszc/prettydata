"""Retain a reusable report visual and its validated width policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, cast

from tabloom.validation.positive import _positive

if TYPE_CHECKING:
    from tabloom.chart import Chart
    from tabloom.table import Table


@dataclass(frozen=True)
class _VisualBlock:
    """A visual reference sized to full width, a width fraction, or native size."""

    visual: Table | Chart
    resize: Literal["full", "original"] | float = "full"
    paginate: bool = False

    def __post_init__(self) -> None:
        """Validate width policies before modifying a report's element list."""
        if not isinstance(cast("object", self.paginate), bool):
            message = "paginate must be a boolean."
            raise TypeError(message)
        if isinstance(self.resize, str):
            if self.resize not in {"full", "original"}:
                message = "resize must be 'full', 'original', or a width fraction."
                raise ValueError(message)
        elif isinstance(self.resize, bool) or not isinstance(self.resize, (int, float)):
            message = "resize must be 'full', 'original', or a numeric width fraction."
            raise TypeError(message)
        else:
            _positive(self.resize, "resize")
            if self.resize > 1:
                message = "A resize width fraction must be at most 1."
                raise ValueError(message)
