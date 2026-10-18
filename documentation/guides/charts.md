# Creating and Customizing Charts

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
