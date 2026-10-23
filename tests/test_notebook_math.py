"""Regression tests for LaTeX rendering in MyST-NB notebook Markdown."""

from __future__ import annotations

from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _markdown(relative: str) -> str:
    notebook = nbformat.read(ROOT / relative, as_version=4)
    nbformat.validate(notebook)
    return "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "markdown"
    )


def test_myst_config_parses_inline_and_display_math():
    conf = (DOCS / "conf.py").read_text(encoding="utf-8")
    assert '"sphinx.ext.mathjax"' in conf
    assert '"myst_nb"' in conf
    assert 'myst_enable_extensions = ["dollarmath", "amsmath"]' in conf
    workflow = (ROOT / ".github/workflows/docs-preview.yml").read_text(
        encoding="utf-8"
    )
    assert "scripts/check_rendered_notebook_math.py build/site" in workflow


def test_notebooks_keep_native_latex_not_unicode_substitutes():
    inline = _markdown("docs/examples/03_difference_orders.ipynb")
    assert "$d=1$" in inline
    assert r"$\mu=0$" in inline
    assert r"$\lambda=\infty$" in inline

    ml = _markdown("docs/examples/02_select_smoothness.ipynb")
    assert r"$\sigma_\varepsilon^2$" in ml
    assert r"$\lambda=\sigma_\varepsilon^2/\sigma_\eta^2$" in ml

    likelihood = _markdown(
        "docs/notebooks/09-gaussian-mle-and-guerrero-smoothness.ipynb"
    )
    assert r"$$" in likelihood
    assert r"\widehat{\sigma}_\varepsilon^2" in likelihood
    assert r"\operatorname{Var}(z_j)" in likelihood
    assert "sigma_epsilon²" not in likelihood
    assert "sigma_eta²" not in likelihood

    forecast = _markdown("docs/notebooks/10-forecast-pipeline.ipynb")
    assert r"\|y-\tau\|_2^2" in forecast


def test_markdown_math_delimiters_are_balanced():
    for path in sorted(DOCS.rglob("*.ipynb")):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        for cell in notebook.cells:
            if cell.cell_type == "markdown":
                # Double-dollar display fences contribute two signs apiece.
                assert cell.source.count("$") % 2 == 0, (
                    path, cell.source[:160]
                )
