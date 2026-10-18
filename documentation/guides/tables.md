# Creating and Editing Tables

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
Tables use black text, black borders, and white cells by default, with no colored
headers or alternating backgrounds. To use the original colored appearance,
pass `theme="blue"`; `"soft_blue"` and `"dark_blue"` are also available. File loaders
use the same plain default and accept an explicit `theme` override.

## Preview rows

```python
from tabloom import Table

table = Table({"Value": range(100)})
table.show()          # First 10 rows.
table.show(head=5)    # First 5 rows.
table.show(tail=5)    # Last 5 rows.
```

Supplying both `head` and `tail` raises `ValueError`. Counts must be nonnegative
integers. Previews leave all data in `table.df`; data exports, `save()`, reports,
and `render()` still use the full table. `render(head=n)` and `render(tail=n)`
are available when you need the preview Figure/Axes directly.

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
