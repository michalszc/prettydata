"""Generated API pages expose public modules, classes, signatures, and source."""

from pathlib import Path

import pytest
from mkdocs.commands.build import build
from mkdocs.config import load_config

ROOT = Path(__file__).parents[1]


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
