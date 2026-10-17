"""Offline integration tests for local and PyPI version validation."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[3]
VALIDATOR = ROOT / "scripts" / "validate_version.sh"


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """Create a minimal package and a controlled substitute for curl."""
    package = tmp_path / "src" / "prettydata"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('__version__ = "0.1.0"\n')
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "prettydata"\nversion = "0.1.0"\n',
    )
    notes = tmp_path / "documentation"
    notes.mkdir()
    (notes / "release-notes.md").write_text("## 0.1.0 — Unreleased\n\n- Foundation.\n")
    binary = tmp_path / "bin"
    binary.mkdir()
    curl = binary / "curl"
    curl.write_text(
        f"#!{sys.executable}\n"
        "import os, sys\nfrom pathlib import Path\n"
        "Path('curl-called').touch()\n"
        "if os.environ.get('PYPI_STATUS') == 'network': sys.exit(7)\n"
        "Path(sys.argv[sys.argv.index('--output') + 1]).write_text(\n"
        '    os.environ.get(\'PYPI_BODY\', \'{"info": {"version": "0.0.1"}}\'))\n'
        "print(os.environ.get('PYPI_STATUS', '200'), end='')\n",
    )
    curl.chmod(0o755)
    return tmp_path


def validate(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Invoke the shell entry point without any real network access."""
    environment = {
        **os.environ,
        "PYTHON": sys.executable,
        "PATH": f"{project / 'bin'}:{os.environ['PATH']}",
    }
    return subprocess.run(
        ["bash", str(VALIDATOR), *args],
        cwd=project,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_offline_validation_never_contacts_pypi(project: Path) -> None:
    result = validate(project, "--offline")
    assert result.returncode == 0, result.stderr
    assert not (project / "curl-called").exists()


@pytest.mark.parametrize(
    ("notes", "error"),
    [
        ("## 0.0.1\n- Old.\n", "is missing"),
        ("## 0.1.0\n- One.\n## 0.1.0\n- Two.\n", "multiple times"),
        ("## 0.1.0\n\n## 0.0.1\n- Old.\n", "Empty release-notes section"),
    ],
)
def test_invalid_notes(project: Path, notes: str, error: str) -> None:
    (project / "documentation" / "release-notes.md").write_text(notes)
    result = validate(project, "--offline")
    assert result.returncode != 0
    assert error in result.stderr


def test_missing_notes(project: Path) -> None:
    (project / "documentation" / "release-notes.md").unlink()
    result = validate(project, "--offline")
    assert result.returncode != 0
    assert "not found" in result.stderr


def test_version_mismatch(project: Path) -> None:
    (project / "src" / "prettydata" / "__init__.py").write_text(
        '__version__ = "0.2.0"\n',
    )
    result = validate(project, "--offline")
    assert result.returncode != 0
    assert "Version mismatch" in result.stderr


@pytest.mark.parametrize(
    "response",
    [
        ("404", "{}", 0, "first release?"),
        ("200", '{"info": {"version": "0.0.1"}}', 0, "All checks passed"),
        ("200", '{"info": {"version": "0.1.0"}}', 1, "Version matches PyPI"),
        ("200", "not-json", 1, "JSONDecodeError"),
        ("503", "{}", 1, "HTTP 503"),
        ("network", "{}", 1, "Could not contact PyPI"),
    ],
)
def test_pypi_responses(
    project: Path,
    monkeypatch: pytest.MonkeyPatch,
    response: tuple[str, str, int, str],
) -> None:
    status, body, expected, message = response
    monkeypatch.setenv("PYPI_STATUS", status)
    monkeypatch.setenv("PYPI_BODY", body)
    result = validate(project)
    assert result.returncode == expected
    assert message in result.stdout + result.stderr


def test_rejects_unknown_arguments(project: Path) -> None:
    assert validate(project, "--unknown").returncode == 2
