"""Report text typography, spacing, validation, and pagination."""

from pathlib import Path
from typing import Any, Literal

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest
from pypdf import PdfReader

from tabloom import Report
from tests.report.pdf_bounds import _block_bounds


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
