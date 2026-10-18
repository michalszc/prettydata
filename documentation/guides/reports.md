# Creating PDF Reports

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
