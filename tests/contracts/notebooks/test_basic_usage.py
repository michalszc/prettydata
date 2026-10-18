"""Execute the basic usage notebook and verify its saved rich outputs."""

import json
from pathlib import Path

import pytest
from matplotlib.figure import Figure
from pypdf import PdfReader

ROOT = Path(__file__).parents[3]


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
