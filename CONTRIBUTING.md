# Contributing to PrettyData

PrettyData 0.0.0 is a repository infrastructure milestone. Feature development
will follow; proposals should not assume an existing table, chart, or report API.

## Development environment

Prerequisites: Python 3.12+, pip 25.1+ (dependency group support), Git, and `jq`
for notebook validation. Release publication additionally uses GitHub CLI.

Clone `https://github.com/michalszc/prettydata.git` and enter the checkout. Use
the existing `.venv`; new contributors can create one with
`python3.12 -m venv .venv` if needed.

```bash
source .venv/bin/activate
make install-dev
```

This installs the editable package, `all` extras, and `dev` dependency group,
then installs pre-commit hooks. The first commit may download hook environments.
Use `make install-dev INSTALL_HOOKS=0` to skip hook installation, as the CI jobs do.
The `example` extra supplies notebook kernel and widget support. No alternative
package manager or lockfile is required.

## Development workflow

1. Create a branch such as `feature/your-feature-name`.
2. Make focused changes and add appropriate tests.
3. Run the checks below and fix failures before committing.
4. Use a conventional commit, such as `fix: correct version validation`.
5. Push your branch and open a PR targeting `master`, explaining the behavior,
   validation, and any infrastructure changes.

```bash
make lint
make format-check
make type-check
make test
make validate-version VALIDATE_VERSION_ARGS=--offline
make docs
make notebooks-check
```

`make validate-version` without the offline argument also compares with PyPI.
Only an actual HTTP 404 is treated as a first release; network and service
failures fail the online check.

Use `make lint-fix` and `make format` to apply fixes. Ruff and mypy cover source,
tests, and Python maintenance scripts. Pytest uses strict discovery and markers,
terminal coverage, and an HTML report in `htmlcov/`. The threshold is 97%.
The initial package only has metadata, so coverage does not indicate features.

```bash
make test-verbose
make test TEST_PATH=tests/contracts/package/test_package.py
make test PYTEST_ARGS="-k import"
pre-commit run --all-files
```

Pre-commit checks whitespace, final newlines, YAML, large files, merge conflicts,
debug statements, and Ruff linting/formatting. CLI and hook Ruff versions match.

The workflows run the shared summary script through Make:

```bash
make ci-check CHECK=lint
make ci-check CHECK=test
make ci-check CHECK=notebooks-check
make ci-check CHECK=validate-version VALIDATE_VERSION_ARGS=--offline
```

`CHECK` defaults to `test` and also accepts `format-check` and `type-check`.
Summaries go to `GITHUB_STEP_SUMMARY` in Actions and to the terminal locally.
The underlying check's output is saved in its `*_output.txt` file.

## Repository organization

- `src/prettydata/`: importable package and PEP 561 typed marker.
- `tests/contracts/`: package and repository infrastructure tests.
- `documentation/`: MkDocs sources, API templates, and release notes.
- `docs/`: generated site, ignored by Git.
- `notebooks/`: future examples and saved-output validation guidance.
- `assets/`: future project assets.
- `scripts/`: version, notebook, release, and CI-summary tooling.
- `.github/workflows/`: CI, CD, documentation, notebooks, releases, and maintenance.

## Documentation and notebooks

`make docs` builds with strict MkDocs checks. `make docs-serve` starts a local
preview at `http://127.0.0.1:8000`; stop it with Ctrl+C. Document current behavior
and expose real APIs through mkdocstrings as they are added.

`make notebooks-check` validates saved outputs without executing cells. There are
no demonstration notebooks yet. Future examples must record the current version,
execution counts, and error-free outputs. Installation cells remain unexecuted.
An empty directory passes; invalid requested paths fail.

If a documentation build fails in `Highlight.__init__`, reinstall the constrained
docs toolchain with `python -m pip install -e . --group docs`. The current
mkdocstrings version requires `pymdown-extensions>=10,<12`.

## Maintenance commands

`make help` lists all targets. `make build` creates wheel/sdist distributions;
`make check-build` validates them with Twine. `make clean` removes generated
package, coverage, cache, and documentation artifacts while preserving `.venv`.

Manual uploads use `make publish-test` and `make publish`. These are publishing
operations requiring intentional authentication. Ordinary checks never invoke them.
CD uses `make ci-publish`, which runs `scripts/ci/publish.sh` around `make publish`
to preserve the publishing success/failure summary. It is also a publishing
operation, not a validation command.

