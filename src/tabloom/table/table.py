"""DataFrame-backed table creation, editing, rendering, and export."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, cast

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.table import Table as MplTable
from matplotlib.transforms import Bbox
from pandas.api.types import is_list_like, is_numeric_dtype

from tabloom.rendering.new_figure import _new_figure
from tabloom.rendering.save_figure import _save_figure
from tabloom.rendering.show_figure import _show_figure
from tabloom.table.layout import _TableLayout
from tabloom.table.select_rows import _select_rows
from tabloom.table.style import _TableStyle
from tabloom.themes.get_theme import _get_theme
from tabloom.validation.dataframe import _dataframe

if TYPE_CHECKING:
    from collections.abc import Hashable, Iterable, Sequence
    from pathlib import Path

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


class Table:
    """An editable pandas table with plain black-and-white graphical defaults.

    Args:
        data: Column mapping, records, rows, DataFrame, or None.
        columns: Column names; required for positional rows.
        title: Optional title above the rendered table.
        theme: Plain black and white by default. Choose ``blue``, ``soft_blue``,
            or ``dark_blue`` for colored headers and alternating row backgrounds.
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
        theme: str = "plain",
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
        """Construct a table from a pandas DataFrame.

        Args:
            df: Source DataFrame.
            **kwargs: Table constructor options. Data is copied by default;
                copy=False shares the exact DataFrame until an editing method
                replaces it.

        Returns:
            A new table with the requested visual settings.

        Raises:
            TypeError: The input is not a single DataFrame.
        """
        return cls(_dataframe(df), **kwargs)

    @classmethod
    def from_csv(
        cls,
        path: str | Path,
        *,
        title: str | None = None,
        theme: str = "plain",
        style: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Table:
        """Read a CSV file using pandas.

        Args:
            path: Path to the input CSV file.
            title: Optional title for graphical output.
            theme: Name of the visual theme.
            style: Table-specific visual overrides.
            **kwargs: Options forwarded to pandas.read_csv, such as sep or index_col.

        Returns:
            A new table containing the loaded data.
        """
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
        theme: str = "plain",
        style: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Table:
        """Read one Excel sheet using pandas and openpyxl.

        Args:
            path: Path to an Excel workbook, normally an .xlsx file.
            title: Optional title for graphical output.
            theme: Name of the visual theme.
            style: Table-specific visual overrides.
            **kwargs: Options forwarded to pandas.read_excel, including a single
                sheet_name. The default engine is openpyxl.

        Returns:
            A new table containing one sheet.

        Raises:
            TypeError: The options request multiple sheets instead of one DataFrame.
        """
        frame = pd.read_excel(path, **{"engine": "openpyxl", **kwargs})
        return cls(_dataframe(frame), title=title, theme=theme, style=style, copy=False)

    @classmethod
    def from_json(
        cls,
        path: str | Path,
        *,
        title: str | None = None,
        theme: str = "plain",
        style: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> Table:
        """Read a JSON file using pandas.

        Args:
            path: Path to the JSON data file.
            title: Optional title for graphical output.
            theme: Name of the visual theme.
            style: Table-specific visual overrides.
            **kwargs: Options forwarded to pandas.read_json, such as orient or lines.

        Returns:
            A new table containing the loaded data.
        """
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
        """Append one mapping or positional row.

        Args:
            row: A mapping from column names to values, or values in column order.
                Missing mapping keys receive missing values. Unknown keys are rejected.

        Returns:
            This table, allowing method chaining.

        Raises:
            TypeError: The row is not a mapping or sequence.
            ValueError: Columns are missing, unknown, or have the wrong value count.
        """
        return self.add_rows([row])

    def add_rows(self, rows: Iterable[Any]) -> Table:
        """Append multiple rows without partially applying invalid input.

        Args:
            rows: An iterable of row mappings or positional sequences. An entirely
                empty table infers columns from mappings; positional rows require
                existing columns. An empty iterable leaves the table unchanged.

        Returns:
            This table, allowing method chaining.

        Raises:
            TypeError: A row is not a mapping or sequence.
            ValueError: A row has unknown columns or an incorrect value count.
        """
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
        """Append a column whose values follow the current row order.

        Args:
            name: A new, unique column name.
            values: One value per existing row. Series index labels are not aligned.

        Returns:
            This table, allowing method chaining.

        Raises:
            ValueError: The column already exists or its length differs from the table.
        """
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
        """Update cells identified by a zero-based row position.

        Args:
            position: Nonnegative row position, independent of pandas index labels.
            row: A partial mapping of cells to update, or a complete sequence in
                column order. Unspecified mapping keys retain their previous values.

        Returns:
            This table. Failed assignments do not partially change the stored frame.

        Raises:
            TypeError: The position or row has an unsupported type.
            IndexError: The position is negative or outside the current table.
            ValueError: Row keys or sequence length do not match the schema.
        """
        self._position(position)
        updates = self._row(row, partial=True)
        frame = self.df.copy()
        for col, value in updates.items():
            frame.iat[position, cast("int", frame.columns.get_loc(col))] = value  # noqa: PD009 - scalar positional assignment
        self.df = frame
        return self

    def remove_row(self, position: int) -> Table:
        """Remove one row while preserving the remaining index labels.

        Args:
            position: Nonnegative, zero-based row position rather than an index label.

        Returns:
            This table, allowing method chaining.

        Raises:
            TypeError: The position is not an integer.
            IndexError: The position is negative or outside the current table.
        """
        self._position(position)
        self.df = self.df.iloc[[i for i in range(len(self.df)) if i != position]].copy()
        return self

    def rename_column(self, old: Hashable, new: Hashable) -> Table:
        """Rename a column without overwriting an existing column.

        Args:
            old: Existing column name.
            new: Replacement name. Reusing the same name is allowed.

        Returns:
            This table, allowing method chaining.

        Raises:
            KeyError: The old column does not exist.
            ValueError: The replacement collides with another column.
        """
        self._validate_columns()
        if old not in self.df.columns:
            raise KeyError(old)
        if new != old and new in self.df.columns:
            message = f"Column {new!r} already exists."
            raise ValueError(message)
        self.df = self.df.rename(columns={old: new})
        return self

    def to_dataframe(self, *, copy: bool = True) -> pd.DataFrame:
        """Return table data without graphical styling.

        Args:
            copy: Return an independent DataFrame copy by default. If False, return
                the same object as table.df.

        Returns:
            The copied or shared pandas DataFrame.
        """
        return self.df.copy() if copy else self.df

    def to_csv(self, path: str | Path, **kwargs: Any) -> None:
        """Export table data as CSV without graphical styling.

        Args:
            path: Destination data filename.
            **kwargs: Options forwarded to pandas DataFrame.to_csv.
                The index is omitted unless index=True is supplied.
        """
        self.df.to_csv(path, **{"index": False, **kwargs})

    def to_excel(self, path: str | Path, **kwargs: Any) -> None:
        """Export table data as EXCEL without graphical styling.

        Args:
            path: Destination data filename.
            **kwargs: Options forwarded to pandas DataFrame.to_excel.
                The index is omitted and openpyxl is the default engine.
        """
        self.df.to_excel(path, **{"index": False, "engine": "openpyxl", **kwargs})

    def to_json(self, path: str | Path, **kwargs: Any) -> None:
        """Export table data as JSON without graphical styling.

        Args:
            path: Destination data filename.
            **kwargs: Options forwarded to pandas DataFrame.to_json.
                The default orientation is records; pass orient to override it.
        """
        self.df.to_json(path, **{"orient": "records", **kwargs})

    def render(
        self, *, head: int | None = None, tail: int | None = None
    ) -> tuple[Figure, Axes]:
        """Create a fresh matplotlib rendering of the current data.

        Args:
            head: Render only the first n rows. None leaves rows unrestricted.
            tail: Render only the last n rows. Cannot be combined with head.

        Returns:
            A Figure/Axes pair owned by the caller. Call plt.close(fig) when it is
            no longer needed. Direct changes to table.df are reflected immediately.

        Raises:
            TypeError: A preview count is not an integer.
            ValueError: Preview counts, column names, dimensions, or widths are invalid.
        """
        self._validate_columns()
        frame = _select_rows(self.df, head, tail)
        return self._render_layout(self._layout(frame))

    def _layout(self, frame: pd.DataFrame | None = None) -> _TableLayout:
        """Measure current data without creating a figure or storing another dataset."""
        self._validate_columns()
        return _TableLayout(
            self.df if frame is None else frame, self._style, self.title, self.figsize
        )

    def _render_layout(
        self,
        layout: _TableLayout,
        *,
        start: int = 0,
        stop: int | None = None,
        figsize: tuple[float, float] | None = None,
        exact: bool = False,
    ) -> tuple[Figure, Axes]:
        """Reuse measured columns when rendering an intact table or a row section."""
        stop = len(layout.rows) - 1 if stop is None else stop
        rows = [layout.rows[0], *layout.rows[start + 1 : stop + 1]]
        row_heights = layout.page_heights if exact else layout.heights
        heights = [row_heights[0], *row_heights[start + 1 : stop + 1]]
        widths = layout.widths
        style, theme = self._style, self._theme
        size = figsize or layout.size
        fig, ax = _new_figure(theme, size, style.font_size)
        try:
            if exact:
                fig.set_layout_engine(None)
                margin = min(0.15, size[0] / 4)
                ax.set_position(
                    (
                        margin / size[0],
                        0.15 / size[1],
                        (size[0] - 2 * margin) / size[0],
                        sum(heights) / size[1],
                    )
                )
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
                        else (style.row_colors or theme.rows)[
                            (start + row_number - 1) % 2
                        ]
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

    def show(self, *, head: int | None = None, tail: int | None = None) -> None:
        """Display a preview of the table without changing its data.

        Args:
            head: Show the first n rows. When neither option is supplied, show 10.
            tail: Show the last n rows instead. Cannot be combined with head.

        Raises:
            TypeError: A preview count is not an integer.
            ValueError: A preview count is negative or both options are supplied.

        In a notebook, the Figure is displayed inline without writing an image
        file and its pyplot registration is cleaned up automatically. Outside
        notebooks, display uses the active graphical backend.
        """
        if head is None and tail is None:
            head = 10
        fig, _ = self.render(head=head, tail=tail)
        _show_figure(fig)

    def save(self, path: str | Path, *, dpi: float = 200, **kwargs: Any) -> None:
        """Save the styled table as PNG, PDF, or SVG.

        Args:
            path: Destination filename, including .png, .pdf, or .svg extension.
            dpi: Positive raster resolution in dots per inch; defaults to 200.
            **kwargs: Additional matplotlib Figure.savefig options, such as
                transparent or bbox_inches.

        Raises:
            ValueError: The extension or DPI is unsupported.

        The temporary rendering is closed after export. Use to_csv, to_excel, or
        to_json to export data rather than graphical styling.
        """
        fig, _ = self.render()
        try:
            _save_figure(fig, path, dpi=dpi, **kwargs)
        finally:
            plt.close(fig)
