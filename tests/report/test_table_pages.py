"""Automatic table pagination repeats headers without mutating data or adding prose."""

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from matplotlib.backends.backend_pdf import PdfPages
from pandas.testing import assert_frame_equal
from pypdf import PdfReader

from tabloom import Report, Table


def test_long_table_fills_space_and_repeats_headers(tmp_path: Path) -> None:
    frame = pd.DataFrame(
        {"Record": [f"ID{i:03d}" for i in range(90)], "Value": range(90)}
    )
    table = Table(frame, title="Measurements", theme="blue")
    report = Report(figsize=(6, 5), margin=0.5).add_text("INTRO")
    report.add_table(table).add_text("AFTER")
    figures = plt.get_fignums()
    for name in ("first.pdf", "again.pdf"):
        path = tmp_path / name
        report.save(path)
        reader = PdfReader(path)
        assert len(reader.pages) > 2
        texts = [page.extract_text() for page in reader.pages]
        assert "INTRO" in texts[0]
        assert "ID000" in texts[0]
        assert "AFTER" in texts[-1]
        for page, text in zip(reader.pages, texts, strict=True):
            if "ID" in text:
                assert "Record" in text
                assert "Value" in text
                assert "Measurements" in text
                assert "Data appendix" not in text
                assert not page.images
        text = "\n".join(texts)
        for index in range(90):
            assert text.count(f"ID{index:03d}") == 1
        assert plt.get_fignums() == figures
    assert_frame_equal(table.df, frame)


def test_whole_table_fit_opt_out(tmp_path: Path) -> None:
    path = tmp_path / "fitted.pdf"
    Report(figsize=(6, 4), margin=0.5).add_table(
        Table({"Record": [f"ID{i:03d}" for i in range(60)]}), paginate=False
    ).save(path)
    reader = PdfReader(path)
    assert len(reader.pages) == 1
    assert "ID059" in reader.pages[0].extract_text()


def test_multiline_rows_and_oversized_single_row(tmp_path: Path) -> None:
    table = Table(
        {"Record": ["START", "HUGE", "END"], "Text": ["Short", "Long\n" * 60, "Done"]}
    )
    path = tmp_path / "multiline.pdf"
    Report(figsize=(6, 4), margin=0.5).add_table(table).save(path)
    reader = PdfReader(path)
    text = "\n".join(page.extract_text() for page in reader.pages)
    assert len(reader.pages) >= 3
    assert all(text.count(value) == 1 for value in ("START", "HUGE", "END"))
    assert text.count("Long") == 60


@pytest.mark.parametrize("resize", ["original", 0.6])
def test_pagination_respects_width_policies(resize: Any, tmp_path: Path) -> None:
    path = tmp_path / "sized.pdf"
    table = Table({"Record": [f"ID{i:03d}" for i in range(80)]})
    Report(figsize=(6, 5), margin=0.5).add_table(table, resize=resize).save(path)
    reader = PdfReader(path)
    assert len(reader.pages) > 1
    assert "ID079" in reader.pages[-1].extract_text()


def test_pagination_failure_releases_temporary_figures(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    table = Table({"Record": range(100)})
    figures = plt.get_fignums()

    def fail(*args: Any, **kwargs: Any) -> None:
        message = "Table PDF failed"
        raise OSError(message)

    monkeypatch.setattr(PdfPages, "savefig", fail)
    with pytest.raises(OSError, match="Table PDF failed"):
        Report().add_table(table).save(tmp_path / "failed.pdf")
    assert plt.get_fignums() == figures
    assert len(table.df) == 100


def test_invalid_paginate_is_atomic(tmp_path: Path) -> None:
    report = Report()
    with pytest.raises(TypeError, match="paginate"):
        report.add_table(Table({"Value": [1]}), paginate="yes")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="empty"):
        report.save(tmp_path / "empty.pdf")
