"""Figure creation and output helpers; never change global plot styles."""

from __future__ import annotations

from math import isfinite
from pathlib import Path
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
from matplotlib import rc_context

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from tabloom._themes import _Theme


def _positive(value: float, name: str) -> None:
    if not isfinite(value) or value <= 0:
        message = f"{name} must be a finite positive number."
        raise ValueError(message)


def _new_figure(
    theme: _Theme,
    figsize: tuple[float, ...],
    fontsize: float = 11,
) -> tuple[Figure, Axes]:
    if len(figsize) != 2:
        message = "figsize must contain width and height in inches."
        raise ValueError(message)
    for dimension in figsize:
        _positive(dimension, "Figure dimensions")
    _positive(fontsize, "Font size")
    with plt.ioff(), rc_context({"font.family": "DejaVu Sans", "text.usetex": False}):
        fig, ax = plt.subplots(figsize=(figsize[0], figsize[1]), layout="constrained")
    fig.set_facecolor(theme.background)
    ax.set_facecolor(theme.background)
    ax.set_prop_cycle(color=theme.palette)
    ax.tick_params(colors=theme.muted, labelsize=fontsize - 1)
    for spine in ax.spines.values():
        spine.set_color(theme.grid)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    return fig, ax


def _save_figure(
    fig: Figure,
    path: str | Path,
    *,
    dpi: float = 200,
    **kwargs: Any,
) -> None:
    if Path(path).suffix.lower() not in {".png", ".pdf", ".svg"}:
        message = "Rendered output must use a .png, .pdf, or .svg extension."
        raise ValueError(message)
    _positive(dpi, "DPI")
    options = {"bbox_inches": "tight", "pad_inches": 0.15, **kwargs}
    fig.savefig(path, dpi=dpi, **options)
