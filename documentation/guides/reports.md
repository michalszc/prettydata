# Creating PDF Reports

## Fill available page space

Add content in reading order. Tabloom places each item below the previous one,
using the remaining space on the current page before starting another page.

```python
from tabloom import Chart, Report, Table

table = Table({"Model": ["A", "B"], "Score": [85, 92]}, title="Scores")
chart = Chart.bar(data=table, x="Model", y="Score", title="Model Comparison")
report = Report(title="Experiment Results")
report.add_text("Model performance on the validation dataset.")
report.add_table(table).add_chart(chart)
report.add_text("Model B achieved the highest score.")
report.save("report.pdf")
```

The title is a heading on the first page. Text wraps and can continue across
pages, including when it starts in the space below a table or chart. Tables and
charts remain intact: if a visual does not fit the remaining space, it moves to
the next page. Visuals are reduced only when too large for a fresh page, rather
than squeezed into a small leftover area. Items are never reordered to fill
earlier gaps. Elements are separated by 12 points of spacing.

The example above fits on one A4 page. A title-only report is valid; a report
with neither a title nor content raises `ValueError`. Output supports PDF only
and needs no LaTeX installation.

## Choose paper size and margins

All pages use A4 portrait by default. Vector graphics, searchable text, and
visual aspect ratios are preserved. Small visuals retain their native scale;
large visuals are reduced to fit the printable area. The original chart
figures, dimensions, layouts, and customizations are retained.

Supply paper dimensions and margins in inches to choose another size:

```python
from tabloom import Chart, Report

chart = Chart.line([1, 2, 3], [2, 5, 4], title="Trend")
report = Report("Custom Paper", figsize=(8.5, 11), margin=0.75)
report.add_text("A consistent page layout for the complete report.")
report.add_chart(chart)
report.save("custom-report.pdf")
```

Margins must leave a positive printable area. Text needs enough height for at
least one line. Tables remain whole blocks; splitting a large table into rows
across pages is outside v0.1.0.

## Request a page break

Use `add_page_break()` when the next element should start on a fresh page.
For a separate cover page, insert a break after the report title:

```python
from tabloom import Report

report = Report("Experiment Results")
report.add_page_break()
report.add_text("This section starts on the second page.")
report.save("report-with-cover.pdf")
```

The method is chainable. Leading, trailing, and repeated breaks do not create
empty pages.
