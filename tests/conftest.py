"""Headless plotting and figure cleanup for all feature tests."""

from collections.abc import Iterator

import matplotlib as mpl
import pytest

mpl.use("Agg")

import matplotlib.pyplot as plt


@pytest.fixture(autouse=True)
def close_figures() -> Iterator[None]:
    """Keep each test's figures isolated without opening graphical windows."""
    yield
    plt.close("all")
