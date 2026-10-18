"""Create an owned, themed matplotlib figure with scoped configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib import rc_context

from tabloom.validation.positive import _positive

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from tabloom.themes.theme import _Theme


def _new_figure(
    theme: _Theme,
    figsize: tuple[float, ...],
    fontsize: float = 11,
) -> tuple[Figure, Axes]:
    """Create Figure/Axes without displaying them or retaining global style changes."""
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
    ax.tick_params(colors=theme.muted, labelsize=max(1, fontsize - 1))
    for spine in ax.spines.values():
        spine.set_color(theme.grid)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    return fig, ax
