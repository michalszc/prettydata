"""Run the large-data notebook offline and verify its complete vector appendix."""

import json
import re
import subprocess
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure
from pypdf import PdfReader

ROOT = Path(__file__).parents[1]


def test_large_notebook_download_cache_and_complete_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exercise 1,599 rows without network access or committed dataset files."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Figure, "show", lambda fig: None)
    row = np.arange(1599)
    fixture = pd.DataFrame(
        {
            "fixed acidity": 7 + row % 20 / 10,
            "volatile acidity": 0.2 + row % 80 / 100,
            "citric acid": row % 50 / 100,
            "residual sugar": 1 + row % 30 / 10,
            "chlorides": 0.04 + row % 30 / 1000,
            "free sulfur dioxide": 5 + row % 40,
            "total sulfur dioxide": 20 + row % 100,
            "density": (0.99 + row % 80 / 10000).round(5),
            "pH": 3 + row % 50 / 100,
            "sulphates": 0.3 + row % 70 / 100,
            "alcohol": 9 + row % 50 / 10,
            "quality": 3 + row % 6,
        }
    ).round(5)
    csv = fixture.to_csv(index=False, sep=";").encode()
    downloads: list[str] = []

    def download(url: str, *, timeout: float) -> BytesIO:
        assert timeout == 30
        downloads.append(url)
        return BytesIO(csv)

    monkeypatch.setattr("urllib.request.urlopen", download)
    notebook = json.loads(
        (ROOT / "notebooks" / "wine_quality_report.ipynb").read_text()
    )
    rich_outputs = [
        output
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
        for output in cell["outputs"]
        if "image/png" in output.get("data", {})
    ]
    assert len(rich_outputs) == 4
    namespace: dict[str, Any] = {}
    sources = [
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    ]
    for source in sources:
        assert "plt.close" not in source
        exec(compile(source, "wine_quality_report.ipynb", "exec"), namespace)
    assert downloads == [
        "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
    ]
    assert namespace["wines"].df.shape == (1599, 12)
    assert namespace["display_data"].shape == (1599, 13)
    # Rerunning the download cell uses the cache rather than another request.
    download_cell = next(source for source in sources if "DATA_URL =" in source)
    exec(compile(download_cell, "wine_quality_report.ipynb", "exec"), namespace)
    assert len(downloads) == 1
    assert len(namespace["scatter"].fig.axes) == 2  # Includes the colorbar.
    assert len(namespace["box"].ax.patches) == 6
    assert len(namespace["histogram"].ax.get_legend().texts) == 2

    reader = PdfReader(tmp_path / "outputs" / "wine_quality_report.pdf")
    assert len(reader.pages) == 54
    for page in reader.pages:
        assert float(page.mediabox.width) == pytest.approx(11.69 * 72)
        assert float(page.mediabox.height) == pytest.approx(8.27 * 72)
    row_numbers: list[int] = []
    for index, page in enumerate(reader.pages[4:]):
        assert not page.images
        start = index * 32 + 1
        stop = min(start + 31, 1599)
        text = page.extract_text(extraction_mode="layout")
        assert f"rows {start}-{stop} of 1599" in text
        assert "Chlorides" in text
        assert "Quality" in text
        row_numbers.extend(
            int(number) for number in re.findall(r"^\s*(\d+)\s+\d", text, re.MULTILINE)
        )
    assert row_numbers == list(range(1, 1600))
    for name in ("scatter", "histogram", "box"):
        path = tmp_path / "outputs" / f"wine_quality_{name}.png"
        assert path.read_bytes().startswith(b"\x89PNG")


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
