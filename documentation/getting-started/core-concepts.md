# Core Concepts

## Tables own data

A `Table` wraps one pandas DataFrame, exposed as `table.df`. Table editing methods
modify the instance and return it for chaining. Rows in `update_row` and
`remove_row` use nonnegative, zero-based **positions**, even when the DataFrame
has custom or duplicate index labels. Other rows retain their index labels.

DataFrames are copied on construction by default. `copy=False` shares the exact
frame until a Table editing method replaces it. `to_dataframe()` returns a copy;
`to_dataframe(copy=False)` returns the same object as `.df`.

```python
import pandas as pd
from tabloom import Table

frame = pd.DataFrame({"Score": [85, 92]}, index=["Alice", "Bob"])
table = Table.from_dataframe(frame)
table.update_row(0, {"Score": 90})  # First row, whose index label is Alice.
assert frame.loc["Alice", "Score"] == 85
assert table.df.loc["Alice", "Score"] == 90
snapshot = table.to_dataframe()
assert snapshot is not table.df
```

Use normal pandas operations through `.df` for filtering, sorting, dtype changes,
and label-based indexing. Rendered tables always use the current data.

## Data exports and visual exports

`to_csv`, `to_excel`, `to_json`, and `to_dataframe` export **data** without visual
styling. CSV and Excel omit the index by default; JSON defaults to records.
Pass pandas options to change these defaults. These formats do not universally
preserve pandas dtypes or index metadata.

`save` on a Table or Chart exports a **visual** as PNG, PDF, or SVG. PNG accepts
DPI control; PDF and SVG retain vector text and graphics where matplotlib can.

## Charts own figures

Chart factories create a Figure and Axes without forcing display. Access them as
`chart.fig` and `chart.ax`. Charts plot the supplied data when created; subsequent
DataFrame edits do not automatically redraw chart artists.

Saving leaves a chart available for customization and reuse. In notebooks,
`chart.show()` and `table.show()` automatically release matplotlib's figure
registration after inline display. The chart's Figure and Axes remain usable
for customization, saving, repeated display, and reports; no manual cleanup
cell is needed. In a graphical application, close the plot window when finished.
A Table's `render()` returns a fresh Figure/Axes pair owned by the caller;
close that figure with `matplotlib.pyplot.close(fig)` when finished.
Table.save cleans up its own temporary figure.

## Reports reuse visuals

Reports retain references to supplied objects and preserve insertion order.
Saving renders tables from current data and uses the current chart figures.
Report saving never closes caller-owned charts or separately rendered tables.

The report theme controls page backgrounds and text. Existing tables and charts
retain their own themes and customizations; select the same theme on each object
for a uniform report.

Content flows top to bottom in insertion order. The report title is a heading on
the first page. Text wraps into the remaining space and continues on later
pages; tables and charts remain intact and move forward only when they do not
fit. Visuals preserve aspect ratios, vector graphics, and searchable text.
Tables and charts fill the printable width by default. Set `resize=0.5` for
half width or `resize="original"` to retain native size where it fits. Very
tall visuals are limited by page height. `add_text` accepts per-block fonts,
colors, alignment, line spacing, and spacing after the block; these settings
are used when wrapping and paginating text.

All pages share the configured paper size and margins. A4 portrait is the
default; Report figsize and margin configure the paper in inches. Use
`add_page_break()` for explicit boundaries, including a separate title page.
Complex multicolumn layout and table-row pagination are outside v0.1.0.
