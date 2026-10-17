# Guides

## Create tables

```python
import pandas as pd
from tabloom import Table

columns = Table({"Name": ["Alice", "Bob"], "Score": [85, 92]})
records = Table([{"Name": "Alice", "Score": 85}])
rows = Table([["Alice", 85]], columns=["Name", "Score"])
frame = Table.from_dataframe(pd.DataFrame({"Score": [85, 92]}))
empty = Table(columns=["Name", "Score"])
```

Positional rows require explicit column names. Column names must be unique.

## Edit incrementally

```python
from tabloom import Table

table = Table(columns=["Name", "Score"])
table.add_row(["Alice", 85])
table.add_rows([{"Name": "Bob", "Score": 92}, ["Charlie", 78]])
table.add_column("Passed", [True, True, False])
table.update_row(1, {"Score": 95})
table.remove_row(2)
table.rename_column("Name", "Student")
print(table.df)
```

Methods return the same Table for chaining. Sequence rows must match the column
count. Mapping inserts may omit columns, which receive missing values; mapping
updates change only supplied cells. Unknown columns, duplicate names, invalid
positions, and mismatched column lengths raise exceptions before modifying data.
Pandas validates the dtype compatibility of cell updates.

An entirely empty `Table()` can infer columns from appended mapping rows.
Adding a column requires one value per existing row, supplied in row order.

## Load and export data

This complete example writes sample files and reads them back. For existing data,
replace the filenames with your own. Extra I/O options are passed to pandas.

```python
from tabloom import Table

table = Table({"Name": ["Alice", "Bob"], "Score": [85, 92]})
table.to_csv("scores.csv", sep=";")
table.to_excel("scores.xlsx", sheet_name="Results")
table.to_json("scores.json")

csv_table = Table.from_csv("scores.csv", sep=";", title="CSV results")
excel_table = Table.from_excel("scores.xlsx", sheet_name="Results")
json_table = Table.from_json("scores.json")
frame = csv_table.to_dataframe()
assert frame["Score"].tolist() == [85, 92]
```

`from_excel` loads one sheet at a time; pass a single sheet name or number.
The default engine is openpyxl for `.xlsx` files. Other formats or engines may
require additional pandas dependencies, which Tabloom does not install.

## Create charts

```python
import pandas as pd
from tabloom import Chart, Table

frame = pd.DataFrame({"epoch": [1, 2, 3, 4], "loss": [0.9, 0.6, 0.4, 0.3]})
line = Chart.line(
    data=frame, x="epoch", y="loss", title="Training Progress",
    xlabel="Epoch", ylabel="Loss", color="teal", linewidth=2, marker="o",
    figsize=(8, 5), font_size=12, label="Training",
)
bar = Chart.bar(data=Table(frame), x="epoch", y="loss")
scatter = Chart.scatter([1, 2, 3], [2, 4, 3], s=60)
histogram = Chart.hist(frame["loss"], bins=3)
box = Chart.box([[1, 2, 3], [2, 3, 5]], tick_labels=["A", "B"])
pie = Chart.pie([3, 2, 1], labels=["A", "B", "C"], autopct="%1.0f%%")

line.ax.set_yscale("log")
line.save("training.svg")
```

Factories accept lists, NumPy arrays, and pandas Series. With `data=`, strings
name columns in a DataFrame or Table. Histograms, box plots, and pie charts use
`x` for values; pies also accept a column name for `labels`. Paired charts need
matching x/y lengths. Pie values must be nonnegative.

All factories accept `title`, `xlabel`, `ylabel`, `theme`, `figsize`, and
`font_size`. Other keywords go to the relevant matplotlib method. Scatter uses
`s` for point size and `c` for numeric color data; pie uses `colors` for wedge
colors; box uses matplotlib's `boxprops`, `medianprops`, and related options.
An explicit `label` creates a legend where the plot supports one. Unsupported
keywords raise an error.

## Select themes and customize tables

Use `default`, `light`, or `dark` on both tables and charts. No theme permanently
changes matplotlib's global settings.

```python
import matplotlib.pyplot as plt
from tabloom import Chart, Table

table = Table(
    {"Model": ["A", "B"], "Score": [85, 92]},
    title="Results", theme="dark",
    style={
        "header_background": "#315c75",
        "header_color": "white",
        "row_colors": ["#202e3b", "#283847"],
        "font_size": 11,
        "cell_alignment": "auto",
        "column_widths": [2, 1],
    },
)
chart = Chart.bar(data=table, x="Model", y="Score", theme="dark")
table.save("dark-table.png")
chart.save("dark-chart.png")

fig, ax = table.render()
ax.set_title("Custom title", color="white")
fig.savefig("custom-table.svg", bbox_inches="tight")
plt.close(fig)
```

`cell_alignment` accepts `auto`, `left`, `center`, or `right`; auto right-aligns
numeric columns and left-aligns other columns. `column_widths` contains one
positive relative width per column. Automatic figure sizes account for text
measurements, multiline cells, headers, and titles. `figsize=(width, height)`
overrides dimensions in inches; choose sufficient space for the content.
Unknown style keys and invalid values raise exceptions.

## Save visual output

```python
from tabloom import Chart, Table

table = Table({"Model": ["A", "B"], "Score": [85, 92]}, title="Results")
chart = Chart.bar(data=table, x="Model", y="Score", title="Scores")
for extension in ("png", "pdf", "svg"):
    table.save(f"results.{extension}", dpi=200)
    chart.save(f"comparison.{extension}", dpi=200)
```

Save methods accept matplotlib savefig options such as `transparent=True`.
Output uses tight bounds by default. Parent directories must already exist.
Saving never forces interactive display. `table.show()` and `chart.show()` use
the active backend; use an interactive backend when opening graphical windows.

## Combine a PDF report

```python
from tabloom import Chart, Report, Table

table = Table({"Model": ["A", "B"], "Score": [85, 92]}, title="Scores")
chart = Chart.bar(data=table, x="Model", y="Score", title="Model Comparison")
report = Report(title="Experiment Results")
report.add_text("Model performance on the validation dataset.")
report.add_table(table).add_chart(chart)
report.save("report.pdf")
```

An optional title produces a cover page. Text sections wrap and paginate; tables
and charts each occupy one page. Insertion order is preserved. A title-only
report is valid; saving a report with neither title nor content raises
`ValueError`. Report output supports PDF only and needs no LaTeX installation.
