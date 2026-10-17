# Quick Start

Create a table, add rows, make a chart, and save a PDF report:

```python
from tabloom import Chart, Report, Table

table = Table(columns=["Model", "Accuracy"], title="Model Results")
table.add_row(["Model A", 0.85])
table.add_row(["Model B", 0.91])
table.add_row({"Model": "Model C", "Accuracy": 0.88})
table.save("results.png")

chart = Chart.bar(
    data=table,
    x="Model",
    y="Accuracy",
    title="Model Comparison",
    ylabel="Accuracy",
)
chart.save("comparison.png")

report = Report(title="Experiment Report")
report.add_text("Comparison of machine learning models.")
report.add_table(table).add_chart(chart)
report.save("experiment_report.pdf")
```

The report contains a cover, text, table, and chart page, in that order.
Use `table.show()` or `chart.show()` in an environment with a graphical backend.
Creation and saving do not open windows. See the [guides](../guides/index.md)
for data files, themes, and customization.
