"""Theme-aware scatter plotting using its matplotlib Axes method."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from tabloom.chart.plots.trendline import _add_trendline
from tabloom.validation.text import _check_text

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from tabloom.themes.theme import _Theme


def _plot_scatter(
    ax: Axes, x: Any, y: Any, theme: _Theme, options: dict[str, Any]
) -> None:
    """Draw points, optional numeric hue/colorbar, and a fitted association line."""
    options = dict(options)
    hue = options.pop("hue", None)
    colorbar = options.pop("colorbar", None)
    colorbar_label = options.pop("colorbar_label", None)
    trendline = options.pop("trendline", False)
    trendline_kwargs = options.pop("trendline_kwargs", None)
    if not isinstance(trendline, bool) or (
        colorbar is not None and not isinstance(colorbar, bool)
    ):
        message = "trendline and colorbar must be boolean (colorbar also accepts None)."
        raise TypeError(message)
    if trendline_kwargs is not None and not trendline:
        message = "trendline_kwargs requires trendline=True."
        raise ValueError(message)
    if hue is not None:
        if "c" in options or "color" in options:
            message = "hue cannot be combined with c or color."
            raise ValueError(message)
        values = np.asarray(hue, dtype=float)
        if values.ndim != 1 or len(values) != len(x) or not np.isfinite(values).all():
            message = "hue must contain one finite numeric value per point."
            raise ValueError(message)
        options["c"] = values
    show_colorbar = hue is not None if colorbar is None else colorbar
    if show_colorbar and hue is None:
        message = "colorbar requires numeric hue values."
        raise ValueError(message)
    if colorbar_label is not None:
        _check_text(colorbar_label)
        if not show_colorbar:
            message = "colorbar_label requires a visible colorbar."
            raise ValueError(message)
    defaults: dict[str, Any] = {
        "s": 44,
        "alpha": 0.85,
        "linewidths": 0.6,
        "edgecolors": theme.background,
    }
    if "c" not in options and "color" not in options:
        defaults["color"] = theme.palette[0]
    points = ax.scatter(x, y, **{**defaults, **options})
    if show_colorbar:
        bar = ax.figure.colorbar(points, ax=ax, pad=0.02, label=colorbar_label or "")
        bar.ax.yaxis.label.set_color(theme.foreground)
        bar.ax.tick_params(colors=theme.muted)
        bar.outline.set_edgecolor(theme.grid)
    if trendline:
        _add_trendline(ax, x, y, theme, dict(trendline_kwargs or {}))
