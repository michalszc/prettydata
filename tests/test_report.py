"""Readable multipage reports, insertion order, pagination, and ownership."""

from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import pytest
from matplotlib.backends.backend_pdf import PdfPages
from pypdf import PdfReader

from tabloom import Chart, Report, Table


def test_empty_and_title_only(tmp_path: Path) -> None:
    path = tmp_path / "report.pdf"
    with pytest.raises(ValueError, match="empty"):
        Report().save(path)
    assert not path.exists()
    Report(title="Experiment Report").save(path)
    reader = PdfReader(path)
    assert len(reader.pages) == 1
    assert "Experiment Report" in reader.pages[0].extract_text()
    assert reader.metadata is not None
    assert reader.metadata.title == "Experiment Report"


@pytest.mark.parametrize("theme", ["default", "light", "dark"])
def test_composition_order_and_reuse(theme: str, tmp_path: Path) -> None:
    table = Table(
        {"Model": ["A", "B"], "Score": [85, 92]}, title="Table page", theme=theme
    )
    chart = Chart.bar(data=table, x="Model", y="Score", title="Chart page", theme=theme)
    canvas = chart.fig.canvas
    report = Report(title="Cover", theme=theme)
    assert (
        report.add_text("First text")
        .add_table(table)
        .add_chart(chart)
        .add_text("Last text")
        is report
    )
    table.df.loc[0, "Model"] = "Updated model"
    chart.ax.set_title("Updated chart")
    before = mpl.rcParams.copy()
    figures = plt.get_fignums()
    for name in ("report.pdf", "again.pdf"):
        path = tmp_path / name
        report.save(path)
        pages = [page.extract_text() for page in PdfReader(path).pages]
        assert len(pages) == 5
        assert "Cover" in pages[0]
        assert "First text" in pages[1]
        assert "Updated model" in pages[2]
        assert "Updated chart" in pages[3]
        assert "Last text" in pages[4]
        assert plt.get_fignums() == figures
        assert chart.fig.canvas is canvas
    assert dict(before) == dict(mpl.rcParams)
    chart.save(tmp_path / "chart.png")


def test_report_without_cover(tmp_path: Path) -> None:
    path = tmp_path / "text.pdf"
    Report().add_text("A text section\n\nWith a second paragraph").save(path)
    reader = PdfReader(path)
    assert len(reader.pages) == 1
    assert "second paragraph" in reader.pages[0].extract_text()


def test_long_text_and_long_words_paginate(tmp_path: Path) -> None:
    path = tmp_path / "long.pdf"
    text = "START\n" + "A line of report text.\n" * 100 + "W" * 300 + "\nEND"
    Report().add_text(text).save(path)
    reader = PdfReader(path)
    assert len(reader.pages) >= 3
    assert "START" in reader.pages[0].extract_text()
    assert "END" in reader.pages[-1].extract_text()
    contents = "".join(page.extract_text() for page in reader.pages)
    assert contents.count("W") == 300


@pytest.mark.parametrize("value", [None, 42, pd.DataFrame()])
def test_invalid_elements(value: Any) -> None:
    report = Report()
    with pytest.raises(TypeError, match="string"):
        report.add_text(value)
    with pytest.raises(TypeError, match="Table"):
        report.add_table(value)
    with pytest.raises(TypeError, match="Chart"):
        report.add_chart(value)


@pytest.mark.parametrize("text", ["", "  \n\t"])
def test_empty_text(text: str) -> None:
    with pytest.raises(ValueError, match="empty"):
        Report().add_text(text)
    with pytest.raises(ValueError, match="empty"):
        Report(title=text)


def test_invalid_format_and_theme(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="extension"):
        Report("Title").save(tmp_path / "report.png")
    with pytest.raises(ValueError, match="Unknown theme"):
        Report(theme="unknown")


@pytest.mark.parametrize("element", ["text", "table", "chart"])
def test_failure_cleanup(
    element: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    report = Report()
    if element == "text":
        report.add_text("Report text")
    elif element == "table":
        report.add_table(Table({"A": [1]}))
    else:
        report.add_chart(Chart.line([1, 2], [2, 3]))
    before = plt.get_fignums()

    def fail(*args: Any, **kwargs: Any) -> None:
        message = "PDF export failed"
        raise OSError(message)

    monkeypatch.setattr(PdfPages, "savefig", fail)
    with pytest.raises(OSError, match="PDF export failed"):
        report.save(tmp_path / "failure.pdf")
    assert plt.get_fignums() == before


def test_zero_width_text_and_long_cover(tmp_path: Path) -> None:
    path = tmp_path / "special.pdf"
    Report(title="I" * 600).add_text("\u200b").save(path)
    reader = PdfReader(path)
    assert len(reader.pages) >= 2
    assert "I" * 10 in reader.pages[0].extract_text()
