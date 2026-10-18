"""High-level scatter coloring and descriptive association lines."""

from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from tabloom import Chart, Report, Table


@pytest.mark.parametrize("as_table", [False, True])
def test_named_hue_colorbar_and_trendline(*, as_table: bool, tmp_path: Path) -> None:
    frame = pd.DataFrame({"X": [1, 2, 3], "Y": [3, 5, 7], "Quality": [4, 6, 8]})
    data = Table(frame) if as_table else frame
    before = mpl.rcParams.copy()
    chart = Chart.scatter(data=data, x="X", y="Y", hue="Quality", trendline=True)
    assert len(chart.fig.axes) == 2
    assert chart.fig.axes[1].get_ylabel() == "Quality"
    np.testing.assert_array_equal(chart.ax.collections[0].get_array(), [4, 6, 8])
    np.testing.assert_allclose(
        np.asarray(chart.ax.lines[0].get_xdata(), dtype=float), [1.0, 3.0]
    )
    np.testing.assert_allclose(
        np.asarray(chart.ax.lines[0].get_ydata(), dtype=float), [3.0, 7.0]
    )
    legend = chart.ax.get_legend()
    assert legend is not None
    assert legend.texts[0].get_text() == "Linear association"
    original_positions = [ax.get_position().bounds for ax in chart.fig.axes]
    Report().add_chart(chart).save(tmp_path / "scatter.pdf")
    for ax, position in zip(chart.fig.axes, original_positions, strict=True):
        assert ax.get_position().bounds == pytest.approx(position)
    chart.save(tmp_path / "scatter.png")
    assert dict(mpl.rcParams) == dict(before)


def test_vector_hue_and_custom_labels() -> None:
    chart = Chart.scatter(
        [1, 2, 3],
        [4, 8, 12],
        hue=pd.Series([2, 3, 4]),
        colorbar_label="Score",
        trendline=True,
        trendline_kwargs={"color": "red", "label": "Fitted line", "linewidth": 3},
        theme="dark_blue",
    )
    assert chart.fig.axes[1].get_ylabel() == "Score"
    assert chart.ax.lines[0].get_color() == "red"
    assert chart.ax.lines[0].get_linewidth() == 3
    legend = chart.ax.get_legend()
    assert legend is not None
    assert legend.texts[0].get_text() == "Fitted line"


def test_disable_colorbar_and_ignore_nonfinite_trend_pairs() -> None:
    chart = Chart.scatter(
        [1, 2, 3, np.nan],
        [2, np.nan, 6, 9],
        hue=[1, 2, 3, 4],
        colorbar=False,
        trendline=True,
    )
    assert len(chart.fig.axes) == 1
    np.testing.assert_allclose(
        np.asarray(chart.ax.lines[0].get_ydata(), dtype=float), [2.0, 6.0]
    )
    frame = pd.DataFrame({"x": [1, 2], "y": [2, 4], "color": [1, 2]})
    chart = Chart.scatter(data=frame, x="x", y="y", hue="color", colorbar=False)
    assert len(chart.fig.axes) == 1


def test_vector_hue_without_label() -> None:
    chart = Chart.scatter([1, 2], [3, 4], hue=np.array([5, 6]))
    assert chart.fig.axes[1].get_ylabel() == ""


@pytest.mark.parametrize(
    ("options", "error", "match"),
    [
        ({"hue": [1]}, ValueError, "hue"),
        ({"hue": [[1, 2], [3, 4]]}, ValueError, "hue"),
        ({"hue": [1, np.nan]}, ValueError, "hue"),
        ({"hue": ["bad", "data"]}, ValueError, "convert"),
        ({"hue": [1, 2], "c": [2, 3]}, ValueError, "combined"),
        ({"hue": [1, 2], "color": "red"}, ValueError, "combined"),
        ({"colorbar": True}, ValueError, "hue"),
        ({"colorbar": "yes"}, TypeError, "boolean"),
        ({"trendline": 1}, TypeError, "boolean"),
        ({"trendline_kwargs": {"color": "red"}}, ValueError, "requires"),
        ({"colorbar_label": "Score"}, ValueError, "visible"),
        ({"hue": [1, 2], "colorbar_label": ""}, ValueError, "empty"),
    ],
)
def test_invalid_scatter_options_cleanup(
    options: dict[str, Any], error: type[Exception], match: str
) -> None:
    figures = plt.get_fignums()
    with pytest.raises(error, match=match):
        Chart.scatter([1, 2], [3, 4], **options)
    assert plt.get_fignums() == figures


@pytest.mark.parametrize(
    ("x", "y"),
    [([1], [2]), ([1, 1], [2, 3]), ([np.nan, 1], [2, np.inf]), ([[1, 2]], [[3, 4]])],
)
def test_invalid_trendline_data(x: Any, y: Any) -> None:
    figures = plt.get_fignums()
    with pytest.raises(ValueError, match="trendline"):
        Chart.scatter(x, y, trendline=True)
    assert plt.get_fignums() == figures


def test_missing_hue_column() -> None:
    with pytest.raises(KeyError, match="hue"):
        Chart.scatter(
            data=pd.DataFrame({"X": [1], "Y": [2]}), x="X", y="Y", hue="missing"
        )
