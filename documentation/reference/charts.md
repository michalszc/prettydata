# Charts API

Factory options shared by all chart types: `data`, `title`, `xlabel`, `ylabel`,
`theme="default"`, `figsize=(7, 4.5)`, and `font_size=11`. Remaining keywords are
passed to matplotlib. See [chart examples](../guides/charts.md).

::: tabloom.chart
    options:
      show_root_heading: true
      show_root_full_path: true
      show_root_members_full_path: false
      merge_init_into_class: true
      separate_signature: true
      show_signature_annotations: true
      filters: ["!^_"]
