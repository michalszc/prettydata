"""Invalid theme names fail with an actionable error."""

import pytest

from tabloom.themes.get_theme import _get_theme


@pytest.mark.parametrize("name", ["unknown", "default", "light", "dark"])
def test_unknown_theme(name: str) -> None:
    with pytest.raises(ValueError, match="Unknown theme"):
        _get_theme(name)
