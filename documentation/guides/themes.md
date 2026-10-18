# Themes and Table Styling

## Select themes and customize tables

Tables default to `plain`: black text and borders on white cells. Charts and
reports keep the colored `blue` theme. Select `theme="blue"` on a table
for the original blue header and alternating rows. All three classes support
`plain`, `blue`, `soft_blue`, and `dark_blue`. No theme permanently changes global
matplotlib settings, and table style overrides still work with any theme.

```python
import matplotlib.pyplot as plt
from tabloom import Chart, Table

table = Table(
    {"Model": ["A", "B"], "Score": [85, 92]},
    title="Results", theme="dark_blue",
    style={
        "header_background": "#315c75",
        "header_color": "white",
        "row_colors": ["#202e3b", "#283847"],
        "font_size": 11,
        "cell_alignment": "auto",
        "column_widths": [2, 1],
    },
)
chart = Chart.bar(data=table, x="Model", y="Score", theme="dark_blue")
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
