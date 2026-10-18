# API Reference

This reference is generated from Tabloom's public docstrings by mkdocstrings.
Each area has its own page for constructors, methods, options, and output
behavior. For complete task-oriented examples, start with the [guides](../guides/index.md).

## Reference map

| Area | Page | Main public API |
| --- | --- | --- |
| Tabular data | [Tables](tables.md) | `Table`: construction, editing, loading, rendering, and export |
| Visualization | [Charts](charts.md) | `Chart`: six factories, customization, display, and export |
| PDF composition | [Reports](reports.md) | `Report`: ordered text, table, and chart pages |
| Visual defaults | [Themes](themes.md) | `default`, `light`, and `dark`; supported style options |

## Public imports

```python
from tabloom import Chart, Report, Table
```

Applications should use the package root or the documented `tabloom.table`,
`tabloom.chart`, and `tabloom.report` packages. Private helper modules are
implementation details. Version and author metadata are available through
`tabloom.__version__` and `tabloom.__author__`.
