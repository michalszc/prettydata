# PrettyData

<p align="center">
  <a href="https://pypi.org/project/prettydata/"><img src="https://img.shields.io/pypi/v/prettydata" alt="PyPI version"></a>
  <a href="https://pypi.org/project/prettydata/"><img src="https://img.shields.io/pypi/dm/prettydata" alt="PyPI monthly downloads"></a>
  <a href="https://github.com/michalszc/prettydata/blob/master/pyproject.toml"><img src="https://img.shields.io/badge/python-3.12%2B-important" alt="Python 3.12 or newer"></a>
  <a href="https://github.com/michalszc/prettydata/actions/workflows/ci.yml"><img src="https://github.com/michalszc/prettydata/actions/workflows/ci.yml/badge.svg?branch=master" alt="CI on master"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License: Apache 2.0"></a>
  <a href="https://michalszc.github.io/prettydata/"><img src="https://img.shields.io/badge/docs-online-blue.svg" alt="Docs"></a>
</p>

A Python library for visually appealing tables, charts, and reports with minimal
configuration.

Designed around pandas and matplotlib, PrettyData aims to combine sensible visual
defaults with access to the underlying libraries for advanced customization.

## Features

PrettyData provides:

- Convenient tabular data creation, rows, and records
- Dataset imports from CSV, Excel, JSON, and other formats
- Integration with pandas for data manipulation
- Attractive tables and matplotlib charts with sensible defaults
- Advanced customization through pandas and matplotlib
- Table and chart exports and PDF reports combining generated visuals

## Installation

```bash
pip install prettydata
```

Python 3.12+ is required. pandas and matplotlib are installed automatically.

For the notebook dependencies:

```bash
pip install "prettydata[example]"
```

## Quick start

Import PrettyData and check its version:

```python
import prettydata

print(prettydata.__version__)
```

## Documentation

- [Installation](https://michalszc.github.io/prettydata/getting-started/installation/)
- [Quick start](https://michalszc.github.io/prettydata/getting-started/quickstart/)
- [Core concepts](https://michalszc.github.io/prettydata/getting-started/core-concepts/)
- [Guides](https://michalszc.github.io/prettydata/guides/)
- [API reference](https://michalszc.github.io/prettydata/reference/)

## Examples

| Example | Description | Notebook | Colab |
|---------|-------------|----------|-------|

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup, quality checks, and
the release workflow. Issues and feature requests are welcome in the
[GitHub repository](https://github.com/michalszc/prettydata/issues).
