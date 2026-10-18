"""Convert DataFrame values into plain visible cell text."""

from __future__ import annotations

from typing import Any

import pandas as pd


def _display(value: Any) -> str:
    """Format missing scalars as empty cells and other values using str."""
    if pd.api.types.is_scalar(value) and pd.isna(value):
        return ""
    return str(value)
