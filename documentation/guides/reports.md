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

## Consistent paper size

All pages use A4 portrait by default, including pages containing small tables or
large charts. Visuals are fitted within common margins, preserving aspect ratios
and vector quality. Small visuals retain their native scale to avoid inflated
fonts; oversized visuals are reduced to fit. They are centered horizontally and aligned to the top
margin. Original chart dimensions, layouts, and customizations are retained.

To select another paper size, supply dimensions and margins in inches:

```python
from tabloom import Chart, Report

chart = Chart.line([1, 2, 3], [2, 5, 4], title="Trend")
report = Report("Custom Paper", figsize=(8.5, 11), margin=0.75)
report.add_text("A consistent page layout for the complete report.")
report.add_chart(chart)
report.save("custom-report.pdf")
```

The configured margins must leave a positive printable area. Very large tables
are scaled to one page; automatic table pagination remains outside v0.1.0.
