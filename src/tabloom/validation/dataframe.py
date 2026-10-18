"""Require a single DataFrame from data loaders."""

from __future__ import annotations

from typing import Any

import pandas as pd


def _dataframe(value: Any) -> pd.DataFrame:
    """Return a DataFrame, rejecting other inputs and multisheet Excel results."""
    if not isinstance(value, pd.DataFrame):
        message = (
            "Expected a single pandas DataFrame; select one sheet for Excel input."
        )
        raise TypeError(message)
    return value
