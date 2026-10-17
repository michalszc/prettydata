"""Smoke tests for package imports and source metadata."""

import tomllib
from importlib.resources import files
from pathlib import Path

import prettydata

ROOT = Path(__file__).parents[3]


def test_package_import() -> None:
    """The minimal package can be imported from an editable installation."""
    assert prettydata.__name__ == "prettydata"


def test_package_version() -> None:
    """Runtime version and authors match the current source configuration."""
    # Editable-install metadata is a snapshot; read the current source metadata.
    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]

    assert prettydata.__version__ == project["version"]
    assert prettydata.__author__ == [author["name"] for author in project["authors"]]


def test_package_is_typed() -> None:
    """The PEP 561 marker is available as a package resource."""
    assert files("prettydata").joinpath("py.typed").is_file()
