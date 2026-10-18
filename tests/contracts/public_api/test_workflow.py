"""Exercise the documented table-to-chart-to-report workflow."""

from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure
from pypdf import PdfReader

from tabloom import Chart, Report, Table


def test_requested_workflow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Figure, "show", lambda fig: None)
    table = Table(columns=["Model", "Accuracy"])
    table.add_row(["Model A", 0.85])
    table.add_row(["Model B", 0.91])
    table.add_row(["Model C", 0.88])
    table.save("results.png")
    chart = Chart.bar(
        data=table, x="Model", y="Accuracy", title="Model Comparison", ylabel="Accuracy"
    )
    chart.save("comparison.png")
    report = Report(title="Experiment Report")
    report.add_text("Comparison of machine learning models.")
    report.add_table(table)
    report.add_chart(chart)
    report.save("experiment_report.pdf")
    reader = PdfReader("experiment_report.pdf")
    assert len(reader.pages) == 2
    assert "Model A" in reader.pages[0].extract_text()
    assert "Model Comparison" in reader.pages[1].extract_text()
    assert plt.fignum_exists(chart.fig.number)
