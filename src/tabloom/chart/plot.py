"""Dispatch chart kinds to independent matplotlib renderers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tabloom.chart.plots.bar import _plot_bar
from tabloom.chart.plots.box import _plot_box
from tabloom.chart.plots.hist import _plot_hist
from tabloom.chart.plots.line import _plot_line
from tabloom.chart.plots.pie import _plot_pie
from tabloom.chart.plots.scatter import _plot_scatter

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from tabloom.chart.types import _Kind
    from tabloom.themes.theme import _Theme


def _plot(  # noqa: PLR0913 - delegate paired and unpaired chart vectors
    ax: Axes, kind: _Kind, x: Any, y: Any, theme: _Theme, options: dict[str, Any]
) -> None:
    """Delegate to the single-purpose renderer for the selected chart kind."""
    if kind == "line":
        _plot_line(ax, x, y, options)
    elif kind == "bar":
        _plot_bar(ax, x, y, theme, options)
    elif kind == "scatter":
        _plot_scatter(ax, x, y, theme, options)
    elif kind == "hist":
        _plot_hist(ax, x, theme, options)
    elif kind == "box":
        _plot_box(ax, x, theme, options)
    else:
        _plot_pie(ax, x, theme, options)
