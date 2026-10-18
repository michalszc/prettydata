"""Theme-aware hist plotting using its matplotlib Axes method."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from tabloom.themes.theme import _Theme
from matplotlib.cbook import normalize_kwargs
from matplotlib.patches import Patch


def _plot_hist(ax: Axes, x: Any, theme: _Theme, options: dict[str, Any]) -> None:
    """Draw a hist chart on supplied axes, applying overridable theme defaults."""
    options = normalize_kwargs(options, Patch)
    ax.hist(
        x,
        **{
            "bins": "auto",
            "color": theme.palette[0],
            "edgecolor": theme.background,
            "linewidth": 0.8,
            **options,
        },
    )
