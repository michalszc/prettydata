"""Generated API pages expose public modules, classes, signatures, and source."""

from pathlib import Path

import pytest
from mkdocs.commands.build import build
from mkdocs.config import load_config

from tests.contracts.public_api.manifest import PUBLIC_SIGNATURES, REFERENCE_CLASSES

ROOT = Path(__file__).parents[3]


@pytest.fixture(scope="module")
def reference_site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build actual reference HTML in temporary storage for semantic checks."""
    site = tmp_path_factory.mktemp("reference-site")
    config = load_config(config_file=str(ROOT / "mkdocs.yml"), site_dir=str(site))
    build(config)
    return site


@pytest.mark.parametrize(
    ("area", "module", "name"),
    [
        ("tables", "table", "Table"),
        ("charts", "chart", "Chart"),
        ("reports", "report", "Report"),
    ],
)
def test_generated_reference(
    reference_site: Path, area: str, module: str, name: str
) -> None:
    html = (reference_site / "reference" / area / "index.html").read_text()
    assert f'id="tabloom.{module}"' in html
    assert f'id="tabloom.{module}.{name}"' in html
    assert "doc-symbol-module" in html
    assert "doc-symbol-class" in html
    assert f"View source for tabloom.{module}.{name} on GitHub" in html
    assert f"/src/tabloom/{module}/{module}.py#L" in html
    assert 'class="doc-signature' in html
    assert "Parameters:" in html
    assert f'id="tabloom.{module}.__all__"' not in html
    assert "organization/" not in html
    assert not (reference_site / "reference" / "organization").exists()


def test_page_break_has_one_documented_return(reference_site: Path) -> None:
    """Render one return entry, keeping page-break behavior in the main prose."""
    html = (reference_site / "reference" / "reports" / "index.html").read_text()
    method = html.split('id="tabloom.report.Report.add_page_break"', 1)[1]
    method = method.split('id="tabloom.report.Report.save"', 1)[0]
    assert method.count('class="doc-section-item"') == 1
    assert (
        "Leading, trailing, and consecutive breaks do not create empty pages." in method
    )
    assert "This report, allowing method chaining." in method


def test_report_styling_parameters_are_documented(reference_site: Path) -> None:
    """Expose new typography and width controls in the generated method reference."""
    html = (reference_site / "reference" / "reports" / "index.html").read_text()
    text_method = html.split('id="tabloom.report.Report.add_text"', 1)[1]
    text_method = text_method.split('id="tabloom.report.Report.add_table"', 1)[0]
    for name in (
        "font_family",
        "font_size",
        "font_weight",
        "font_style",
        "color",
        "align",
        "line_spacing",
        "space_after",
    ):
        assert f"<code>{name}</code>" in text_method
    for name in ("add_table", "add_chart"):
        method = html.split(f'id="tabloom.report.Report.{name}"', 1)[1]
        method = method.split('<h4 id="', 1)[0]
        assert "<code>resize</code>" in method
        if name == "add_table":
            assert "<code>paginate</code>" in method


def test_scatter_controls_are_documented(reference_site: Path) -> None:
    """Describe the convenience controls beside the actual factory signature."""
    html = (reference_site / "reference" / "charts" / "index.html").read_text()
    method = html.split('id="tabloom.chart.Chart.scatter"', 1)[1]
    method = method.split('id="tabloom.chart.Chart.hist"', 1)[0]
    for name in ("hue", "colorbar", "colorbar_label", "trendline", "trendline_kwargs"):
        assert f"<code>{name}</code>" in method


@pytest.mark.parametrize("name", REFERENCE_CLASSES)
def test_protected_endpoints_have_reference_anchors(
    reference_site: Path, name: str
) -> None:
    """Every supported public method remains addressable in the generated API."""
    module, area = REFERENCE_CLASSES[name]
    html = (reference_site / "reference" / area / "index.html").read_text()
    prefix = f"tabloom.{module}.{name}"
    assert f'id="{prefix}"' in html
    for endpoint in PUBLIC_SIGNATURES:
        owner, _, member = endpoint.partition(".")
        if owner == name and member:
            assert f'id="{prefix}.{member}"' in html, endpoint
