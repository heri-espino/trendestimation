"""Fast structural tests of the reproducible SVG notebook workflow."""

import ast
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]


def test_all_notebooks_select_pinned_awesomefigures_and_svg():
    paths = sorted((ROOT / "docs").glob("**/*.ipynb"))
    assert len(paths) == 14
    for path in paths:
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        codes = [cell.source for cell in nb.cells if cell.cell_type == "code"]
        first = codes[0]
        for signature in (
            "import awesomefigures as af",
            "from matplotlib_inline.backend_inline import set_matplotlib_formats",
            'af.set_style("elegante"',
            'palette="okabe-ito"',
            "rasterize=False",
            'set_matplotlib_formats("svg", "png")',
        ):
            assert signature in first, (path, signature)
        for code in codes:
            ast.parse(code, filename=str(path))
        # GitHub's notebook viewer can display PNG while Sphinx uses SVG.
        # Executed figures retain both MIME variants, not raster-only images.
        for cell in nb.cells:
            for output in cell.get("outputs", []):
                data = output.get("data", {})
                if "image/png" in data:
                    assert "image/svg+xml" in data, path
        assert any(cell.get("id") == "te-dual-coordinate" for cell in nb.cells)



def test_forecast_optional_export_is_svg():
    path = ROOT / "docs/notebooks/10-forecast-pipeline.ipynb"
    nb = nbformat.read(path, as_version=4)
    source = "\n".join(cell.source for cell in nb.cells if cell.cell_type == "code")
    assert "SAVE_SVG = False" in source
    assert ".svg" in source
    assert ".png" not in source
    assert "SAVE_PNG" not in source
    assert 'af.color_palette("okabe-ito", as_hex=True)' in source


def test_external_package_is_pinned_and_pages_is_manual():
    requirement = (ROOT / "docs/requirements-figures.txt").read_text()
    assert "awesomefigures @ git+https://github.com/awesomefigures/awesomefigures.git@" in requirement
    assert "54c8bf2374551fa39428f47f69580b4822d4b938" in requirement
    workflow = (ROOT / ".github/workflows/docs.yml").read_text()
    assert "workflow_dispatch:" in workflow
    assert "push:" not in workflow
    assert "docs/requirements-figures.txt" in workflow
