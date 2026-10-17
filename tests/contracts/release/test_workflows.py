"""Contracts for deployment and release workflow boundaries."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).parents[3]
SHA = "a" * 40


def workflow(name: str) -> dict[str, Any]:
    """Read YAML without interpreting GitHub's `on` key as a boolean."""
    result: dict[str, Any] = yaml.load(
        (ROOT / ".github" / "workflows" / f"{name}.yml").read_text(),
        Loader=yaml.BaseLoader,
    )
    return result


def permits(guard: str, **fields: str) -> bool:
    """Evaluate the conjunction of equality guards used by these workflows."""
    clauses = guard.removeprefix("${{").removesuffix("}}").strip().split("&&")
    results = []
    for clause in clauses:
        match = re.fullmatch(
            r"\s*github\.event\.workflow_run\.([\w.]+) == "
            r"(?:'([^']+)'|(github\.repository))\s*",
            clause,
        )
        assert match is not None, f"Unsupported workflow guard: {clause}"
        field, literal, repository = match.groups()
        expected = "owner/repo" if repository else literal
        results.append(fields[field] == expected)
    return all(results)


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("conclusion", "success", True),
        ("conclusion", "failure", False),
        ("conclusion", "cancelled", False),
        ("conclusion", "skipped", False),
        ("event", "pull_request", False),
        ("head_branch", "feature/example", False),
        ("head_repository.full_name", "fork/repo", False),
    ],
)
def test_cd_guards(field: str, value: str, *, expected: bool) -> None:
    fields = {
        "conclusion": "success",
        "event": "push",
        "head_branch": "master",
        "head_repository.full_name": "owner/repo",
    }
    fields[field] = value
    assert permits(workflow("cd")["jobs"]["publish"]["if"], **fields) is expected


