"""Report visual sizing preserves aspect ratio and caller-owned figures."""

from pathlib import Path
from typing import Any

import pytest
from pypdf import PdfReader

from tabloom import Chart, Report, Table
from tests.report.pdf_bounds import _block_bounds


@pytest.mark.parametrize("as_table", [False, True])
@pytest.mark.parametrize("resize", ["default", "full", 1, 0.5, "original"])
def test_visual_width_and_aspect_ratio(
    *, as_table: bool, resize: Any, tmp_path: Path
) -> None:
    visual: Any = (
        Table({"Name": ["A", "B"], "Score": [1, 2]})
        if as_table
        else Chart.bar(["A", "B"], [1, 2], figsize=(3, 2))
    )
    native_path = tmp_path / "native.pdf"
    report = Report(figsize=(8, 10), margin=0.5)
    add = report.add_table if as_table else report.add_chart
    add(visual, resize="original").save(native_path)
    native = _block_bounds(PdfReader(native_path).pages[0])[0]

    report = Report(figsize=(8, 10), margin=0.5)
    add = report.add_table if as_table else report.add_chart
    options = {} if resize == "default" else {"resize": resize}
    assert add(visual, **options) is report
    path = tmp_path / "sized.pdf"
    report.save(path)
    reader = PdfReader(path)
    assert len(reader.pages) == 1
    left, bottom, width, height = _block_bounds(reader.pages[0])[0]
    expected = (
        native[2] if resize == "original" else 504 * (0.5 if resize == 0.5 else 1)
    )
    assert width == pytest.approx(expected)
    assert width / height == pytest.approx(native[2] / native[3])
    assert left == pytest.approx((576 - width) / 2)
    assert bottom + height == pytest.approx(684)
    assert not reader.pages[0].images


def test_tall_visual_fits_height_and_leaves_source_unchanged(tmp_path: Path) -> None:
    chart = Chart.line([1, 2], [3, 4], figsize=(2, 12), title="Tall chart")
    original_size = chart.fig.get_size_inches().copy()
    original_position = chart.ax.get_position().bounds
    original_canvas = chart.fig.canvas
    path = tmp_path / "tall.pdf"
    Report(figsize=(6, 7), margin=0.5).add_text("BEFORE").add_chart(chart).save(path)
    reader = PdfReader(path)
    assert len(reader.pages) == 2
    left, bottom, width, height = _block_bounds(reader.pages[1])[0]
    assert height == pytest.approx(6 * 72)
    assert width < 5 * 72
    assert left > 36
    assert bottom == pytest.approx(36)
    assert chart.fig.get_size_inches().tolist() == original_size.tolist()
    assert chart.ax.get_position().bounds == pytest.approx(original_position)
    assert chart.fig.canvas is original_canvas


@pytest.mark.parametrize("as_table", [False, True])
@pytest.mark.parametrize(
    ("resize", "error"),
    [
        ("wide", ValueError),
        (0, ValueError),
        (-0.5, ValueError),
        (1.5, ValueError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (True, TypeError),
        (None, TypeError),
        ((3, 2), TypeError),
    ],
)
def test_invalid_resize_does_not_append_visual(
    *, as_table: bool, resize: Any, error: type[Exception], tmp_path: Path
) -> None:
    visual: Any = Table({"A": [1]}) if as_table else Chart.line([1, 2], [3, 4])
    report = Report()
    add = report.add_table if as_table else report.add_chart
    with pytest.raises(error, match="resize"):
        add(visual, resize=resize)
    with pytest.raises(ValueError, match="empty"):
        report.save(tmp_path / "empty.pdf")
