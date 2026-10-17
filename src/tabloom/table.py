"""DataFrame-backed tables with convenient editing and graphical output."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, cast

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.colors import to_rgba
from matplotlib.font_manager import FontProperties
from matplotlib.table import Table as MplTable
from matplotlib.transforms import Bbox
from pandas.api.types import is_list_like, is_numeric_dtype

from tabloom._rendering import _new_figure, _positive, _save_figure
from tabloom._themes import _get_theme

if TYPE_CHECKING:
    from collections.abc import Hashable, Iterable, Sequence
    from pathlib import Path

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


@dataclass(frozen=True)
class _TableStyle:
    header_background: str | None = None
    header_color: str | None = None
    row_colors: Sequence[str] | None = None
    font_size: float = 11
    cell_alignment: Literal["auto", "left", "center", "right"] = "auto"
    column_widths: Sequence[float] | None = None

    def __post_init__(self) -> None:
        _positive(self.font_size, "Font size")
        if self.cell_alignment not in {"auto", "left", "center", "right"}:
            message = "cell_alignment must be auto, left, center, or right."
            raise ValueError(message)
        if self.row_colors is not None and len(self.row_colors) != 2:
            message = "row_colors must contain two alternating colors."
            raise ValueError(message)
        colors = [self.header_background, self.header_color]
        colors.extend(self.row_colors or ())
        for color in colors:
            if color is not None:
                to_rgba(color)
        for width in self.column_widths or ():
            _positive(width, "Column widths")


def _text_size(
    text: str, font_size: float, weight: str = "normal"
) -> tuple[float, float]:
    """Measure plain multiline text in inches using matplotlib's own renderer."""
    renderer = RendererAgg(1, 1, 72)
    font = FontProperties(family="DejaVu Sans", size=font_size, weight=weight)
    lines = text.split("\n")
    width = max(
        renderer.get_text_width_height_descent(line, font, ismath=False)[0]
        for line in lines
    )
    return (width + 12) / (0.84 * 72), (len(lines) * font_size * 1.4 + 14) / 72


def _display(value: Any) -> str:
    if pd.api.types.is_scalar(value) and pd.isna(value):
        return ""
    return str(value)


def _dataframe(value: Any) -> pd.DataFrame:
    if not isinstance(value, pd.DataFrame):
        message = (
            "Expected a single pandas DataFrame; select one sheet for Excel input."
        )
        raise TypeError(message)
    return value


