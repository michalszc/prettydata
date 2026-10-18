"""Chart factories, scoped styling, data resolution, and output lifecycle."""

from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure
from pandas.testing import assert_frame_equal
from pypdf import PdfReader

from tabloom import Chart, Table

FACTORIES = [Chart.line, Chart.bar, Chart.scatter, Chart.hist, Chart.box, Chart.pie]


@pytest.mark.parametrize("factory", FACTORIES)
@pytest.mark.parametrize("container", [list, np.array, pd.Series])
def test_factories_and_vector_inputs(factory: Any, container: Any) -> None:
    x = container([1, 2, 3])
    y = container([3, 5, 4])
    chart = (
        factory(x, y)
        if factory in (Chart.line, Chart.bar, Chart.scatter)
        else factory(x)
    )
    assert isinstance(chart.fig, Figure)
    assert isinstance(chart.ax, Axes)
    assert chart.ax.figure is chart.fig
    chart.fig.canvas.draw()
    chart.ax.set_title("Advanced customization")
    chart.ax.set_yscale("log")
    assert chart.ax.get_yscale() == "log"


@pytest.mark.parametrize("factory", FACTORIES)
@pytest.mark.parametrize("as_table", [False, True])
def test_dataframe_and_table_inputs(factory: Any, *, as_table: bool) -> None:
    frame = pd.DataFrame({"x": [1, 2, 3], "y": [3, 4, 5], "label": ["A", "B", "C"]})
    original = frame.copy()
    data = Table(frame, copy=False) if as_table else frame
    options = {"data": data, "x": "x"}
    if factory in (Chart.line, Chart.bar, Chart.scatter):
        options["y"] = "y"
    elif factory == Chart.pie:
        options["labels"] = "label"
    chart = factory(**options)
    chart.fig.canvas.draw()
    assert_frame_equal(frame, original)


@pytest.mark.parametrize("theme", ["blue", "soft_blue", "dark_blue"])
@pytest.mark.parametrize("factory", FACTORIES)
def test_themes_and_settings(factory: Any, theme: str) -> None:
    before = mpl.rcParams.copy()
    options = {
        "theme": theme,
        "figsize": (8, 5),
        "font_size": 12,
        "title": "Title",
        "xlabel": "X",
        "ylabel": "Y",
    }
    chart = (
        factory([1, 2], [3, 4], **options)
        if factory in (Chart.line, Chart.bar, Chart.scatter)
        else factory([1, 2], **options)
    )
    chart.fig.canvas.draw()
    assert chart.fig.get_size_inches().tolist() == [8, 5]
    assert chart.ax.get_title() == "Title"
    assert chart.ax.get_xlabel() == "X"
    assert chart.ax.get_ylabel() == "Y"
    assert chart.ax.xaxis.label.get_fontsize() == 12
    assert dict(before) == dict(mpl.rcParams)
    if theme == "dark_blue":
        assert chart.fig.get_facecolor() == mpl.colors.to_rgba("#18232e")


def test_customization_and_legend() -> None:
    chart = Chart.line(
        [1, 2], [3, 4], color="red", linewidth=4, marker="o", label="Run A"
    )
    line = chart.ax.lines[0]
    assert line.get_color() == "red"
    assert line.get_linewidth() == 4
    assert line.get_marker() == "o"
    assert chart.ax.get_legend() is not None
    aliases = Chart.line([1, 2], [2, 3], lw=3, c="green", ms=8)
    assert aliases.ax.lines[0].get_linewidth() == 3
    assert aliases.ax.lines[0].get_color() == "green"
    bar = Chart.bar(["A", "B"], [3, 4], color=["red", "blue"], width=0.5)
    assert bar.ax.patches[0].get_facecolor() == mpl.colors.to_rgba("red")
    scatter = Chart.scatter([1, 2], [3, 4], c=[0.2, 0.8], cmap="viridis", s=80)
    collection = scatter.ax.collections[0]
    assert isinstance(collection, PathCollection)
    assert collection.get_sizes().tolist() == [80]
    Chart.scatter([1, 2], [3, 4], color="red")
    hist = Chart.hist([1, 2, 3], bins=2)
    assert len(hist.ax.patches) == 2
    Chart.box([[1, 2, 3], [2, 3, 4]], tick_labels=["A", "B"], patch_artist=False)
    pie = Chart.pie(
        [1, 2], labels=["A", "B"], colors=["red", "blue"], autopct="%1.0f%%"
    )
    assert pie.ax.patches[0].get_facecolor() == mpl.colors.to_rgba("red")


