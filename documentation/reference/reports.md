# Reports API

Content fills the remaining page space in insertion order. Use `add_page_break()`
for an explicit boundary. `add_text` exposes typography and spacing; `add_table`
and `add_chart` accept `resize="full"` (default), width fractions, or `"original"`.
`add_table` paginates long tables automatically; `paginate=False` fits one block.
See the [report guide](../guides/reports.md) for styled text, visual sizing,
automatic pagination, paper settings, and cover-page examples.

::: tabloom.report
    options:
      show_root_heading: true
      show_root_full_path: true
      show_root_members_full_path: false
      merge_init_into_class: true
      separate_signature: true
      show_signature_annotations: true
      filters: ["!^_"]
