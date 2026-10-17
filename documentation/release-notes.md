# Release Notes

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
