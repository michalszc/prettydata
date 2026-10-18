"""Library modules remain focused and document their individual responsibility."""

import ast
from pathlib import Path

import pytest

SOURCE = Path(__file__).parents[3] / "src" / "tabloom"


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


@pytest.mark.parametrize(
    "path",
    sorted(SOURCE.rglob("__init__.py")),
    ids=lambda path: str(path.parent.relative_to(SOURCE)),
)
def test_source_packages_have_matching_test_packages(path: Path) -> None:
    """New source packages need a matching, discoverable feature-test location."""
    relative = path.parent.relative_to(SOURCE)
    tests = Path(__file__).parents[2]
    assert (tests / relative / "__init__.py").is_file(), (
        f"Create tests/{relative}/__init__.py beside the new source package"
    )


@pytest.mark.parametrize(
    "path",
    sorted(SOURCE.rglob("__init__.py")),
    ids=lambda path: str(path.relative_to(SOURCE)),
)
def test_package_initializers_only_define_exports(path: Path) -> None:
    """Keep implementations in their own modules and initializers as import surfaces."""
    tree = ast.parse(path.read_text())
    assert not any(
        isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        for node in tree.body
    ), f"{path} should re-export its API rather than define implementations"
