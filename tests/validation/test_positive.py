"""Shared numeric dimensions and font sizes require finite positive values."""

import pytest

from tabloom.validation.positive import _positive


@pytest.mark.parametrize("value", [0.001, 1.0, 1000.0])
def test_positive_finite_values_are_accepted(value: float) -> None:
    _positive(value, "Width")


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), -float("inf")])
def test_invalid_numbers_name_the_failing_option(value: float) -> None:
    with pytest.raises(ValueError, match="Width must be a finite positive number"):
        _positive(value, "Width")
