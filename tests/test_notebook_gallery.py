"""Lightweight reproducibility and notebook-gallery structure checks."""
import ast
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]


def test_explanatory_executable_notebooks():
    examples = sorted((ROOT / "docs" / "notebooks").glob("*.ipynb"))
    assert len(examples) >= 10
    for file in examples:
        notebook = nbformat.read(file, as_version=4)
        nbformat.validate(notebook)
        assert notebook.cells[0].cell_type == "markdown"
        assert sum(c.cell_type == "markdown" for c in notebook.cells) >= 4
        assert sum(c.cell_type == "code" for c in notebook.cells) >= 3
        sources = "\n".join(c.source for c in notebook.cells if c.cell_type == "code")
        assert "plt." in sources, file.name


def test_notebooks_documented_in_gallery():
    gallery = (ROOT / "docs" / "gallery.rst").read_text(encoding="utf-8")
    for file in (ROOT / "docs" / "notebooks").glob("*.ipynb"):
        assert "notebooks/" + file.stem in gallery


def test_manual_only_heavy_workflow():
    workflow = (ROOT / ".github" / "workflows" / "docs.yml").read_text()
    assert "workflow_dispatch:" in workflow
    assert "push:" not in workflow


def test_forecast_notebook_documents_full_pipeline():
    """Check notebook content; complete figure generation remains manual."""
    path = ROOT / "docs" / "notebooks" / "10-forecast-pipeline.ipynb"
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    narrative = "\n".join(c.source for c in notebook.cells if c.cell_type == "markdown")
    code = "\n".join(c.source for c in notebook.cells if c.cell_type == "code")
    for func in (
        "forecast_trend", "plot_forecast", "plot_smoothness_comparison",
        "plot_smoothness_path", "plot_forecast_methods",
        "plot_residual_diagnostics", "plot_forecast_dashboard",
    ):
        assert func in code, func
    assert "SMOOTHNESS = 0.80" in code
    assert "history = all_observed[:-holdout_length]" in code
    assert "test = all_observed[-holdout_length:]" in code
    assert "forecast_trend(\n    history" in code
    assert "last_observation_baseline" in code
    assert "MAE" in code and "RMSE" in code
    assert "SAVE_PNG" in code
    assert "prediction interval" in narrative.lower()


def test_gaussian_variance_component_notebooks():
    """Check that both variance estimates are covered by executable examples."""
    notebook_paths = (
        "docs/notebooks/03-classical-criteria.ipynb",
        "docs/notebooks/04-nonzero-mean.ipynb",
        "docs/notebooks/06-spectral-diagnostics.ipynb",
        "docs/notebooks/08-applied-workflows.ipynb",
        "docs/notebooks/09-gaussian-mle-and-guerrero-smoothness.ipynb",
        "docs/notebooks/10-forecast-pipeline.ipynb",
        "docs/examples/02_select_smoothness.ipynb",
    )
    for relative in notebook_paths:
        notebook = nbformat.read(ROOT / relative, as_version=4)
        nbformat.validate(notebook)
        code_cells = [c.source for c in notebook.cells if c.cell_type == "code"]
        code = "\n".join(code_cells)
        assert "estimate_variance_components(" in code, relative
        assert 'criterion="mle"' in code, relative
        assert "observation_variance" in code, relative
        assert "difference_variance" in code, relative
        for cell in code_cells:
            ast.parse(cell, filename=relative)


def test_forecast_variance_diagnostic_never_uses_holdout_test():
    """Variance-component comparison must use historical values, not test."""
    path = ROOT / "docs/notebooks/10-forecast-pipeline.ipynb"
    notebook = nbformat.read(path, as_version=4)
    variance_cell = next(c for c in notebook.cells if c.get("id") == "fp090-variance-code")
    identifiers = {node.id for node in ast.walk(ast.parse(variance_cell.source))
                   if isinstance(node, ast.Name)}
    assert "history" in identifiers
    assert "test" not in identifiers
    assert "estimate_variance_components" in identifiers
