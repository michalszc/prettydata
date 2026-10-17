"""High-level factories for independently customizable matplotlib charts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.cbook import normalize_kwargs
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from pandas.api.types import is_list_like

from tabloom._rendering import _new_figure, _save_figure
from tabloom._themes import _get_theme
from tabloom.table import Table

if TYPE_CHECKING:
    from pathlib import Path

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from tabloom._themes import _Theme

_Kind = Literal["line", "bar", "scatter", "hist", "box", "pie"]


def _resolve(value: Any, data: pd.DataFrame | None, name: str) -> Any:
    if isinstance(value, str) and data is not None:
        if value not in data.columns:
            message = f"Column {value!r} for {name} does not exist."
            raise KeyError(message)
        value = data[value]
    if isinstance(value, (str, bytes)) or not is_list_like(value):
        message = f"{name} must be a list, array, Series, or a column name with data."
        raise TypeError(message)
    if len(value) == 0:
        message = f"{name} must not be empty."
        raise ValueError(message)
    return value


def _plot(  # noqa: PLR0913 - dispatch needs axes, data, theme, and plot options
    ax: Axes, kind: _Kind, x: Any, y: Any, theme: _Theme, options: dict[str, Any]
) -> None:
    """Set type-specific defaults while forwarding actual matplotlib options."""
    if kind == "line":
        options = normalize_kwargs(options, Line2D)
        ax.plot(x, y, **{"linewidth": 2.2, "markersize": 5, **options})
    elif kind == "bar":
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
    elif kind == "scatter":
        defaults: dict[str, Any] = {
            "s": 44,
            "alpha": 0.85,
            "linewidths": 0.6,
            "edgecolors": theme.background,
        }
        if "c" not in options and "color" not in options:
            defaults["color"] = theme.palette[0]
        ax.scatter(x, y, **{**defaults, **options})
    elif kind == "hist":
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
    elif kind == "box":
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
    else:
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


class Chart:
    """A matplotlib figure created by a convenient chart factory.

    Every factory accepts title, xlabel, ylabel, theme, figsize, and font_size.
    Additional keyword arguments go to its matplotlib plotting method. For
    column-based inputs, supply a pandas DataFrame or Tabloom Table as data.
    Use fig and ax to customize the result with normal matplotlib methods.
    """

    def __init__(self, fig: Figure, ax: Axes) -> None:
        """Store a Figure/Axes pair; normally use the chart factories."""
        self.fig = fig
        self.ax = ax

    @classmethod
    def line(cls, x: Any = None, y: Any = None, **kwargs: Any) -> Chart:
        """Plot x/y values or named data columns as lines.

        Example:
            ``Chart.line([1, 2, 3], [2, 5, 4], marker="o", title="Trend")``
        """
        return cls._create("line", x, y, **kwargs)

    @classmethod
    def bar(cls, x: Any = None, y: Any = None, **kwargs: Any) -> Chart:
        """Plot categories x and heights y as vertical bars."""
        return cls._create("bar", x, y, **kwargs)

    @classmethod
    def scatter(cls, x: Any = None, y: Any = None, **kwargs: Any) -> Chart:
        """Plot paired x/y observations; use s for size and c for color data."""
        return cls._create("scatter", x, y, **kwargs)

    @classmethod
    def hist(cls, x: Any = None, **kwargs: Any) -> Chart:
        """Plot a histogram of x values; accepts bins and other hist options."""
        return cls._create("hist", x, **kwargs)

    @classmethod
    def box(cls, x: Any = None, **kwargs: Any) -> Chart:
        """Plot x values or groups of values using matplotlib boxplot options."""
        return cls._create("box", x, **kwargs)

    @classmethod
    def pie(cls, x: Any = None, **kwargs: Any) -> Chart:
        """Plot nonnegative x values, optionally with labels or autopct.

        With data supplied, labels may also name a column in that dataset.
        """
        return cls._create("pie", x, **kwargs)

    @classmethod
    def _create(  # noqa: PLR0913 - shared factory presentation options
        cls,
        kind: _Kind,
        x: Any,
        y: Any = None,
        *,
        data: pd.DataFrame | Table | None = None,
        title: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        theme: str = "default",
        figsize: tuple[float, float] = (7, 4.5),
        font_size: float = 11,
        **kwargs: Any,
    ) -> Chart:
        visual = _get_theme(theme)
        frame: Any = data.df if isinstance(data, Table) else data
        if frame is not None:
            if not isinstance(frame, pd.DataFrame):
                message = "data must be a pandas DataFrame or Tabloom Table."
                raise TypeError(message)
            if not frame.columns.is_unique:
                message = "Chart data column names must be unique."
                raise ValueError(message)
        x = _resolve(x, frame, "x")
        if kind in {"line", "bar", "scatter"}:
            y = _resolve(y, frame, "y")
            if len(x) != len(y):
                message = "x and y must have the same length."
                raise ValueError(message)
        elif y is not None:
            message = f"{kind} accepts x values only; y is unsupported."
            raise TypeError(message)
        if kind == "pie" and kwargs.get("labels") is not None:
            kwargs["labels"] = _resolve(kwargs["labels"], frame, "labels")
            if len(kwargs["labels"]) != len(x):
                message = "Pie labels and values must have the same length."
                raise ValueError(message)
        fig, ax = _new_figure(visual, figsize, font_size)
        try:
            _plot(ax, kind, x, y, visual, kwargs)
            ax.set_title(
                title or "",
                fontsize=font_size + 3,
                color=visual.foreground,
                pad=14,
                fontfamily="DejaVu Sans",
                usetex=False,
            )
            ax.set_xlabel(
                xlabel or "",
                fontsize=font_size,
                color=visual.foreground,
                labelpad=8,
                fontfamily="DejaVu Sans",
                usetex=False,
            )
            ax.set_ylabel(
                ylabel or "",
                fontsize=font_size,
                color=visual.foreground,
                labelpad=8,
                fontfamily="DejaVu Sans",
                usetex=False,
            )
            if kind != "pie":
                ax.grid(
                    axis="y" if kind in {"bar", "hist", "box"} else "both",
                    color=visual.grid,
                    linewidth=0.7,
                    alpha=0.7,
                )
                ax.margins(x=0.05)
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(
                    handles,
                    labels,
                    fontsize=font_size,
                    facecolor=visual.background,
                    edgecolor=visual.grid,
                    labelcolor=visual.foreground,
                )
        except Exception:
            plt.close(fig)
            raise
        return cls(fig, ax)

    def show(self) -> None:
        """Display this figure using the active graphical backend."""
        self.fig.show()

    def save(self, path: str | Path, *, dpi: float = 200, **kwargs: Any) -> None:
        """Save PNG, PDF, or SVG while keeping the figure available for reuse."""
        _save_figure(self.fig, path, dpi=dpi, **kwargs)