def test_cd_records_identity_before_publishing(tmp_path: Path) -> None:
    cd = workflow("cd")
    assert cd["on"]["workflow_run"] == {
        "workflows": ["CI"],
        "branches": ["master"],
        "types": ["completed"],
    }
    steps = cd["jobs"]["publish"]["steps"]
    assert steps[0]["with"]["ref"] == "${{ github.event.workflow_run.head_sha }}"
    names = [step.get("name", "") for step in steps]
    record = names.index("Record deployment identity")
    upload = names.index("Upload deployment identity")
    publish = names.index("Publish to PyPI")
    assert record < upload < publish
    assert steps[upload]["with"] == {
        "name": "release-metadata",
        "path": "release-metadata.json",
        "if-no-files-found": "error",
    }
    assert steps[names.index("Build package")]["run"] == "make build"
    assert steps[names.index("Check build")]["run"] == "make check-build"
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "prettydata"\nversion = "0.1.0"\n',
    )
    binary = tmp_path / "bin"
    binary.mkdir()
    git = binary / "git"
    git.write_text(f"#!/bin/sh\nprintf '%s\\n' '{SHA}'\n")
    git.chmod(0o755)
    assert steps[record]["run"] == "make release-metadata"
    assert (
        steps[record]["env"]["DEPLOYED_SHA"]
        == "${{ github.event.workflow_run.head_sha }}"
    )
    (tmp_path / "Makefile").write_text((ROOT / "Makefile").read_text())
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "release.py").write_text((ROOT / "scripts" / "release.py").read_text())
    environment = {**os.environ, "DEPLOYED_SHA": SHA}
    environment["PATH"] = f"{binary}:{ROOT / '.venv' / 'bin'}:{environment['PATH']}"
    result = subprocess.run(
        ["make", "release-metadata", f"PYTHON={sys.executable}"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads((tmp_path / "release-metadata.json").read_text()) == {
        "sha": SHA,
        "name": "prettydata",
        "version": "0.1.0",
    }
    environment["DEPLOYED_SHA"] = "b" * 40
    result = subprocess.run(
        ["make", "release-metadata", f"PYTHON={sys.executable}"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "Checkout does not match" in result.stderr

    # A local invocation needs no CI environment or network access.
    environment.pop("DEPLOYED_SHA")
    result = subprocess.run(
        [
            "make",
            "release-metadata",
            f"PYTHON={sys.executable}",
            "RELEASE_METADATA=local.json",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads((tmp_path / "local.json").read_text())["sha"] == SHA


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("conclusion", "success", True),
        ("conclusion", "failure", False),
        ("conclusion", "cancelled", False),
        ("conclusion", "skipped", False),
        ("head_branch", "feature/example", False),
        ("head_repository.full_name", "fork/repo", False),
    ],
)
def test_release_guards(field: str, value: str, *, expected: bool) -> None:
    fields = {
        "conclusion": "success",
        "head_branch": "master",
        "head_repository.full_name": "owner/repo",
    }
    fields[field] = value
    assert permits(workflow("release")["jobs"]["release"]["if"], **fields) is expected


def test_release_uses_metadata_from_exact_cd_run() -> None:
    release = workflow("release")
    assert release["on"] == {
        "workflow_run": {
            "workflows": ["CD"],
            "branches": ["master"],
            "types": ["completed"],
        },
    }
    assert release["concurrency"]["cancel-in-progress"] == "false"
    job = release["jobs"]["release"]
    assert job["permissions"] == {"actions": "read", "contents": "write"}
    steps = job["steps"]
    names = [step["name"] for step in steps]
    download = names.index("Download deployment identity")
    select = names.index("Select deployed commit")
    checkout = names.index("Check out deployed commit")
    publish = names.index("Publish GitHub release")
    assert download < select < checkout < publish
    assert steps[download]["with"]["run-id"] == "${{ github.event.workflow_run.id }}"
    assert steps[download]["with"]["repository"] == "${{ github.repository }}"
    assert steps[download]["with"]["name"] == "release-metadata"
    metadata_path = steps[download]["with"]["path"] + "/release-metadata.json"
    assert steps[select]["env"]["RELEASE_METADATA"] == metadata_path
    assert steps[publish]["env"]["RELEASE_METADATA"] == metadata_path
    assert steps[checkout]["with"]["ref"] == "${{ steps.deployment.outputs.sha }}"
    assert steps[checkout]["with"]["path"] == "deployed"
    assert steps[publish]["env"]["RELEASE_PROJECT"] == "deployed"
    assert steps[publish]["env"]["GH_TOKEN"] == "${{ secrets.GITHUB_TOKEN }}"
    assert steps[select]["run"] == "make release-select-commit"
    assert steps[publish]["run"] == "make release"
    assert not any("pip install" in step.get("run", "") for step in steps)


@pytest.mark.parametrize("name", ["ci", "cd", "release"])
def test_workflow_job_environment_uses_available_contexts(name: str) -> None:
    """Job env is evaluated before runner and step contexts are available.

    GitHub's context-availability table allows these seven contexts at job env:
    https://docs.github.com/en/actions/reference/workflows-and-actions/contexts
    """
    available = {"github", "needs", "strategy", "matrix", "vars", "secrets", "inputs"}
    for job in workflow(name)["jobs"].values():
        for value in job.get("env", {}).values():
            for expression in re.findall(r"\$\{\{(.*?)\}\}", value):
                contexts = set(re.findall(r"(?<![\w.])([a-z_]\w*)\.", expression))
                assert contexts <= available, (
                    f"Unavailable contexts in {name} job env: {contexts - available}"
                )


def test_ci_checks_release_automation_changes() -> None:
    ci = workflow("ci")
    for event in ("push", "pull_request"):
        assert {
            ".github/workflows/cd.yml",
            ".github/workflows/release.yml",
            "scripts/release.py",
            "documentation/release-notes.md",
        } <= set(ci["on"][event]["paths"])
    checks = ci["jobs"]["quality-checks"]["strategy"]["matrix"]["check"]
    assert {"lint", "format-check", "type-check", "test"} <= set(checks)
    makefile = (ROOT / "Makefile").read_text()
    assert "ruff check src/ tests/ scripts/" in makefile
    assert "ruff format --diff src/ tests/ scripts/" in makefile
    assert "mypy src/prettydata/ tests/ scripts/" in makefile
    assert "pytest $(TEST_PATH) $(PYTEST_ARGS)" in makefile


def test_ci_keeps_quality_and_compatibility_separate() -> None:
    ci = workflow("ci")
    assert set(ci["jobs"]) == {"quality-checks", "python-compatibility"}
    assert ci["jobs"]["quality-checks"]["strategy"]["matrix"]["check"] == [
        "lint",
        "format-check",
        "type-check",
        "test",
        "validate-version",
    ]
    compatibility = ci["jobs"]["python-compatibility"]
    assert compatibility["strategy"]["matrix"]["python-version"] == ["3.13", "3.14"]


def test_cd_publishes_with_make_and_twine() -> None:
    cd = workflow("cd")
    assert set(cd["jobs"]) == {"publish"}
    steps = cd["jobs"]["publish"]["steps"]
    publish = next(step for step in steps if step.get("name") == "Publish to PyPI")
    assert publish["run"] == "make ci-publish"
    assert publish["env"] == {
        "TWINE_USERNAME": "__token__",
        "TWINE_PASSWORD": "${{ secrets.PYPI_API_TOKEN }}",
    }


def test_docs_configures_and_uploads_pages_during_build() -> None:
    docs = workflow("docs")
    build = docs["jobs"]["build"]["steps"]
    names = [step.get("name", "") for step in build]
    assert names.index("Generate documentation") < names.index("Setup Pages")
    assert names.index("Setup Pages") < names.index("Upload artifact")
    for name in ("Setup Pages", "Upload artifact"):
        assert build[names.index(name)]["if"] == "github.event_name == 'push'"
    deploy = docs["jobs"]["deploy"]
    assert deploy["needs"] == "build"
    assert deploy["if"] == "github.event_name == 'push'"
    assert [step["name"] for step in deploy["steps"]] == ["Deploy to GitHub Pages"]


@pytest.mark.parametrize("name", ["ci", "cd", "docs", "notebooks"])
def test_workflows_install_through_make(name: str) -> None:
    steps = [step for job in workflow(name)["jobs"].values() for step in job["steps"]]
    installs = [step for step in steps if "Install" in step.get("name", "")]
    assert installs
    assert all(step["run"].startswith("make install") for step in installs)
    for step in installs:
        if step["run"].startswith("make install-dev"):
            assert "INSTALL_HOOKS=0" in step["run"]


@pytest.mark.parametrize("install_hooks", ["0", "1"])
def test_development_install_can_skip_hooks(install_hooks: str) -> None:
    """Inspect the Make recipe without installing dependencies or changing hooks."""
    result = subprocess.run(
        [
            "make",
            "--dry-run",
            "install-dev",
            f"INSTALL_HOOKS={install_hooks}",
            f"PYTHON={sys.executable}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--group dev" in result.stdout
    assert ("pre_commit install" in result.stdout) is (install_hooks == "1")


def test_workflows_use_make_for_summary_checks() -> None:
    ci = workflow("ci")
    steps = ci["jobs"]["quality-checks"]["steps"]
    assert steps[-1]["run"] == 'make ci-check CHECK="${{ matrix.check }}"'
    assert ci["jobs"]["python-compatibility"]["steps"][-1]["run"] == (
        "make ci-check CHECK=test"
    )
    assert workflow("notebooks")["jobs"]["validate"]["steps"][-1]["run"] == (
        "make ci-check CHECK=notebooks-check"
    )


@pytest.mark.parametrize("exit_code", [0, 1])
def test_make_ci_check_runs_locally_and_preserves_failure(
    tmp_path: Path, exit_code: int
) -> None:
    """Exercise the Make wrapper with a controlled check and no GitHub environment."""
    real_make = shutil.which("make")
    assert real_make is not None
    (tmp_path / "Makefile").write_text((ROOT / "Makefile").read_text())
    scripts = tmp_path / "scripts" / "ci"
    scripts.mkdir(parents=True)
    (scripts / "run_check.sh").write_text(
        (ROOT / "scripts" / "ci" / "run_check.sh").read_text(),
    )
    binary = tmp_path / "bin"
    binary.mkdir()
    make = binary / "make"
    make.write_text(f"#!/bin/sh\necho fixture-check-output\nexit {exit_code}\n")
    make.chmod(0o755)
    environment = {**os.environ, "PATH": f"{binary}:{os.environ['PATH']}"}
    environment.pop("GITHUB_STEP_SUMMARY", None)
    result = subprocess.run(
        [real_make, "ci-check", "CHECK=lint"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert (result.returncode == 0) is (exit_code == 0), result.stderr
    assert ("✅" if exit_code == 0 else "❌") in result.stdout
    if exit_code:
        assert "fixture-check-output" in result.stdout


@pytest.mark.parametrize("exit_code", [0, 1])
def test_make_ci_publish_reports_mocked_upload(tmp_path: Path, exit_code: int) -> None:
    """Test the publishing wrapper with a fake Make upload; never invoke Twine."""
    real_make = shutil.which("make")
    assert real_make is not None
    (tmp_path / "Makefile").write_text((ROOT / "Makefile").read_text())
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "prettydata"\nversion = "0.1.0"\n',
    )
    scripts = tmp_path / "scripts" / "ci"
    scripts.mkdir(parents=True)
    (scripts / "publish.sh").write_text(
        (ROOT / "scripts" / "ci" / "publish.sh").read_text(),
    )
    binary = tmp_path / "bin"
    binary.mkdir()
    make = binary / "make"
    make.write_text(
        '#!/bin/sh\nprintf "%s\\n" "$*" >> publish-called\n'
        'echo "Response from https://upload.pypi.org/legacy/:"\n'
        'echo "400 Bad Request: fixture rejection reason"\n'
        f"exit {exit_code}\n",
    )
    make.chmod(0o755)
    summary = tmp_path / "summary.md"
    result = subprocess.run(
        [real_make, "ci-publish", f"PYTHON={sys.executable}"],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": f"{binary}:{os.environ['PATH']}",
            "GITHUB_STEP_SUMMARY": str(summary),
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert (result.returncode == 0) is (exit_code == 0), result.stderr
    assert (tmp_path / "publish-called").read_text().splitlines() == [
        "publish TWINE_UPLOAD_ARGS=--verbose --non-interactive --disable-progress-bar",
    ]
    content = summary.read_text()
    if exit_code == 0:
        assert "Package published successfully" in content
        assert "https://pypi.org/project/prettydata/0.1.0/" in content
    else:
        assert "Publishing failed" in content
        assert "400 Bad Request: fixture rejection reason" in content
        assert "400 Bad Request: fixture rejection reason" in result.stdout
        assert "Package published successfully" not in content
