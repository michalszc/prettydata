"""Execute the Excel notebook offline with real workbook reads and exports."""

import json
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure
from pypdf import PdfReader

ROOT = Path(__file__).parents[1]


@pytest.fixture
def financial_sample() -> tuple[pd.DataFrame, bytes]:
    """Create a small workbook matching the selected source-sheet schema."""
    row = np.arange(700)
    fixture = pd.DataFrame(
        {
            "Segment": "Government",
            "Country": np.array(["Canada", "France", "Germany"])[row % 3],
            "Product": np.array(
                ["Paseo", "VTT", "Velo", "Amarilla", "Carretera", "Montana"]
            )[row % 6],
            "Discount Band": "None",
            "Units Sold": 100 + row % 50,
            "Manufacturing Price": 3,
            "Sale Price": 20,
            "Gross Sales": 2000 + row * 100,
            "Discounts": 0,
            " Sales ": 2000.25 + row * 100.5,
            "COGS": 1000,
            "Profit": 1000.25 + row * 100.5,
            "Date": pd.date_range("2013-09-01", periods=16, freq="MS").take(row % 16),
            "Month Number": 1,
            "Month Name": "January",
            "Year": 2014,
        }
    )
    workbook = BytesIO()
    fixture.to_excel(workbook, sheet_name="Sheet1", index=False, engine="openpyxl")
    return fixture, workbook.getvalue()


def test_excel_notebook_download_charts_exports_and_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    financial_sample: tuple[pd.DataFrame, bytes],
) -> None:
    """Validate Excel parsing, aggregations, unused chart types, and PDF reuse."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Figure, "show", lambda fig: None)
    fixture, workbook_bytes = financial_sample
    downloads: list[str] = []

    def download(url: str, *, timeout: float) -> BytesIO:
        assert timeout == 30
        downloads.append(url)
        return BytesIO(workbook_bytes)

    monkeypatch.setattr("urllib.request.urlopen", download)
    notebook = json.loads((ROOT / "notebooks" / "excel_sales_report.ipynb").read_text())
    assert (
        sum(
            "image/png" in output.get("data", {})
            for cell in notebook["cells"]
            if cell["cell_type"] == "code"
            for output in cell["outputs"]
        )
        == 3
    )
    sources = [
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    ]
    namespace: dict[str, Any] = {}
    for source in sources:
        assert "plt.close" not in source
        exec(compile(source, "excel_sales_report.ipynb", "exec"), namespace)
    assert downloads == ["https://go.microsoft.com/fwlink/?LinkID=521962"]
    sales = namespace["sales"].df
    assert sales.shape == (700, 6)
    assert list(sales.columns) == [
        "Country",
        "Product",
        "Units Sold",
        "Sales",
        "Profit",
        "Date",
    ]
    assert pd.api.types.is_datetime64_any_dtype(sales["Date"])
    expected = fixture.groupby("Date")[" Sales "].sum().sort_index()
    assert namespace["monthly"]["Date"].is_monotonic_increasing
    np.testing.assert_allclose(
        namespace["monthly"]["Sales"].to_numpy(), expected.to_numpy()
    )
    trend = namespace["trend"]
    assert len(trend.ax.lines) == 1
    assert trend.ax.lines[0].get_marker() == "o"
    np.testing.assert_allclose(
        np.asarray(trend.ax.lines[0].get_ydata(), dtype=float),
        expected.to_numpy() / 1_000_000,
    )
    product_share = namespace["product_share"]
    assert len(product_share.ax.patches) == 6
    assert sum(
        wedge.theta2 - wedge.theta1 for wedge in product_share.ax.patches
    ) == pytest.approx(360, abs=0.001)
    labels = [text.get_text() for text in product_share.ax.texts]
    assert set(fixture["Product"]) <= set(labels)
    assert len([label for label in labels if label.endswith("%")]) == 6

    output_dir = tmp_path / "outputs"
    summary = pd.read_excel(output_dir / "monthly_summary.xlsx")
    pd.testing.assert_frame_equal(summary, namespace["monthly_table"].df)
    reader = PdfReader(output_dir / "excel_sales_report.pdf")
    assert len(reader.pages) == 2
    text = [page.extract_text() for page in reader.pages]
    assert text[0].index("Excel Sales Report") < text[0].index("Monthly sales")
    assert text[0].index("Monthly sales") < text[0].index("Sales share by product")
    assert "Monthly summary" in text[1]
    assert all(month in text[1] for month in summary["Month"])
    assert all(not page.images for page in reader.pages)
    assert len({tuple(page.mediabox) for page in reader.pages}) == 1
    for name in ("monthly_sales", "product_share"):
        assert (output_dir / f"{name}.png").read_bytes().startswith(b"\x89PNG")

    # A second run reads the cached workbook without another network request.
    download_cell = next(source for source in sources if "DATA_URL =" in source)
    exec(compile(download_cell, "excel_sales_report.ipynb", "exec"), namespace)
    assert len(downloads) == 1
    assert namespace["sales"].df.equals(sales)
