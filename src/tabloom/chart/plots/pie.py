"""Theme-aware pie plotting using its matplotlib Axes method."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from tabloom.themes.theme import _Theme


def _plot_pie(ax: Axes, x: Any, theme: _Theme, options: dict[str, Any]) -> None:
    """Draw a pie chart on supplied axes, applying overridable theme defaults."""
    ax.pie(
        x,
        **{
            "colors": theme.palette,
            "startangle": 90,
            "wedgeprops": {"edgecolor": theme.background, "linewidth": 1},
            "textprops": {"color": theme.foreground, "fontfamily": "DejaVu Sans"},
            **options,
        },
    )
    ax.set_aspect("equal")
