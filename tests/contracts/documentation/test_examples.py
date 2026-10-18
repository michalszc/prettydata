"""Execute README and documentation examples in temporary directories."""

import re
from pathlib import Path

import pytest
from matplotlib.figure import Figure
from pypdf import PdfReader

ROOT = Path(__file__).parents[3]
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
