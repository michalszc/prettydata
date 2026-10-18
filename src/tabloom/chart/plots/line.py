"""Theme-aware line plotting using its matplotlib Axes method."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

from matplotlib.cbook import normalize_kwargs
from matplotlib.lines import Line2D


def _plot_line(ax: Axes, x: Any, y: Any, options: dict[str, Any]) -> None:
    """Draw a line chart on supplied axes, applying overridable theme defaults."""
    options = normalize_kwargs(options, Line2D)
    ax.plot(x, y, **{"linewidth": 2.2, "markersize": 5, **options})
