# Troubleshooting

## Import or Python version errors

Tabloom requires Python 3.12 or newer. Use the Python interpreter and notebook
kernel belonging to the environment where Tabloom is installed. If needed:

```bash
python -m pip install tabloom
```

For contributor setup, see
[CONTRIBUTING.md](https://github.com/michalszc/tabloom/blob/master/CONTRIBUTING.md).

## Row or column errors

Supply column names when constructing positional rows. Sequence rows must match
the column count, and new columns must match the existing row count. Mapping
keys must name existing columns unless an entirely empty table is inferring its
initial schema. Duplicate column names are unsupported.

`update_row` and `remove_row` take zero-based positions, not pandas index labels.
Negative positions are rejected. For labels use `table.df.loc[...]` directly.
Pandas may reject a value incompatible with the column dtype; convert that column
through `.df` before assigning values of a different type.

## Chart input errors

Supply both x and y for line, bar, and scatter charts. Their lengths must match.
Use x alone for histogram, box, and pie charts. Column-name inputs need `data=`
and unique column names. Unknown plotting keywords are reported by matplotlib.

## Excel errors

The standard Tabloom installation includes openpyxl for `.xlsx` files. Select one
sheet with `sheet_name="Results"` or `sheet_name=0`; `sheet_name=None` returns a
collection of sheets in pandas and is rejected by Tabloom. Additional Excel
formats and engines require their own pandas dependencies.

## Display and export errors

In headless environments, configure `MPLBACKEND=Agg` before importing Tabloom and
use `save()` rather than `show()`. Creation and saving do not open windows.
An interactive matplotlib backend is needed for graphical display.

Table and chart graphical exports accept PNG, PDF, or SVG extensions; reports
accept PDF only. Create the destination directory first. Large tables may need
large figures; choose sufficient dimensions when overriding automatic sizing.

An empty report needs content or a nonempty title. Blank text sections are
rejected. Saving a chart or including it in a report leaves its figure available
for reuse; close it yourself when finished.
