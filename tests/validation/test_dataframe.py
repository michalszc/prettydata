"""DataFrame validation preserves identity and rejects ambiguous loader results."""

from typing import Any

import pandas as pd
import pytest

from tabloom.validation.dataframe import _dataframe


def test_dataframe_is_returned_without_copying() -> None:
    frame = pd.DataFrame({"Value": [1, 2]}, index=["a", "b"])
    assert _dataframe(frame) is frame


@pytest.mark.parametrize(
    "value", [None, [], {"Value": [1]}, {"Sheet1": pd.DataFrame()}, pd.Series([1])]
)
def test_non_frames_and_multisheet_results_are_rejected(value: Any) -> None:
    with pytest.raises(TypeError, match="single pandas DataFrame; select one sheet"):
        _dataframe(value)
