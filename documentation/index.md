# Tabloom

Tabloom creates attractive tables, charts, and PDF reports with a few lines of
Python. Version **0.1.0** builds on pandas and matplotlib, with consistent themes
and access to the underlying objects for advanced customization.

```python
from tabloom import Chart, Report, Table

table = Table({"Model": ["A", "B"], "Accuracy": [0.85, 0.91]})
chart = Chart.bar(data=table, x="Model", y="Accuracy", title="Model Comparison")
report = Report(title="Experiment Results")
report.add_text("Model performance on the validation set.")
report.add_table(table).add_chart(chart)
report.save("experiment.pdf")
```

## Documentation map

- [Getting Started](getting-started/index.md): installation and a working example.
- [Core Concepts](getting-started/core-concepts.md): data, visuals, and ownership.
- [Guides](guides/index.md): editing, external files, charts, themes, and reports.
- [API Reference](reference/index.md): the public classes and methods.
- [Examples](examples.md): basic usage and a complete large-dataset report, with Colab links.
- [Troubleshooting](troubleshooting.md): input, export, and display errors.
- [Release Notes](release-notes.md): changes grouped by version.
