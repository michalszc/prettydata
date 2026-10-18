"""Head/tail display previews retain a table's complete underlying data."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from tabloom import Table

if TYPE_CHECKING:
    from matplotlib.figure import Figure


@pytest.mark.parametrize(
    ("options", "expected"),
    [
        ({}, list(range(10))),
        ({"head": 3}, [0, 1, 2]),
        ({"tail": 3}, [12, 13, 14]),
        ({"head": 0}, []),
        ({"tail": 0}, []),
        ({"head": 30}, list(range(15))),
    ],
)
def test_show_preview(
    options: dict[str, Any], expected: list[int], monkeypatch: pytest.MonkeyPatch
) -> None:
    frame = pd.DataFrame({"Value": range(15)}, index=range(100, 115))
    table = Table(frame)
    shown: list[Figure] = []
    monkeypatch.setattr("tabloom.table.table._show_figure", shown.append)
    table.show(**options)
    cells = shown[0].axes[0].tables[0].get_celld()
    assert [
        int(cell.get_text().get_text()) for (row, _), cell in cells.items() if row
    ] == expected
    assert_frame_equal(table.df, frame)


def test_render_defaults_to_complete_data_and_supports_tail() -> None:
    table = Table({"Value": range(15)})
    _, ax = table.render()
    assert len(ax.tables[0].get_celld()) == 16
    _, ax = table.render(tail=2)
    assert ax.tables[0][1, 0].get_text().get_text() == "13"
    assert ax.tables[0][2, 0].get_text().get_text() == "14"


@pytest.mark.parametrize(
    ("options", "error"),
    [
        ({"head": 10, "tail": 2}, ValueError),
        ({"head": -1}, ValueError),
        ({"tail": -1}, ValueError),
        ({"head": True}, TypeError),
        ({"tail": 2.5}, TypeError),
    ],
)
def test_invalid_preview(options: dict[str, Any], error: type[Exception]) -> None:
    table = Table({"Value": [1]})
    with pytest.raises(error, match=r"head|tail"):
        table.show(**options)
    with pytest.raises(error, match=r"head|tail"):
        table.render(**options)
