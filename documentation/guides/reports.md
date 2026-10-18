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
the next page. Visuals fill the printable width by default, preserving aspect
ratios. They are never squeezed into a small leftover area. Items are never
reordered to fill earlier gaps. Elements are separated by 12 points by default.

Full-width visuals may need multiple pages. A title-only report is valid; a report
with neither a title nor content raises `ValueError`. Output supports PDF only
and needs no LaTeX installation.

## Style text

Each `add_text` call accepts its own typography and spacing. Font sizes and
`space_after` are measured in points (72 points = 1 inch). `line_spacing` is a
line-height multiplier, at least 1; it affects both wrapping layout and page
capacity. Text inherits the report theme's foreground color unless overridden.

```python
from tabloom import Report

report = Report()
report.add_text(
    "Experiment Results",
    font_family="DejaVu Serif",
    font_size=22,
    font_weight="bold",
    color="#244c66",
    align="center",
    space_after=18,
)
report.add_text(
    "Model B achieved the highest accuracy on the validation dataset.",
    font_size=11,
    font_style="italic",
    line_spacing=1.4,
    space_after=6,
)
report.save("styled-text.pdf")
```

The default text settings are DejaVu Sans, 12 points, normal weight and style,
left alignment, 1.5 line spacing, and 12 points after the block. Choose `left`,
`center`, or `right` alignment. Font families must be installed and available to
matplotlib; bundled choices include DejaVu Sans, DejaVu Serif, and DejaVu Sans
Mono. Font weights and styles use matplotlib's values. The same font is used
for measurement and rendering, and styling never changes global settings.

`Report(title="...")` supplies a 24-point bold heading. To customize the main
heading, omit this automatic title and create it with `add_text`, as above.

## Size tables and charts

Both `add_table` and `add_chart` accept `resize`:

| Value | Result |
| --- | --- |
| `"full"` (default) | Fill the printable width between the margins. |
| A number in `(0, 1]`, such as `0.5` | Use that fraction of the printable width. |
| `"original"` | Keep native size, shrinking only if necessary to fit the page. |

```python
from tabloom import Chart, Report, Table

table = Table({"Model": ["A", "B"], "Score": [85, 92]})
chart = Chart.bar(data=table, x="Model", y="Score", title="Comparison")
report = Report("Visual Sizes")
report.add_table(table)  # Full width by default.
report.add_chart(chart, resize=0.5)  # Half the printable width, centered.
report.add_table(table, resize="original")
report.save("sized-report.pdf")
```

Scaling preserves the complete visual, including fonts, titles, and labels, and
does not modify the supplied object. Smaller visuals can be enlarged. Very tall
visuals are limited by the printable page height, so their final width may be
less than requested. Every visual remains a centered block in the content flow;
a fractional width does not place multiple visuals side by side.

## Choose paper size and margins

All pages use A4 portrait by default. Vector graphics, searchable text, and
visual aspect ratios are preserved. Visuals use the requested width within the
printable area. The original chart
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
For a complete large-data workflow, see the [wine-quality notebook](../examples.md).
It explicitly slices all 1,599 observations into 32-row tables, repeating column
headers and adding page breaks to produce a readable landscape data appendix.

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
