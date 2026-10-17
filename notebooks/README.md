# Notebooks

PrettyData 0.0.0 establishes the repository infrastructure. No example notebooks
are included because the library has no tables, charts, or report APIs yet.

Future examples belong here. Install their environment with the `example` extra.
Run `make notebooks-check` to validate saved notebooks without executing cells.
The validator requires `jq` on PATH and `nbformat` from the docs dependency group.

Each notebook must contain exactly one executed `prettydata.__version__` cell
with saved output matching the project version. Other code cells must have
execution counts and no stored errors. A `%pip install ...prettydata...` cell
must remain unexecuted with no saved output.

An empty notebook directory passes with an informational message. An explicitly
requested path that does not exist fails validation.
