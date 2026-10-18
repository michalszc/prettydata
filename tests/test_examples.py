"""Execute user-facing examples in isolated temporary directories."""

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure
from pypdf import PdfReader

from tabloom import Chart, Report, Table

ROOT = Path(__file__).parents[1]
DOCUMENTS = [
    path
    for path in [ROOT / "README.md", *sorted((ROOT / "documentation").rglob("*.md"))]
    if "```python\n" in path.read_text()
]


@pytest.mark.parametrize(
    "document", DOCUMENTS, ids=lambda path: str(path.relative_to(ROOT))
)
def test_document_examples(
    document: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Figure, "show", lambda fig: None)
    for example in re.findall(r"```python\n(.*?)```", document.read_text(), re.DOTALL):
        exec(compile(example, str(document), "exec"), {})
    for path in tmp_path.glob("*.pdf"):
        assert len(PdfReader(path).pages) > 0
    if document.name == "README.md":
        assert (tmp_path / "results.png").read_bytes().startswith(b"\x89PNG")
        assert (tmp_path / "comparison.png").read_bytes().startswith(b"\x89PNG")
        assert len(PdfReader(tmp_path / "experiment_report.pdf").pages) == 2


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


def test_notebook_code(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Figure, "show", lambda fig: None)
    notebook = json.loads((ROOT / "notebooks" / "basic_usage.ipynb").read_text())
    rich_outputs = [
        output
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
        for output in cell["outputs"]
        if output["output_type"] == "display_data" and "image/png" in output["data"]
    ]
    assert len(rich_outputs) == 2
    namespace: dict[str, object] = {}
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            assert "plt.close" not in source
            exec(compile(source, "basic_usage.ipynb", "exec"), namespace)
    assert len(PdfReader("experiment_report.pdf").pages) == 2
