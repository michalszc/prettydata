"""Smoke tests for the installed package and its metadata."""

import tomllib
from importlib.metadata import version
from importlib.resources import files
from pathlib import Path

import prettydata

ROOT = Path(__file__).parents[3]


def test_package_import() -> None:
    """The minimal package can be imported from an editable installation."""
    assert prettydata.__name__ == "prettydata"


def test_package_version() -> None:
    """Installed metadata and the initializer match the declared version."""
    with (ROOT / "pyproject.toml").open("rb") as stream:
        project = tomllib.load(stream)["project"]

    assert prettydata.__version__ == project["version"]
    assert version("prettydata") == project["version"]
    assert prettydata.__author__ == [author["name"] for author in project["authors"]]


def test_package_is_typed() -> None:
    """The PEP 561 marker is available as a package resource."""
    assert files("prettydata").joinpath("py.typed").is_file()
