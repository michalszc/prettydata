"""Display one owned figure using notebook rich output or a graphical backend."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def _show_figure(fig: Figure) -> None:
    """Display only fig, without saving a file or displaying unrelated figures.

    A running IPython kernel receives the Figure itself through its rich display
    protocol. Outside a notebook, use the figure's active graphical backend.
    IPython is optional and is never needed for saving or report generation.
    """
    try:
        # Notebook support is optional and loaded only when showing a figure.
        from IPython import get_ipython  # noqa: PLC0415
        from IPython.display import display  # noqa: PLC0415
    except ImportError:
        fig.show()
        return
    shell = get_ipython()
    if getattr(shell, "kernel", None) is not None:
        display(fig)
    else:
        fig.show()