@pytest.mark.parametrize(
    ("factory", "kwargs", "error", "match"),
    [
        (Chart.line, {}, TypeError, "x must"),
        (Chart.line, {"x": [1]}, TypeError, "y must"),
        (Chart.line, {"x": [1], "y": [1, 2]}, ValueError, "same length"),
        (Chart.hist, {"x": []}, ValueError, "empty"),
        (Chart.hist, {"x": "value"}, TypeError, "column name"),
        (Chart.hist, {"x": [1], "data": []}, TypeError, "DataFrame"),
        (
            Chart.hist,
            {"data": pd.DataFrame({"x": [1]}), "x": "absent"},
            KeyError,
            "does not exist",
        ),
        (
            Chart.hist,
            {"x": [1], "data": pd.DataFrame([[1, 2]], columns=["x", "x"])},
            ValueError,
            "unique",
        ),
        (Chart.hist, {"x": [1], "y": [2]}, TypeError, "unsupported"),
        (Chart.pie, {"x": [1, 2], "labels": ["A"]}, ValueError, "same length"),
        (Chart.pie, {"x": [-1, 2]}, ValueError, "negative"),
        (
            Chart.line,
            {"x": [1], "y": [2], "theme": "unknown"},
            ValueError,
            "Unknown theme",
        ),
        (Chart.bar, {"x": [1], "y": [2], "bogus": 1}, AttributeError, "bogus"),
        (Chart.box, {"x": [1, 2], "bogus": 1}, TypeError, "bogus"),
        (Chart.hist, {"x": [1], "figsize": (0, 2)}, ValueError, "positive"),
    ],
)
def test_invalid_input_cleanup(
    factory: Any, kwargs: dict[str, Any], error: type[Exception], match: str
) -> None:
    before = plt.get_fignums()
    with pytest.raises(error, match=match):
        factory(**kwargs)
    assert plt.get_fignums() == before


@pytest.mark.parametrize("extension", ["png", "pdf", "svg"])
def test_save_and_reuse(extension: str, tmp_path: Path) -> None:
    chart = Chart.line(
        [1, 2], [3, 4], title="Saved chart", xlabel="Time", ylabel="Score"
    )
    path = tmp_path / f"chart.{extension}"
    chart.save(path, dpi=120)
    assert path.stat().st_size > 100
    if extension == "pdf":
        text = PdfReader(path).pages[0].extract_text()
        assert all(label in text for label in ("Saved chart", "Time", "Score"))
    elif extension == "png":
        assert path.read_bytes().startswith(b"\x89PNG")
    else:
        assert "<svg" in path.read_text()
    assert plt.fignum_exists(chart.fig.number)
    chart.ax.set_title("Changed")
    chart.save(path)
    assert chart.ax.get_title() == "Changed"


def test_show_and_no_implicit_display(monkeypatch: pytest.MonkeyPatch) -> None:
    shown: list[Figure] = []
    monkeypatch.setattr(Figure, "show", lambda fig: shown.append(fig))
    plt.ion()
    try:
        chart = Chart.bar(["A"], [2])
        assert shown == []
        assert plt.isinteractive()
        chart.show()
        assert shown == [chart.fig]
    finally:
        plt.ioff()


def test_matplotlib_failure_preserves_settings() -> None:
    before = mpl.rcParams.copy()
    with pytest.raises(ValueError, match="color"):
        Chart.line([1, 2], [2, 3], color="not-a-color")
    assert dict(before) == dict(mpl.rcParams)
