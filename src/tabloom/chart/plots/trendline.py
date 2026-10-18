"""Draw a descriptive linear association using finite numeric scatter pairs."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from tabloom.themes.theme import _Theme


def _add_trendline(
    ax: Axes, x: Any, y: Any, theme: _Theme, options: dict[str, Any]
) -> None:
    """Fit a centered least-squares line without SciPy or global configuration."""
    x_values, y_values = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x_values.ndim != 1 or y_values.ndim != 1:
        message = "trendline requires one-dimensional numeric x and y values."
        raise ValueError(message)
    finite = np.isfinite(x_values) & np.isfinite(y_values)
    x_values, y_values = x_values[finite], y_values[finite]
    if len(x_values) < 2 or np.ptp(x_values) == 0:
        message = "trendline requires at least two finite pairs with distinct x values."
        raise ValueError(message)
    centered = x_values - x_values.mean()
    slope = np.dot(centered, y_values - y_values.mean()) / np.dot(centered, centered)
    endpoints = np.array([x_values.min(), x_values.max()])
    fitted = y_values.mean() + slope * (endpoints - x_values.mean())
    ax.plot(
        endpoints,
        fitted,
        **{
            "color": theme.foreground,
            "linestyle": "--",
            "linewidth": 1.5,
            "label": "Linear association",
            **options,
        },
    )
