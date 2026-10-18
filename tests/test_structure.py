"""Library modules remain focused and document their individual responsibility."""

import ast
from pathlib import Path

import pytest

SOURCE = Path(__file__).parents[1] / "src" / "tabloom"


@pytest.mark.parametrize(
    "path", sorted(SOURCE.rglob("*.py")), ids=lambda path: str(path.relative_to(SOURCE))
)
def test_focused_documented_module(path: Path) -> None:
    tree = ast.parse(path.read_text())
    assert ast.get_docstring(tree), f"{path} needs a module docstring"
    definitions = [
        node
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert len(definitions) <= 1, f"{path} contains multiple top-level definitions"
    for definition in definitions:
        assert ast.get_docstring(definition), (
            f"{path}: {definition.name} needs documentation"
        )
