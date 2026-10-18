"""Content fills available report space before pagination, preserving order."""

from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from pypdf import PdfReader

from tabloom import Chart, Report, Table


def test_title_and_mixed_content_share_a_page(tmp_path: Path) -> None:
    path = tmp_path / "flow.pdf"
    table = Table({"Model": ["A", "B"], "Score": [85, 92]}, title="TABLE")
    chart = Chart.bar(data=table, x="Model", y="Score", title="CHART")
    Report("HEADING").add_text("INTRO").add_table(table, resize="original").add_chart(
        chart, resize="original"
    ).add_text("END").save(path)
    reader = PdfReader(path)
    assert len(reader.pages) == 1
    text = reader.pages[0].extract_text()
    positions = [
        text.index(label) for label in ("HEADING", "INTRO", "TABLE", "CHART", "END")
    ]
    assert positions == sorted(positions)
    assert len(reader.pages[0].images) == 0


def test_visual_moves_only_when_remaining_space_is_insufficient(tmp_path: Path) -> None:
    path = tmp_path / "overflow.pdf"
    chart = Chart.line([1, 2], [2, 3], title="CHART", figsize=(4, 2.5))
    report = Report(figsize=(6, 4.5), margin=0.5)
    report.add_text("INTRO\n" + "A line of text.\n" * 4)
    report.add_chart(chart, resize="original").add_text("AFTER")
    report.save(path)
    pages = [page.extract_text() for page in PdfReader(path).pages]
    assert len(pages) == 2
    assert "INTRO" in pages[0]
    assert "CHART" not in pages[0]
    assert "CHART" in pages[1]
    assert "AFTER" in pages[1]


def test_text_uses_space_below_a_visual_before_continuing(tmp_path: Path) -> None:
    path = tmp_path / "text-flow.pdf"
    report = Report(figsize=(6, 4), margin=0.5)
    report.add_table(Table({"A": [1]}, title="BEFORE"), resize="original")
    report.add_text("\n".join(f"Unique line {i:02d}" for i in range(10)))
    report.save(path)
    pages = [page.extract_text() for page in PdfReader(path).pages]
    assert len(pages) == 2
    assert "BEFORE" in pages[0]
    assert "Unique line 00" in pages[0]
    assert "Unique line 09" not in pages[0]
    assert "Unique line 09" in pages[1]
    combined = "".join(pages)
    for index in range(10):
        assert combined.count(f"Unique line {index:02d}") == 1


def test_multiple_small_visuals_share_space(tmp_path: Path) -> None:
    path = tmp_path / "visuals.pdf"
    table = Table({"A": [1]}, title="TABLE")
    chart = Chart.scatter([1, 2], [2, 3], title="CHART", figsize=(3, 2))
    Report().add_table(table, resize="original").add_chart(
        chart, resize="original"
    ).add_table(table, resize="original").save(path)
    reader = PdfReader(path)
    assert len(reader.pages) == 1
    text = reader.pages[0].extract_text()
    assert text.count("TABLE") == 2
    assert "CHART" in text


def test_explicit_breaks_do_not_create_blank_pages(tmp_path: Path) -> None:
    path = tmp_path / "breaks.pdf"
    report = Report()
    assert (
        report.add_page_break()
        .add_text("FIRST")
        .add_page_break()
        .add_page_break()
        .add_text("SECOND")
        .add_page_break()
        is report
    )
    report.save(path)
    pages = [page.extract_text() for page in PdfReader(path).pages]
    assert len(pages) == 2
    assert "FIRST" in pages[0]
    assert "SECOND" in pages[1]
    assert "SECOND" not in pages[0]


def test_explicit_cover_page(tmp_path: Path) -> None:
    path = tmp_path / "cover.pdf"
    Report("TITLE").add_page_break().add_text("BODY").save(path)
    pages = [page.extract_text() for page in PdfReader(path).pages]
    assert len(pages) == 2
    assert "TITLE" in pages[0]
    assert "BODY" not in pages[0]
    assert "BODY" in pages[1]


@pytest.mark.parametrize("extra", [False, True])
def test_exact_fit_text_has_no_extra_page(*, extra: bool, tmp_path: Path) -> None:
    path = tmp_path / "exact.pdf"
    report = Report(figsize=(4, 2), margin=0.5).add_text("A\nB\nC\nD")
    if extra:
        report.add_text("E")
    report.save(path)
    reader = PdfReader(path)
    assert len(reader.pages) == (2 if extra else 1)
    assert "D" in reader.pages[0].extract_text()
    if extra:
        assert "E" in reader.pages[1].extract_text()


def test_break_only_report_is_empty(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="empty"):
        Report().add_page_break().save(tmp_path / "empty.pdf")


def test_tiny_text_area_fails_without_leaking_figures(tmp_path: Path) -> None:
    before = plt.get_fignums()
    with pytest.raises(ValueError, match="too small"):
        Report(figsize=(1, 0.2), margin=0).add_text("Text").save(tmp_path / "tiny.pdf")
    assert plt.get_fignums() == before
