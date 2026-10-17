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

Designed around pandas and matplotlib, Tabloom aims to combine sensible visual
defaults with access to the underlying libraries for advanced customization.

## Features

Tabloom provides:

- Convenient tabular data creation, rows, and records
- Dataset imports from CSV, Excel, JSON, and other formats
- Integration with pandas for data manipulation
- Attractive tables and matplotlib charts with sensible defaults
- Advanced customization through pandas and matplotlib
- Table and chart exports and PDF reports combining generated visuals

## Installation

```bash
pip install tabloom
```

Python 3.12+ is required. pandas and matplotlib are installed automatically.

For the notebook dependencies:

```bash
pip install "tabloom[example]"
```

## Quick start

Import Tabloom and check its version:

```python
import tabloom

print(tabloom.__version__)
```

## Documentation

- [Installation](https://michalszc.github.io/tabloom/getting-started/installation/)
- [Quick start](https://michalszc.github.io/tabloom/getting-started/quickstart/)
- [Core concepts](https://michalszc.github.io/tabloom/getting-started/core-concepts/)
- [Guides](https://michalszc.github.io/tabloom/guides/)
- [API reference](https://michalszc.github.io/tabloom/reference/)

## Examples

| Example | Description | Notebook | Colab |
|---------|-------------|----------|-------|
| **Basic usage** | Import Tabloom and print its version | [basic_usage.ipynb](notebooks/basic_usage.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/michalszc/tabloom/blob/master/notebooks/basic_usage.ipynb) |

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup, quality checks, and
the release workflow. Issues and feature requests are welcome in the
[GitHub repository](https://github.com/michalszc/tabloom/issues).
