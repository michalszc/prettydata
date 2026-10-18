"""Theme-aware bar plotting using its matplotlib Axes method."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from tabloom.themes.theme import _Theme
from matplotlib.cbook import normalize_kwargs
from matplotlib.patches import Patch


def _plot_bar(ax: Axes, x: Any, y: Any, theme: _Theme, options: dict[str, Any]) -> None:
    """Draw a bar chart on supplied axes, applying overridable theme defaults."""
    options = normalize_kwargs(options, Patch)
    ax.bar(
        x,
        y,
        **{
            "width": 0.7,
            "color": theme.palette[0],
            "edgecolor": theme.background,
            **options,
        },
    )
