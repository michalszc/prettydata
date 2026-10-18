"""Package import remains usable without notebook/development tools or side effects."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[3]


def test_import_does_not_require_optional_tools_or_create_figures(
    tmp_path: Path,
) -> None:
    """Check a fresh interpreter so pytest's imported modules cannot mask failures."""
    environment = os.environ.copy()
    environment.update(
        PYTHONPATH=str(ROOT / "src"),
        MPLBACKEND="Agg",
        MPLCONFIGDIR=str(tmp_path / "matplotlib-cache"),
    )
    working = tmp_path / "work"
    working.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt

before = dict(mpl.rcParams)
backend = mpl.get_backend()
for name in ('IPython', 'ipykernel', 'ipywidgets', 'nbformat', 'mkdocs', 'pytest'):
    sys.modules[name] = None
import tabloom

assert set(tabloom.__all__) >= {'Table', 'Chart', 'Report'}
assert not plt.get_fignums()
assert dict(mpl.rcParams) == before
assert mpl.get_backend() == backend
assert not list(Path.cwd().iterdir())
""",
        ],
        cwd=working,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert not result.stdout
