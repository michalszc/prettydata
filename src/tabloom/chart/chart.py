"""Public chart factories, matplotlib access, display, and graphical export."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import pandas as pd

from tabloom.chart.plot import _plot
from tabloom.chart.resolve import _resolve
from tabloom.rendering.new_figure import _new_figure
from tabloom.rendering.save_figure import _save_figure
from tabloom.rendering.show_figure import _show_figure
from tabloom.table import Table
from tabloom.themes.get_theme import _get_theme

if TYPE_CHECKING:
    from pathlib import Path

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from tabloom.chart.types import _Kind


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
        """Create lines from vectors or named data columns.

        Args:
            x: X values or category labels, or a column name when data is supplied.
            y: Y values, bar heights, or a column name; must match the x length.
            **kwargs: Common factory options (data, title, xlabel, ylabel, theme,
                figsize, font_size) and matplotlib plotting options. Use color,
                linewidth, marker, and label to customize lines.

        Returns:
            A Chart exposing its Figure and Axes through fig and ax.

        Raises:
            TypeError: The input type or a plotting option is unsupported.
            ValueError: Input lengths, dimensions, theme, or numeric values are invalid.
            KeyError: A requested data column does not exist.
        """
        return cls._create("line", x, y, **kwargs)

    @classmethod
    def bar(cls, x: Any = None, y: Any = None, **kwargs: Any) -> Chart:
        """Create vertical bars from vectors or named data columns.

        Args:
            x: X values or category labels, or a column name when data is supplied.
            y: Y values, bar heights, or a column name; must match the x length.
            **kwargs: Common factory options (data, title, xlabel, ylabel, theme,
                figsize, font_size) and matplotlib plotting options. Use color
                and width to customize bars.

        Returns:
            A Chart exposing its Figure and Axes through fig and ax.

        Raises:
            TypeError: The input type or a plotting option is unsupported.
            ValueError: Input lengths, dimensions, theme, or numeric values are invalid.
            KeyError: A requested data column does not exist.
        """
        return cls._create("bar", x, y, **kwargs)

    @classmethod
    def scatter(cls, x: Any = None, y: Any = None, **kwargs: Any) -> Chart:
        """Create scatter points from vectors or named data columns.

        Args:
            x: X values or category labels, or a column name when data is supplied.
            y: Y values, bar heights, or a column name; must match the x length.
            **kwargs: Common factory options (data, title, xlabel, ylabel, theme,
                figsize, font_size) and matplotlib plotting options. Use s for
                point size and c for numeric color values.

        Returns:
            A Chart exposing its Figure and Axes through fig and ax.

        Raises:
            TypeError: The input type or a plotting option is unsupported.
            ValueError: Input lengths, dimensions, theme, or numeric values are invalid.
            KeyError: A requested data column does not exist.
        """
        return cls._create("scatter", x, y, **kwargs)

    @classmethod
    def hist(cls, x: Any = None, **kwargs: Any) -> Chart:
        """Create a histogram from vectors or named data columns.

        Args:
            x: Values or groups of values, or a column name when data is supplied.
            **kwargs: Common factory options (data, title, xlabel, ylabel, theme,
                figsize, font_size) and matplotlib plotting options. Use bins
                and density to configure the histogram.

        Returns:
            A Chart exposing its Figure and Axes through fig and ax.

        Raises:
            TypeError: The input type or a plotting option is unsupported.
            ValueError: Input lengths, dimensions, theme, or numeric values are invalid.
            KeyError: A requested data column does not exist.
        """
        return cls._create("hist", x, **kwargs)

    @classmethod
    def box(cls, x: Any = None, **kwargs: Any) -> Chart:
        """Create box plots from vectors or named data columns.

        Args:
            x: Values or groups of values, or a column name when data is supplied.
            **kwargs: Common factory options (data, title, xlabel, ylabel, theme,
                figsize, font_size) and matplotlib plotting options. Use
                tick_labels, boxprops, and medianprops for grouped distributions.

        Returns:
            A Chart exposing its Figure and Axes through fig and ax.

        Raises:
            TypeError: The input type or a plotting option is unsupported.
            ValueError: Input lengths, dimensions, theme, or numeric values are invalid.
            KeyError: A requested data column does not exist.
        """
        return cls._create("box", x, **kwargs)

    @classmethod
    def pie(cls, x: Any = None, **kwargs: Any) -> Chart:
        """Create a pie chart from vectors or named data columns.

        Args:
            x: Values or groups of values, or a column name when data is supplied.
            **kwargs: Common factory options (data, title, xlabel, ylabel, theme,
                figsize, font_size) and matplotlib plotting options. Use labels
                or a labels column name, colors, and autopct for wedge annotations.

        Returns:
            A Chart exposing its Figure and Axes through fig and ax.

        Raises:
            TypeError: The input type or a plotting option is unsupported.
            ValueError: Input lengths, dimensions, theme, or numeric values are invalid.
            KeyError: A requested data column does not exist.
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
        theme: str = "blue",
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
        """Display this chart directly in a notebook or graphical backend.

        Notebook output uses the existing Figure without saving an image file.
        Pyplot registration is cleaned up automatically after notebook display.
        Only this chart is displayed, and its figure remains available for
        customization, saving, and reuse in reports.
        """
        _show_figure(self.fig)

    def save(self, path: str | Path, *, dpi: float = 200, **kwargs: Any) -> None:
        """Save PNG, PDF, or SVG without closing the chart.

        Args:
            path: Destination filename with a supported graphical extension.
            dpi: Positive raster resolution in dots per inch.
            **kwargs: Additional matplotlib Figure.savefig options.

        Raises:
            ValueError: The output extension or DPI is invalid.

        The chart remains available for display, customization, and report composition.
        """
        _save_figure(self.fig, path, dpi=dpi, **kwargs)
