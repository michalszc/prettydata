"""Table data contracts, pandas I/O, styling, and rendered output."""

from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure
from pandas.testing import assert_frame_equal
from pypdf import PdfReader

from tabloom import Table


def test_default_table_is_plain_black_and_white() -> None:
    """Default construction needs no styling arguments to produce a plain table."""
    table = Table({"Name": ["Alice", "Bob"], "Score": [85, 92]}, title="Results")
    before = mpl.rcParams.copy()
    fig, ax = table.render()
    assert fig.get_facecolor() == mpl.colors.to_rgba("white")
    assert mpl.colors.to_rgba(ax.title.get_color()) == mpl.colors.to_rgba("black")
    for cell in ax.tables[0].get_celld().values():
        assert cell.get_facecolor() == mpl.colors.to_rgba("white")
        assert cell.get_edgecolor() == mpl.colors.to_rgba("black")
        assert mpl.colors.to_rgba(cell.get_text().get_color()) == mpl.colors.to_rgba(
            "black"
        )
    assert dict(mpl.rcParams) == dict(before)


@pytest.mark.parametrize(
    "data",
    [
        {"Name": ["Alice"], "Score": [85]},
        [{"Name": "Alice", "Score": 85}],
        pd.DataFrame({"Name": ["Alice"], "Score": [85]}),
    ],
)
def test_construction(data: Any) -> None:
    assert_frame_equal(Table(data).df, pd.DataFrame({"Name": ["Alice"], "Score": [85]}))


def test_rows_and_empty_construction() -> None:
    assert Table().df.empty
    assert list(Table(columns=["A", "B"]).df.columns) == ["A", "B"]
    assert Table([[1, 2]], columns=["A", "B"]).df.iloc[0].tolist() == [1, 2]
    with pytest.raises(ValueError, match="Provide columns"):
        Table([[1, 2]])
    with pytest.raises(ValueError, match="unique"):
        Table(columns=["A", "A"])
    with pytest.raises(TypeError, match="DataFrame"):
        Table.from_dataframe([])  # type: ignore[arg-type]


def test_copy_controls() -> None:
    frame = pd.DataFrame({"A": [1]})
    table = Table.from_dataframe(frame)
    table.df.loc[0, "A"] = 2
    assert frame.loc[0, "A"] == 1
    assert Table.from_dataframe(frame, copy=False).df is frame
    exported = table.to_dataframe()
    exported.loc[0, "A"] = 3
    assert table.df.loc[0, "A"] == 2
    assert table.to_dataframe(copy=False) is table.df


def test_chain_and_incremental_edits() -> None:
    table = Table(columns=["Name", "Score"])
    assert table.add_rows([]) is table
    assert (
        table.add_row(["Alice", 85])
        .add_rows([{"Name": "Bob", "Score": 92}, ["Charlie", 78]])
        .add_column("Passed", [True, True, False])
        is table
    )
    assert (
        table.update_row(0, {"Score": 90}).rename_column("Name", "Model").remove_row(1)
        is table
    )
    assert table.df.to_dict("list") == {
        "Model": ["Alice", "Charlie"],
        "Score": [90, 78],
        "Passed": [True, False],
    }
    assert table.update_row(1, ["C", 80, True]) is table
    assert table.rename_column("Model", "Model") is table
    assert table.df.iloc[1].tolist() == ["C", 80, True]


def test_inference_partial_rows_and_index_preservation() -> None:
    table = Table().add_rows([{"A": 1}, {"A": 2, "B": 3}])
    assert table.df["B"].isna().iloc[0]
    table.add_row({"B": 4})
    assert table.df["A"].isna().iloc[2]
    frame = pd.DataFrame({"A": [1, 2]}, index=[2, 3])
    table = Table(frame).update_row(0, [7])
    assert table.df.loc[2, "A"] == 7
    table.add_row([9]).remove_row(1)
    assert table.df.index.tolist() == [2, 4]
    duplicate_index = Table(pd.DataFrame({"A": [1, 2]}, index=["x", "x"]))
    duplicate_index.remove_row(0)
    assert duplicate_index.df["A"].tolist() == [2]


