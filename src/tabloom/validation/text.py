"""Validation of nonempty report titles and text sections."""

from __future__ import annotations

from typing import Any


def _check_text(value: Any) -> None:
    """Reject non-string values and text without visible non-whitespace content."""
    if not isinstance(value, str):
        message = "Text must be a string."
        raise TypeError(message)
    if not value.strip():
        message = "Text must not be empty or whitespace only."
        raise ValueError(message)
