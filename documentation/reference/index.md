# API Reference

The primary public API consists of `Table`, `Chart`, and `Report`, imported from
`tabloom`. Version and author metadata remain available as `__version__` and
`__author__`.

## Table

::: tabloom.Table
    options:
      show_root_heading: false
      merge_init_into_class: true
      members:
        - from_dataframe
        - from_csv
        - from_excel
        - from_json
        - add_row
        - add_rows
        - add_column
        - update_row
        - remove_row
        - rename_column
        - to_dataframe
        - to_csv
        - to_excel
        - to_json
        - render
        - show
        - save

## Chart

Factory options shared by all chart types: `data`, `title`, `xlabel`, `ylabel`,
`theme="default"`, `figsize=(7, 4.5)`, and `font_size=11`. Remaining keywords are
passed to matplotlib. See [chart examples](../guides/index.md#create-charts).

::: tabloom.Chart
    options:
      show_root_heading: false
      members:
        - line
        - bar
        - scatter
        - hist
        - box
        - pie
        - show
        - save

## Report

::: tabloom.Report
    options:
      show_root_heading: false
      merge_init_into_class: true
      members:
        - add_text
        - add_table
        - add_chart
        - save
