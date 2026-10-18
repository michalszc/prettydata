"""Targeted notebook display and optional-IPython graphical fallback."""

import builtins
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import IPython
import IPython.display
import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

from tabloom import Chart, Report, Table


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
    assert not plt.fignum_exists(displayed[0].number)
    assert plt.fignum_exists(unrelated.fig.number)
    if isinstance(visual, Chart):
        assert displayed[0] is visual.fig
        visual.ax.set_title("Still reusable")
        assert visual.ax.get_title() == "Still reusable"
        visual.show()
        assert displayed == [visual.fig, visual.fig]
        visual.save(tmp_path / "reused.png")
        Report().add_chart(visual).save(tmp_path / "reused.pdf")
        assert (tmp_path / "reused.png").read_bytes().startswith(b"\x89PNG")
        assert (tmp_path / "reused.pdf").read_bytes().startswith(b"%PDF")


@pytest.mark.parametrize("as_table", [False, True])
def test_notebook_display_failure_cleans_up_registration(
    *, as_table: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    unrelated = Chart.line([1, 2], [3, 4])
    visual = Table({"A": [1]}) if as_table else Chart.bar(["A"], [1])
    monkeypatch.setattr(
        IPython, "get_ipython", lambda: SimpleNamespace(kernel=object())
    )

    def fail(fig: Figure) -> None:
        message = "Notebook display failed"
        raise RuntimeError(message)

    monkeypatch.setattr(IPython.display, "display", fail)
    with pytest.raises(RuntimeError, match="Notebook display failed"):
        visual.show()
    assert plt.get_fignums() == [unrelated.fig.number]
    if isinstance(visual, Chart):
        assert len(visual.ax.patches) == 1


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
    assert plt.fignum_exists(chart.fig.number)


def test_terminal_ipython_uses_graphical_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chart = Chart.line([1, 2], [3, 4])
    shown: list[Figure] = []
    monkeypatch.setattr(IPython, "get_ipython", lambda: SimpleNamespace())
    monkeypatch.setattr(Figure, "show", lambda fig: shown.append(fig))
    chart.show()
    assert shown == [chart.fig]
    assert plt.fignum_exists(chart.fig.number)
