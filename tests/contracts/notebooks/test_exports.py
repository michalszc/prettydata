"""Notebook exports are ignored without hiding sources or project assets."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[3]


def test_generated_notebook_exports_are_ignored() -> None:
    """Ignore common exports and arbitrary output files while retaining sources."""
    ignored = [
        "notebooks/experiment_report.pdf",
        "notebooks/chart.png",
        "notebooks/chart.svg",
        "notebooks/results.csv",
        "notebooks/results.tsv",
        "notebooks/results.xls",
        "notebooks/results.xlsx",
        "notebooks/results.xlsm",
        "notebooks/results.xlsb",
        "notebooks/results.ods",
        "notebooks/results.json",
        "notebooks/results.jsonl",
        "notebooks/results.parquet",
        "notebooks/results.feather",
        "notebooks/results.pkl",
        "notebooks/results.pickle",
        "notebooks/outputs/nested/custom-format.anything",
        "notebooks/data/winequality-red.csv",
    ]
    retained = [
        "notebooks/wine_quality_report.ipynb",
        "assets/illustration.png",
        "tests/fixture.csv",
    ]
    result = subprocess.run(
        [
            "git",
            "-c",
            "core.excludesFile=/dev/null",
            "check-ignore",
            "--no-index",
            "--stdin",
        ],
        cwd=ROOT,
        input="\n".join([*ignored, *retained]) + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.splitlines() == ignored
