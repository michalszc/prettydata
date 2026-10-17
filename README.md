# PrettyData

<p align="center">
  <a href="https://pypi.org/project/prettydata/"><img src="https://img.shields.io/pypi/v/prettydata" alt="PyPI version"></a>
  <a href="https://pypi.org/project/prettydata/"><img src="https://img.shields.io/pypi/dm/prettydata" alt="PyPI monthly downloads"></a>
  <a href="https://github.com/michalszc/prettydata/blob/master/pyproject.toml"><img src="https://img.shields.io/badge/python-3.12%2B-important" alt="Python 3.12 or newer"></a>
  <a href="https://github.com/michalszc/prettydata/actions/workflows/ci.yml"><img src="https://github.com/michalszc/prettydata/actions/workflows/ci.yml/badge.svg?branch=master" alt="CI on master"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License: Apache 2.0"></a>
  <a href="https://michalszc.github.io/prettydata/"><img src="https://img.shields.io/badge/docs-online-blue.svg" alt="Docs"></a>
</p>

A Python library being developed for visually appealing tables, charts, and
reports with minimal configuration.

## Development status

**v0.0.0 — Repository Foundation** establishes packaging, development tooling,
tests, documentation, and release infrastructure. The package can be imported;
table, chart, and report functionality has not been implemented.

## Planned scope

- Convenient tabular data creation, rows, and records.
- CSV, Excel, JSON, and other dataset imports with pandas integration.
- Attractive tables and matplotlib charts with sensible defaults.
- Advanced customization through underlying pandas and matplotlib objects.
- Exporting tables and charts and combining them into PDF reports.

These are future capabilities. No feature API is available in this milestone.

## Installation

Python 3.12+ is required. Install from PyPI:

```bash
pip install prettydata
```

The initial dependencies are pandas and matplotlib. Verify installation with:

```python
import prettydata

print(prettydata.__version__)
```

The PyPI distribution and Python import names are both `prettydata`.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup, quality checks, and
the release workflow. Issues and feature requests are welcome in the
[GitHub repository](https://github.com/michalszc/prettydata/issues).

## Documentation

- [Documentation site](https://michalszc.github.io/prettydata/) — available after GitHub Pages deployment.
- [Installation](documentation/getting-started/installation.md).
- [Quick start](documentation/getting-started/quickstart.md).
- [Guides](documentation/guides/index.md).
- [API reference](documentation/reference/index.md).
- [Examples](documentation/examples.md).
- [Troubleshooting](documentation/troubleshooting.md).
- [Release notes](documentation/release-notes.md).

Build locally with `make docs` or preview with `make docs-serve`.

## License

PrettyData is licensed under [Apache License 2.0](LICENSE). See [NOTICE](NOTICE)
for copyright and attribution, including reused repository infrastructure.
