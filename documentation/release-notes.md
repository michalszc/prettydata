# Release Notes

## 0.1.0 — Unreleased

-  Added shared visual themes and scoped matplotlib rendering foundations in
  [PR #5](https://github.com/michalszc/tabloom/pull/5).
- Added editable DataFrame-backed tables, data imports/exports, and themed
  PNG/PDF/SVG rendering.
- Added line, bar, scatter, histogram, box, and pie charts with shared themes,
  pandas/Table inputs, matplotlib customization, and graphical exports.
- Added ordered PDF reports with flowing text, reusable tables/charts,
  automatic pagination, and explicit page breaks without external LaTeX.
- Added executable quick-start documentation, a complete API reference, and
  an executed example notebook.
- Excel support targets `.xlsx`; report visuals remain intact blocks.
  Complex document layout and table-row pagination remain outside this release.

- Organized implementation into focused feature packages, with at most one
  top-level class or function per module and documented internal responsibilities.

- Split API reference and workflow guides into separate table, chart, report,
  data, theme, and export areas with concise overview maps.

- Made Table.show and Chart.show display figures directly in notebooks without
  intermediate image files, and refreshed the executed example notebook.

- Standardized PDF report paper size (A4 by default) with configurable dimensions
  and margins, preserving vector visuals and the original chart layouts.
- Promoted the existing pypdf dependency to runtime for vector page composition.

- Made report content fill remaining page space in order, with inline titles,
  text continuation, and optional add_page_break boundaries.

## 0.0.0 — 2026-10-17

- Established the minimal typed package, development tooling, smoke tests,
  version validation, and deployment-identity release tooling in
  [PR #1](https://github.com/michalszc/tabloom/pull/1).
- This is the repository foundation milestone. Tables, charts, and reports
  are planned for future development.
- Prepared static notebook validation without introducing demonstration notebooks
  for features that have not been implemented.
- Added strict MkDocs Material documentation, mkdocstrings API infrastructure,
  development instructions, and contributor/release guidance.
- Added CI quality and Python 3.12–3.14 compatibility checks, separate static
  notebook and documentation workflows, GitHub Pages, Twine publishing,
  GitHub releases, and stale issue/PR maintenance.
- Exposed the shared CI check summaries through `make ci-check CHECK=...`.
- Added a basic usage notebook that imports PrettyData and prints its version,
  linked from the README and documentation examples.
