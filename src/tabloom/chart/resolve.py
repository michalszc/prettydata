"""Resolve input vectors and named DataFrame columns without copying datasets."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pandas.api.types import is_list_like

if TYPE_CHECKING:
    import pandas as pd


def _resolve(value: Any, data: pd.DataFrame | None, name: str) -> Any:
    """Resolve a data column or validate a nonempty list-like input."""
    if isinstance(value, str) and data is not None:
        if value not in data.columns:
            message = f"Column {value!r} for {name} does not exist."
            raise KeyError(message)
        value = data[value]
    if isinstance(value, (str, bytes)) or not is_list_like(value):
        message = f"{name} must be a list, array, Series, or a column name with data."
        raise TypeError(message)
    if len(value) == 0:
        message = f"{name} must not be empty."
        raise ValueError(message)
    return value
