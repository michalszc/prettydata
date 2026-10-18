"""Select a non-mutating table preview using pandas positional slicing."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def _select_rows(
    frame: pd.DataFrame, head: int | None, tail: int | None
) -> pd.DataFrame:
    """Return all rows or one validated head/tail preview without changing data."""
    if head is not None and tail is not None:
        message = "head and tail cannot be used together."
        raise ValueError(message)
    for name, count in (("head", head), ("tail", tail)):
        if count is not None:
            if isinstance(count, bool) or not isinstance(count, int):
                message = f"{name} must be a nonnegative integer."
                raise TypeError(message)
            if count < 0:
                message = f"{name} must be a nonnegative integer."
                raise ValueError(message)
    if head is not None:
        return frame.head(head)
    if tail is not None:
        return frame.tail(tail)
    return frame
