"""Shared visual defaults and scoped rendering behavior."""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

from tabloom._rendering import _new_figure, _save_figure
from tabloom._themes import _get_theme


@pytest.mark.parametrize("name", ["default", "light", "dark"])
def test_theme_and_figure(name: str, tmp_path: Path) -> None:
    before = mpl.rcParams.copy()
    theme = _get_theme(name)
    fig, ax = _new_figure(theme, (6, 4))
    assert fig.get_size_inches().tolist() == [6, 4]
    assert ax.get_facecolor() == mpl.colors.to_rgba(theme.background)
    assert not ax.spines["top"].get_visible()
    for suffix in ("png", "pdf", "svg"):
        path = tmp_path / f"figure.{suffix}"
        _save_figure(fig, path)
        assert path.stat().st_size > 100
    assert plt.fignum_exists(fig.number)
    assert dict(mpl.rcParams) == dict(before)


def test_unknown_theme() -> None:
    with pytest.raises(ValueError, match="Unknown theme"):
        _get_theme("unknown")


@pytest.mark.parametrize("size", [(0, 4), (4, -1), (float("nan"), 4)])
def test_invalid_dimensions(size: tuple[float, float]) -> None:
    with pytest.raises(ValueError, match="positive"):
        _new_figure(_get_theme("default"), size)


def test_invalid_figure_arguments(tmp_path: Path) -> None:
    theme = _get_theme("default")
    with pytest.raises(ValueError, match="width and height"):
        _new_figure(theme, (4,))
    with pytest.raises(ValueError, match="Font size"):
        _new_figure(theme, (4, 4), fontsize=0)
    fig, _ = _new_figure(theme, (4, 4))
    with pytest.raises(ValueError, match="extension"):
        _save_figure(fig, tmp_path / "figure.txt")
    with pytest.raises(ValueError, match="DPI"):
        _save_figure(fig, tmp_path / "figure.png", dpi=0)
