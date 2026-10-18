"""Theme-aware scatter plotting using its matplotlib Axes method."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from tabloom.themes.theme import _Theme


def _plot_scatter(
    ax: Axes, x: Any, y: Any, theme: _Theme, options: dict[str, Any]
) -> None:
    """Draw a scatter chart on supplied axes, applying overridable theme defaults."""
    defaults: dict[str, Any] = {
        "s": 44,
        "alpha": 0.85,
        "linewidths": 0.6,
        "edgecolors": theme.background,
    }
    if "c" not in options and "color" not in options:
        defaults["color"] = theme.palette[0]
    ax.scatter(x, y, **{**defaults, **options})
