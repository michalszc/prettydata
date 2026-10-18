"""Report typography and width policies survive export as vector PDF content."""

from pathlib import Path
from typing import Any, Literal

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest
from pypdf import PageObject, PdfReader

from tabloom import Chart, Report, Table


def _block_bounds(page: PageObject) -> list[tuple[float, float, float, float]]:
    """Read the actual page-space clipping rectangles of merged vector blocks."""
    contents = page.get_contents()
    assert contents is not None
    operations = contents.operations
    bounds = []
    for index, (matrix, operator) in enumerate(operations[:-2]):
        rectangle, next_operator = operations[index + 1]
        if (
            operator == b"cm"
            and next_operator == b"re"
            and operations[index + 2][1] == b"W"
        ):
            bounds.append(
                (
                    float(matrix[4]),
                    float(matrix[5]),
                    float(matrix[0]) * float(rectangle[2]),
                    float(matrix[3]) * float(rectangle[3]),
                )
            )
    return bounds


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


@pytest.mark.parametrize("align", ["left", "center", "right"])
def test_text_typography_and_alignment(
    align: Literal["left", "center", "right"], tmp_path: Path
) -> None:
    path = tmp_path / "styled.pdf"
    before = mpl.rcParams.copy()
    figures = plt.get_fignums()
    report = Report(theme="dark_blue", figsize=(6, 5), margin=0.5)
    assert (
        report.add_text(
            "Styled text",
            font_family="DejaVu Serif",
            font_size=18,
            font_weight=700,
            font_style="italic",
            color="#c0392b",
            align=align,
            line_spacing=2,
            space_after=20,
        )
        is report
    )
    report.add_text("NEXT").save(path)
    page = PdfReader(path).pages[0]
    segments: list[tuple[float, str, float]] = []

    def visit(text: str, cm: Any, tm: Any, font: Any, font_size: float) -> None:
        if "Styled text" in text:
            x = float(cm[0]) * float(tm[4]) + float(cm[4]) - 36
            segments.append((x, str(font["/BaseFont"]), font_size))

    page.extract_text(visitor_text=visit)
    x, font_name, font_size = segments[0]
    assert "DejaVuSerif-BoldItalic" in font_name
    assert font_size == 18
    if align == "left":
        assert x == pytest.approx(0)
    elif align == "center":
        assert 0 < x < 180
    else:
        assert 180 < x < 360
    contents = page.get_contents()
    assert contents is not None
    colors = [values for values, operator in contents.operations if operator == b"rg"]
    assert any(
        [float(value) for value in color]
        == pytest.approx([192 / 255, 57 / 255, 43 / 255])
        for color in colors
    )
    assert "NEXT" in page.extract_text()
    assert not page.images
    assert plt.get_fignums() == figures
    assert dict(mpl.rcParams) == dict(before)


def test_font_size_and_spacing_drive_pagination(tmp_path: Path) -> None:
    path = tmp_path / "spaced.pdf"
    text = "\n".join(f"Line {index}" for index in range(7))
    Report(figsize=(6, 4), margin=0.5).add_text(
        text, font_size=18, line_spacing=2, space_after=0
    ).save(path)
    pages = [page.extract_text() for page in PdfReader(path).pages]
    assert len(pages) == 2
    assert "Line 5" in pages[0]
    assert "Line 6" not in pages[0]
    assert "Line 6" in pages[1]
    assert "".join(pages).count("Line") == 7


@pytest.mark.parametrize("space_after", [0, 36])
def test_space_after_moves_following_content(
    space_after: float, tmp_path: Path
) -> None:
    path = tmp_path / "spacing.pdf"
    Report(figsize=(6, 5), margin=0.5).add_text(
        "FIRST", space_after=space_after
    ).add_text("SECOND").save(path)
    bounds = _block_bounds(PdfReader(path).pages[0])
    assert bounds[0][1] - (bounds[1][1] + bounds[1][3]) == pytest.approx(space_after)


def test_custom_font_wraps_and_saves_repeatedly(tmp_path: Path) -> None:
    report = Report(figsize=(3, 4), margin=0.5).add_text(
        "W" * 240, font_family="DejaVu Sans Mono", font_size=16, line_spacing=1.25
    )
    for name in ("first.pdf", "again.pdf"):
        path = tmp_path / name
        report.save(path)
        reader = PdfReader(path)
        assert len(reader.pages) > 1
        assert "".join(page.extract_text() for page in reader.pages).count("W") == 240


@pytest.mark.parametrize(
    "options",
    [
        {"font_family": ""},
        {"font_family": "ThisFontDoesNotExistInTabloom"},
        {"font_size": 0},
        {"font_size": float("nan")},
        {"font_weight": "not-a-weight"},
        {"font_style": "not-a-style"},
        {"color": "not-a-color"},
        {"align": "justify"},
        {"line_spacing": 0.9},
        {"line_spacing": float("nan")},
        {"space_after": -1},
        {"space_after": float("inf")},
    ],
)
def test_invalid_text_style_is_atomic(options: dict[str, Any], tmp_path: Path) -> None:
    report = Report()
    with pytest.raises(
        ValueError,
        match=r"empty|font|weight|style|color|align|line_spacing|space_after",
    ):
        report.add_text("INVALID", **options)
    path = tmp_path / "valid.pdf"
    report.add_text("VALID").save(path)
    text = PdfReader(path).pages[0].extract_text()
    assert "VALID" in text
    assert "INVALID" not in text
