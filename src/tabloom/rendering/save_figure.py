"""PNG, PDF, and SVG output for an existing matplotlib figure."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from tabloom.validation.positive import _positive

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def _save_figure(
    fig: Figure,
    path: str | Path,
    *,
    dpi: float = 200,
    **kwargs: Any,
) -> None:
    """Validate output format and DPI, then save without closing the figure."""
    if Path(path).suffix.lower() not in {".png", ".pdf", ".svg"}:
        message = "Rendered output must use a .png, .pdf, or .svg extension."
        raise ValueError(message)
    _positive(dpi, "DPI")
    options = {"bbox_inches": "tight", "pad_inches": 0.15, **kwargs}
    fig.savefig(path, dpi=dpi, **options)
