"""Theme-aware box plotting using its matplotlib Axes method."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from tabloom.themes.theme import _Theme


def _plot_box(ax: Axes, x: Any, theme: _Theme, options: dict[str, Any]) -> None:
    """Draw a box chart on supplied axes, applying overridable theme defaults."""
    patch = options.get("patch_artist", True)
    boxprops = (
        {"facecolor": theme.palette[0], "edgecolor": theme.palette[0]}
        if patch
        else {"color": theme.palette[0]}
    )
    ax.boxplot(
        x,
        **{
            "patch_artist": True,
            "boxprops": boxprops,
            "medianprops": {"color": theme.foreground},
            "whiskerprops": {"color": theme.muted},
            "capprops": {"color": theme.muted},
            "flierprops": {"markeredgecolor": theme.muted},
            **options,
        },
    )
