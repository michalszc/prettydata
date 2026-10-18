# Loading and Exporting Data

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
