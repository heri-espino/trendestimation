"""Lightweight reproducibility and notebook-gallery structure checks."""
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]


def test_nine_explanatory_executable_notebooks():
    examples = sorted((ROOT / "docs" / "notebooks").glob("*.ipynb"))
    assert len(examples) == 9
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


def test_forecast_notebook_documents_complete_pipeline():
    """Structural checks only: heavy figures execute in manual notebook workflow."""
    path = ROOT / "docs" / "notebooks" / "09-forecast-pipeline.ipynb"
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    narrative = "\n".join(c.source for c in notebook.cells if c.cell_type == "markdown")
    code = "\n".join(c.source for c in notebook.cells if c.cell_type == "code")
    for api in (
        "forecast_trend", "plot_forecast", "plot_smoothness_comparison",
        "plot_smoothness_path", "plot_forecast_methods",
        "plot_residual_diagnostics", "plot_forecast_dashboard",
    ):
        assert api in code, api
    assert "SMOOTHNESS = 0.80" in code
    assert "history = all_observed[:-holdout_length]" in code
    assert "test = all_observed[-holdout_length:]" in code
    assert "forecast_trend(\n    history" in code
    assert "last_observation_baseline" in code
    assert "MAE" in code and "RMSE" in code
    assert "SAVE_PNG" in code
    assert "prediction interval" in narrative.lower()