@pytest.mark.parametrize(
    ("operation", "error"),
    [
        (lambda t: t.add_row([1]), ValueError),
        (lambda t: t.add_row("bad"), TypeError),
        (lambda t: t.add_row(42), TypeError),
        (lambda t: t.add_rows([[3, 4], {"unknown": 1}]), ValueError),
        (lambda t: t.add_column("A", [1]), ValueError),
        (lambda t: t.add_column("C", []), ValueError),
        (lambda t: t.update_row(-1, [1, 2]), IndexError),
        (lambda t: t.update_row(position=True, row=[1, 2]), TypeError),
        (lambda t: t.remove_row(3), IndexError),
        (lambda t: t.remove_row("0"), TypeError),
        (lambda t: t.rename_column("missing", "C"), KeyError),
        (lambda t: t.rename_column("A", "B"), ValueError),
        (lambda t: t.update_row(0, {"A": 8, "B": [2, 3]}), ValueError),
    ],
)
def test_invalid_edit_is_atomic(operation: Any, error: type[Exception]) -> None:
    table = Table({"A": [1], "B": [2]})
    original = table.df.copy()
    with pytest.raises(error):
        operation(table)
    assert_frame_equal(table.df, original)


def test_missing_columns_and_external_duplicate_columns() -> None:
    with pytest.raises(ValueError, match="Define columns"):
        Table().add_row([1])
    table = Table({"A": [1], "B": [2]})
    table.df.columns = ["A", "A"]
    with pytest.raises(ValueError, match="unique"):
        table.render()


@pytest.mark.parametrize("extension", ["csv", "xlsx", "json"])
def test_data_roundtrip(extension: str, tmp_path: Path) -> None:
    table = Table({"Name": ["Alice", "Bob"], "Score": [85, 92]})
    path = tmp_path / f"data.{extension}"
    if extension == "csv":
        table.to_csv(path, sep=";")
        loaded = Table.from_csv(path, sep=";", title="Loaded", theme="dark_blue")
        assert loaded.title == "Loaded"
    elif extension == "xlsx":
        table.to_excel(path, sheet_name="Results")
        loaded = Table.from_excel(path, sheet_name="Results")
        with pytest.raises(TypeError, match="single"):
            Table.from_excel(path, sheet_name=None)
    else:
        table.to_json(path)
        loaded = Table.from_json(path)
    assert_frame_equal(loaded.df, table.df)
    _, ax = loaded.render()
    # Explicitly requested themes still win over the plain loading default.
    if extension != "csv":
        assert ax.tables[0][0, 0].get_facecolor() == mpl.colors.to_rgba("white")
        assert ax.tables[0][1, 0].get_edgecolor() == mpl.colors.to_rgba("black")
    with pytest.raises(FileNotFoundError):
        Table.from_csv(tmp_path / "missing.csv")


def test_io_overrides(tmp_path: Path) -> None:
    table = Table({"A": [1, 2]})
    table.to_csv(tmp_path / "data.csv", index=True)
    assert Table.from_csv(tmp_path / "data.csv", index_col=0).df.index.tolist() == [
        0,
        1,
    ]
    table.to_json(tmp_path / "data.json", orient="split")
    assert_frame_equal(
        Table.from_json(tmp_path / "data.json", orient="split").df, table.df
    )


