"""Text validation accepts Unicode content and rejects empty/non-string values."""

from typing import Any

import pytest

from tabloom.validation.text import _check_text


@pytest.mark.parametrize("value", ["Report", " \n café \t", "東京\n大阪"])
def test_visible_text_is_accepted(value: str) -> None:
    _check_text(value)


@pytest.mark.parametrize("value", [None, 42, b"Text", ["Text"]])
def test_non_strings_raise_type_error(value: Any) -> None:
    with pytest.raises(TypeError, match="Text must be a string"):
        _check_text(value)


@pytest.mark.parametrize("value", ["", " \n\t"])
def test_whitespace_only_text_is_rejected(value: str) -> None:
    with pytest.raises(ValueError, match="empty or whitespace"):
        _check_text(value)
