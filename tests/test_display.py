"""Targeted notebook display and optional-IPython graphical fallback."""

import builtins
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import IPython
import IPython.display
import pytest
from matplotlib.figure import Figure

from tabloom import Chart, Table


@pytest.mark.parametrize("as_table", [False, True])
def test_notebook_display_without_files(
    *, as_table: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    displayed: list[Figure] = []
    shown: list[Figure] = []
    unrelated = Chart.line([1, 2], [3, 4])
    visual = Table({"A": [1]}) if as_table else Chart.bar(["A"], [1])
    monkeypatch.setattr(
        IPython, "get_ipython", lambda: SimpleNamespace(kernel=object())
    )
    monkeypatch.setattr(IPython.display, "display", lambda fig: displayed.append(fig))
    monkeypatch.setattr(Figure, "show", lambda fig: shown.append(fig))
    visual.show()
    assert len(displayed) == 1
    assert displayed[0] is not unrelated.fig
    assert shown == []
    assert list(tmp_path.iterdir()) == []
    if isinstance(visual, Chart):
        assert displayed[0] is visual.fig
        visual.ax.set_title("Still reusable")
        assert visual.ax.get_title() == "Still reusable"


def test_graphical_display_without_ipython(monkeypatch: pytest.MonkeyPatch) -> None:
    chart = Chart.line([1, 2], [3, 4])
    shown: list[Figure] = []
    original = builtins.__import__

    def unavailable(name: str, *args: Any, **kwargs: Any) -> Any:
        if name.startswith("IPython"):
            message = "IPython is not installed"
            raise ImportError(message)
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", unavailable)
    monkeypatch.setattr(Figure, "show", lambda fig: shown.append(fig))
    chart.show()
    assert shown == [chart.fig]


def test_terminal_ipython_uses_graphical_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chart = Chart.line([1, 2], [3, 4])
    shown: list[Figure] = []
    monkeypatch.setattr(IPython, "get_ipython", lambda: SimpleNamespace())
    monkeypatch.setattr(Figure, "show", lambda fig: shown.append(fig))
    chart.show()
    assert shown == [chart.fig]