## Release process

The automated sequence is **CI → CD → Release**.

1. Update the version in both `pyproject.toml` and `src/prettydata/__init__.py`
   for source changes. Keep the values equal.
2. Add exactly one nonempty `## <version> — <date or Unreleased>` section in
   `documentation/release-notes.md`, linking the corresponding PR.
3. Run quality, test, docs, notebook, and version checks. Maintainers also validate
   distribution builds before release.
4. Merge the reviewed PR to `master`. Successful push CI triggers CD for that
   exact commit. CD builds/checks distributions, records deployment identity,
   and publishes through `make ci-publish` using the `PYPI_API_TOKEN` secret.
5. Successful CD triggers Release, which downloads metadata from the exact CD run,
   checks out the deployed SHA, validates name/version, and creates `v<version>`
   with curated notes and a version-specific PyPI link.

Infrastructure-only follow-up commits may retain the current version. The
initial bootstrap establishes 0.0.0 once; it implements no feature APIs.

### Local release tooling

```bash
make release-metadata
make release-metadata RELEASE_METADATA=/tmp/prettydata-release-metadata.json
```

Metadata records `sha`, `name`, and `version`. CD also supplies `DEPLOYED_SHA`
to verify the checkout. The default `release-metadata.json` is ignored by Git.
Recording metadata does not build or publish anything.

`make release-select-commit` validates metadata and writes its SHA to
`GITHUB_OUTPUT`; it does not check out code. `make release` publishes through
GitHub CLI, requiring authentication and matching metadata. `RELEASE_METADATA`
selects the file, `RELEASE_PROJECT` selects the deployed checkout, and
`RELEASE_REPOSITORY` or `GITHUB_REPOSITORY` specifies the owner/repository.

### Configuration and recovery

Maintainers must configure GitHub Pages, the `PYPI_API_TOKEN` repository secret,
and repository token permissions. Workflow chaining becomes active once these
files exist on the default branch. No external credentials are committed.

For GitHub release failures after PyPI publication, rerun the failed Release job
while its CD metadata artifact is available. Avoid rerunning CD solely to recover
a GitHub release: the package version is already published. Retries skip an
existing published release at the same commit. Conflicting tags, draft releases,
mismatched metadata, and unavailable artifacts fail for maintainer review.
Automation never moves tags or overwrites releases. GitHub supplies tag source
archives; package wheels and sdists remain on PyPI.

## Repository configuration for maintainers

The following settings are configured manually outside the repository:

- **GitHub Pages:** choose **GitHub Actions** in Settings → Pages. Configure the
  `github-pages` environment to allow deployments from `master`. `docs.yml`
  builds PR documentation and deploys only pushes to `master`.
- **PyPI:** configure a project-scoped API token for `prettydata` as the repository
  Actions secret `PYPI_API_TOKEN`. CD passes it to Twine as `TWINE_PASSWORD`, with
  `TWINE_USERNAME=__token__`, and runs `make publish`.
- **GitHub Releases:** permit the Release job's `actions: read` and
  `contents: write` permissions under repository/organization policies. It uses
  the automatic `GITHUB_TOKEN`; no separate PAT is required for GitHub releases.
- **Maintenance:** the scheduled workflow uses the `no-activity` label for stale
  issues and PRs. Create that label if it is not present. The policy marks items
  after 90 inactive days and closes them after another 30 days.

The first workflow chain must be checked after the workflow files reach the default
branch. CI runs quality checks and tests on Python 3.12; a separate
`python-compatibility` job tests Python 3.13 and 3.14. Documentation and notebooks
have their own workflows. Regular PRs cannot publish packages or deploy Pages.
CD builds and checks distributions from the exact successful CI commit, records
and uploads metadata, and publishes through Twine. Release retrieves metadata
from that specific CD run.

Workflow dependency installation uses `make install-dev INSTALL_HOOKS=0`, or `make install` with
`INSTALL_ARGS='--group docs'` / `INSTALL_ARGS='--group build'`. These use the
same pip groups as local development. `make publish-test` remains available for
manual TestPyPI uploads.

## Code style and contributions

Use type hints, descriptive names, and public API docstrings. Keep changes focused,
test meaningful behavior, and update documentation and release notes. Avoid
speculative feature abstractions. Preserve licenses and third-party attribution.