class Table:
    """An editable pandas table with professional graphical defaults.

    Args:
        data: Column mapping, records, rows, DataFrame, or None.
        columns: Column names; required for positional rows.
        title: Optional title above the rendered table.
        theme: One of ``default``, ``light``, or ``dark``.
        style: Overrides: header_background, header_color, row_colors,
            font_size, cell_alignment, and relative column_widths.
        figsize: Optional figure width and height in inches.
        copy: Copy an incoming DataFrame by default. With False, share it until
            an editing method replaces the underlying frame.
    """

    def __init__(  # noqa: PLR0913 - explicit construction and presentation options
        self,
        data: Any = None,
        *,
        columns: Sequence[Hashable] | None = None,
        title: str | None = None,
        theme: str = "default",
        style: Mapping[str, Any] | None = None,
        figsize: tuple[float, float] | None = None,
        copy: bool = True,
    ) -> None:
        self._theme = _get_theme(theme)
        self._style = _TableStyle(**dict(style or {}))
        self.title = title
        self.figsize = figsize
        if (
            isinstance(data, (list, tuple))
            and data
            and columns is None
            and not isinstance(data[0], Mapping)
        ):
            message = "Provide columns when constructing a table from rows."
            raise ValueError(message)
        if isinstance(data, pd.DataFrame) and columns is None:
            self.df = data.copy() if copy else data
        else:
            self.df = pd.DataFrame(
                data, columns=list(columns) if columns is not None else None, copy=copy
            )
        self._validate_columns()

    def _validate_columns(self) -> None:
        if not self.df.columns.is_unique:
            message = "Table column names must be unique."
            raise ValueError(message)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, **kwargs: Any) -> Table:
        """Wrap a DataFrame; pass copy=False to share its data."""
        return cls(_dataframe(df), **kwargs)

    @classmethod
    def from_csv(
        cls,
        path: str | Path,
        *,
        title: str | None = None,
        theme: str = "default",
        style: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Table:
        """Read CSV data, forwarding extra options to pandas.read_csv."""
        return cls(
            pd.read_csv(path, **kwargs),
            title=title,
            theme=theme,
            style=style,
            copy=False,
        )

    @classmethod
    def from_excel(
        cls,
        path: str | Path,
        *,
        title: str | None = None,
        theme: str = "default",
        style: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Table:
        """Read one Excel sheet, forwarding options to pandas.read_excel."""
        frame = pd.read_excel(path, **{"engine": "openpyxl", **kwargs})
        return cls(_dataframe(frame), title=title, theme=theme, style=style, copy=False)

    @classmethod
    def from_json(
        cls,
        path: str | Path,
        *,
        title: str | None = None,
        theme: str = "default",
        style: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Table:
        """Read JSON data, forwarding options to pandas.read_json."""
        return cls(
            pd.read_json(path, **kwargs),
            title=title,
            theme=theme,
            style=style,
            copy=False,
        )

    def _row(self, row: Any, *, partial: bool = False) -> dict[Hashable, Any]:
        if isinstance(row, Mapping):
            unknown = set(row).difference(self.df.columns)
            if len(unknown):
                message = f"Unknown columns: {list(unknown)!r}."
                raise ValueError(message)
            return (
                dict(row)
                if partial
                else {col: row.get(col, pd.NA) for col in self.df.columns}
            )
        if isinstance(row, (str, bytes)) or not is_list_like(row):
            message = "A row must be a mapping or a sequence of cell values."
            raise TypeError(message)
        values = list(row)
        if len(values) != len(self.df.columns):
            message = f"Expected {len(self.df.columns)} row values, got {len(values)}."
            raise ValueError(message)
        return dict(zip(self.df.columns, values, strict=True))

    def add_row(self, row: Any) -> Table:
        """Append a mapping or positional row and return this table."""
        return self.add_rows([row])

    def add_rows(self, rows: Iterable[Any]) -> Table:
        """Append rows atomically, inferring columns from mappings if needed."""
        self._validate_columns()
        records = list(rows)
        if not records:
            return self
        if not len(self.df.columns):
            if not all(isinstance(row, Mapping) for row in records):
                message = "Define columns before adding positional rows."
                raise ValueError(message)
            incoming = pd.DataFrame(records)
        else:
            incoming = pd.DataFrame(
                [self._row(row) for row in records], columns=self.df.columns
            )
        labels = []
        next_label = len(self.df)
        for _ in records:
            while next_label in self.df.index:
                next_label += 1
            labels.append(next_label)
            next_label += 1
        incoming.index = pd.Index(labels)
        self.df = incoming if not len(self.df) else pd.concat([self.df, incoming])
        return self

    def add_column(self, name: Hashable, values: Iterable[Any]) -> Table:
        """Add a column of values in row order; existing names are rejected."""
        self._validate_columns()
        if name in self.df.columns:
            message = f"Column {name!r} already exists."
            raise ValueError(message)
        data = list(values)
        if len(data) != len(self.df):
            message = "Column length must match the number of rows."
            raise ValueError(message)
        frame = self.df.copy()
        frame[name] = data
        self.df = frame
        return self

    def _position(self, position: int) -> None:
        self._validate_columns()
        if isinstance(position, bool) or not isinstance(position, int):
            message = "Row position must be a nonnegative integer."
            raise TypeError(message)
        if not 0 <= position < len(self.df):
            message = f"Row position {position} is out of range."
            raise IndexError(message)

    def update_row(self, position: int, row: Any) -> Table:
        """Update a row by zero-based position; mappings may update some cells."""
        self._position(position)
        updates = self._row(row, partial=True)
        frame = self.df.copy()
        for col, value in updates.items():
            frame.iat[position, cast("int", frame.columns.get_loc(col))] = value  # noqa: PD009 - scalar positional assignment
        self.df = frame
        return self

    def remove_row(self, position: int) -> Table:
        """Remove a row by zero-based position, preserving other index labels."""
        self._position(position)
        self.df = self.df.iloc[[i for i in range(len(self.df)) if i != position]].copy()
        return self

    def rename_column(self, old: Hashable, new: Hashable) -> Table:
        """Rename a column, rejecting missing names and name collisions."""
        self._validate_columns()
        if old not in self.df.columns:
            raise KeyError(old)
        if new != old and new in self.df.columns:
            message = f"Column {new!r} already exists."
            raise ValueError(message)
        self.df = self.df.rename(columns={old: new})
        return self

    def to_dataframe(self, *, copy: bool = True) -> pd.DataFrame:
        """Return a copy of the data, or the underlying frame with copy=False."""
        return self.df.copy() if copy else self.df

    def to_csv(self, path: str | Path, **kwargs: Any) -> None:
        """Export data, without styling; omit the index unless overridden."""
        self.df.to_csv(path, **{"index": False, **kwargs})

    def to_excel(self, path: str | Path, **kwargs: Any) -> None:
        """Export data to Excel using pandas and openpyxl, without styling."""
        self.df.to_excel(path, **{"index": False, "engine": "openpyxl", **kwargs})

    def to_json(self, path: str | Path, **kwargs: Any) -> None:
        """Export data as JSON records by default, without graphical styling."""
        self.df.to_json(path, **{"orient": "records", **kwargs})

    def render(self) -> tuple[Figure, Axes]:
        """Create a fresh Figure/Axes from current data; the caller owns it."""
        self._validate_columns()
        style, theme = self._style, self._theme
        rows = [[str(col) for col in self.df.columns]]
        rows.extend(
            [_display(value) for value in row]
            for row in self.df.itertuples(index=False, name=None)
        )
        widths = [
            max(
                _text_size(row[col], style.font_size, "bold" if i == 0 else "normal")[0]
                for i, row in enumerate(rows)
            )
            for col in range(len(self.df.columns))
        ]
        heights = [
            max((_text_size(cell, style.font_size)[1] for cell in row), default=0.5)
            for row in rows
        ]
        if style.column_widths is not None:
            if len(style.column_widths) != len(widths):
                message = "column_widths must match the number of columns."
                raise ValueError(message)
            total = sum(style.column_widths)
            fractions = [value / total for value in style.column_widths]
            required = max(
                (
                    width / fraction
                    for width, fraction in zip(widths, fractions, strict=True)
                ),
                default=0,
            )
            widths = [fraction * required for fraction in fractions]
        title_width = (
            _text_size(self.title, style.font_size + 3)[0] if self.title else 0
        )
        size = self.figsize or (
            max(3, sum(widths) + 0.5, title_width),
            max(1.2, sum(heights) + (0.7 if self.title else 0.3)),
        )
        fig, ax = _new_figure(theme, size, style.font_size)
        try:
            ax.set_axis_off()
            if self.title:
                ax.set_title(
                    self.title,
                    fontsize=style.font_size + 3,
                    color=theme.foreground,
                    pad=16,
                    fontfamily="DejaVu Sans",
                    usetex=False,
                )
            if not widths:
                ax.text(
                    0.5, 0.5, "No data", ha="center", va="center", color=theme.muted
                )
                return fig, ax
            artist = MplTable(ax, bbox=Bbox.from_bounds(0, 0, 1, 1))
            for row_number, row in enumerate(rows):
                for col_number, text in enumerate(row):
                    header = row_number == 0
                    background = (
                        (style.header_background or theme.header_background)
                        if header
                        else (style.row_colors or theme.rows)[(row_number - 1) % 2]
                    )
                    alignment = style.cell_alignment
                    if alignment == "auto":
                        alignment = (
                            "right"
                            if is_numeric_dtype(self.df.dtypes.iloc[col_number])
                            else "left"
                        )
                    cell = artist.add_cell(
                        row_number,
                        col_number,
                        width=widths[col_number] / sum(widths),
                        height=heights[row_number] / sum(heights),
                        text=text,
                        loc=alignment,
                        facecolor=background,
                        edgecolor=theme.grid,
                    )
                    cell.set_linewidth(0.5)
                    cell.PAD = 0.08
                    cell.get_text().set(
                        fontsize=style.font_size,
                        fontfamily="DejaVu Sans",
                        color=(style.header_color or theme.header_color)
                        if header
                        else theme.foreground,
                        weight="bold" if header else "normal",
                        usetex=False,
                    )
            artist.auto_set_font_size(value=False)
            ax.add_table(artist)
        except Exception:
            plt.close(fig)
            raise
        return fig, ax

    def show(self) -> None:
        """Display a freshly rendered table using the active graphical backend."""
        fig, _ = self.render()
        fig.show()

    def save(self, path: str | Path, *, dpi: float = 200, **kwargs: Any) -> None:
        """Save a rendered PNG, PDF, or SVG, rather than exporting table data."""
        fig, _ = self.render()
        try:
            _save_figure(fig, path, dpi=dpi, **kwargs)
        finally:
            plt.close(fig)
