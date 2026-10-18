"""Validation of finite positive dimensions and font sizes."""

from __future__ import annotations

from math import isfinite


def _positive(value: float, name: str) -> None:
    """Raise ValueError unless value is finite and strictly positive."""
    if not isfinite(value) or value <= 0:
        message = f"{name} must be a finite positive number."
        raise ValueError(message)