@pytest.mark.parametrize("theme", ["blue", "soft_blue", "dark_blue"])
def test_rendering_and_style(theme: str) -> None:
    table = Table(
        {"Name": ["Alice\nSmith", "Bob"], "Score": [85, np.nan]},
        title="Experiment Results",
        theme=theme,
    )
    before = mpl.rcParams.copy()
    fig, ax = table.render()
    fig.canvas.draw()
    assert ax.get_title() == "Experiment Results"
    cells = ax.tables[0].get_celld()
    assert cells[1, 0].get_text().get_horizontalalignment() == "left"
    assert cells[1, 1].get_text().get_horizontalalignment() == "right"
    assert cells[2, 1].get_text().get_text() == ""
    assert cells[1, 0].get_facecolor() != cells[2, 0].get_facecolor()
    for cell in cells.values():
        assert (
            cell.get_text().get_window_extent().width <= cell.get_window_extent().width
        )
        assert (
            cell.get_text().get_window_extent().height
            <= cell.get_window_extent().height
        )
    assert dict(before) == dict(mpl.rcParams)
    table.df.loc[0, "Name"] = "Updated"
    _, new_ax = table.render()
    assert new_ax.tables[0][1, 0].get_text().get_text() == "Updated"


def test_custom_style_and_widths() -> None:
    table = Table(
        {"A": [1], "B": [2]},
        figsize=(7, 3),
        style={
            "header_background": "navy",
            "header_color": "yellow",
            "row_colors": ["white", "silver"],
            "cell_alignment": "center",
            "font_size": 12,
            "column_widths": [1, 2],
        },
    )
    fig, ax = table.render()
    assert fig.get_size_inches().tolist() == [7, 3]
    cells = ax.tables[0].get_celld()
    assert cells[0, 0].get_facecolor() == mpl.colors.to_rgba("navy")
    assert cells[0, 0].get_text().get_color() == "yellow"
    assert cells[1, 0].get_text().get_horizontalalignment() == "center"
    assert cells[0, 1].get_width() == pytest.approx(2 * cells[0, 0].get_width())


@pytest.mark.parametrize(
    "style",
    [
        {"font_size": 0},
        {"cell_alignment": "invalid"},
        {"row_colors": ["red"]},
        {"header_color": "invalid"},
        {"column_widths": [0]},
    ],
)
def test_invalid_style(style: dict[str, Any]) -> None:
    with pytest.raises(
        ValueError, match=r"font|Font|alignment|colors|color|width|RGBA"
    ):
        Table(style=style)


def test_unknown_style_and_width_mismatch() -> None:
    with pytest.raises(TypeError, match="unexpected"):
        Table(style={"unknown": 1})
    with pytest.raises(ValueError, match="column_widths"):
        Table({"A": [1]}, style={"column_widths": [1, 2]}).render()


@pytest.mark.parametrize(
    "table", [Table(), Table(columns=["A"]), Table({"A": [[1, 2]]})]
)
def test_empty_and_nested_rendering(table: Table) -> None:
    fig, _ = table.render()
    fig.canvas.draw()


@pytest.mark.parametrize("extension", ["png", "pdf", "svg"])
def test_save_and_cleanup(extension: str, tmp_path: Path) -> None:
    table = Table({"A": [1]}, title="Saved table")
    path = tmp_path / f"table.{extension}"
    before = plt.get_fignums()
    table.save(path, dpi=120)
    assert plt.get_fignums() == before
    assert path.stat().st_size > 100
    if extension == "pdf":
        assert "Saved table" in PdfReader(path).pages[0].extract_text()
    elif extension == "png":
        assert path.read_bytes().startswith(b"\x89PNG")
    else:
        assert "<svg" in path.read_text()


def test_show_and_failure_cleanup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    shown = []
    monkeypatch.setattr(Figure, "show", lambda fig: shown.append(fig))
    table = Table({"A": [1]})
    table.show()
    assert len(shown) == 1
    before = plt.get_fignums()
    with pytest.raises(ValueError, match="extension"):
        table.save(tmp_path / "bad.txt")
    assert plt.get_fignums() == before

    def fail(*args: Any, **kwargs: Any) -> None:
        message = "render failure"
        raise RuntimeError(message)

    monkeypatch.setattr("tabloom.table.table.MplTable.add_cell", fail)
    with pytest.raises(RuntimeError, match="render failure"):
        table.render()
    assert plt.get_fignums() == before
