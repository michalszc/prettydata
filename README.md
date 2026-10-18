# Tabloom

<p align="center">
  <a href="https://pypi.org/project/tabloom/"><img src="https://img.shields.io/pypi/v/tabloom" alt="PyPI version"></a>
  <a href="https://pypi.org/project/tabloom/"><img src="https://img.shields.io/pypi/dm/tabloom" alt="PyPI monthly downloads"></a>
  <a href="https://github.com/michalszc/tabloom/blob/master/pyproject.toml"><img src="https://img.shields.io/badge/python-3.12%2B-important" alt="Python 3.12 or newer"></a>
  <a href="https://github.com/michalszc/tabloom/actions/workflows/ci.yml"><img src="https://github.com/michalszc/tabloom/actions/workflows/ci.yml/badge.svg?branch=master" alt="CI on master"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License: Apache 2.0"></a>
  <a href="https://michalszc.github.io/tabloom/"><img src="https://img.shields.io/badge/docs-online-blue.svg" alt="Docs"></a>
</p>

A Python library for visually appealing tables, charts, and reports with minimal
configuration.

Designed around pandas and matplotlib, Tabloom combines sensible visual
defaults with access to the underlying libraries for advanced customization.

## Features

Tabloom provides:

- Convenient tabular data creation, rows, and records
- Dataset imports from CSV, Excel (.xlsx), and JSON
- Integration with pandas for data manipulation
- Attractive tables and matplotlib charts with sensible defaults
- Advanced customization through pandas and matplotlib
- Table and chart exports and PDF reports combining generated visuals

## Installation

```bash
pip install tabloom
```

Python 3.12+ is required. pandas, matplotlib, openpyxl, and pypdf are installed
automatically.

For the notebook dependencies:

```bash
pip install "tabloom[example]"
```

## Quick start

Create a table, add rows, generate a chart, and combine them into a PDF:

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

Report content fills available page space in order, with automatic pagination.
Long tables continue across pages with repeated headers; use `paginate=False`
on `add_table()` to fit a table as one block instead.
Use `report.add_page_break()` when you want an explicit fresh page.
Tables and charts fill the printable width by default; pass `resize=0.5` for
half width or `resize="original"` for native size. `add_text()` accepts font,
size, color, alignment, and spacing options.

Tables are plain black and white by default. Select `theme="blue"` for the
original colored table style, or choose `"soft_blue"` or `"dark_blue"`. Charts keep their
colored defaults; `theme="plain"` is also available for monochrome charts.
Use `table.df`, `chart.fig`, and `chart.ax` for pandas/matplotlib customization.
Table and chart `save()` support PNG, PDF, and SVG; `to_csv()`, `to_excel()`,
and `to_json()` export table data without graphical styling.

## Documentation

- [Installation](https://michalszc.github.io/tabloom/getting-started/installation/)
- [Quick start](https://michalszc.github.io/tabloom/getting-started/quickstart/)
- [Core concepts](https://michalszc.github.io/tabloom/getting-started/core-concepts/)
- [Guides](https://michalszc.github.io/tabloom/guides/)
- [API reference](https://michalszc.github.io/tabloom/reference/)

## Examples

| Example | Description | Notebook | Colab |
|---------|-------------|----------|-------|
| **Basic usage** | Create tables, charts, and a PDF report | [basic_usage.ipynb](notebooks/basic_usage.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/michalszc/tabloom/blob/master/notebooks/basic_usage.ipynb) |
| **Wine quality report** | Download 1,599 rows, build plain tables, explore three chart types, and export all data in a report | [wine_quality_report.ipynb](notebooks/wine_quality_report.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/michalszc/tabloom/blob/master/notebooks/wine_quality_report.ipynb) |

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup, quality checks, and
the release workflow. Issues and feature requests are welcome in the
[GitHub repository](https://github.com/michalszc/tabloom/issues).
