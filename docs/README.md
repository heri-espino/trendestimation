# Building the documentation

This is the source for the Sphinx site, using Furo, sphinx-design,
sphinx-copybutton, and MyST-NB. Jupyter notebooks are the canonical
worked examples; the site embeds the **same files**.

At the repository root:

```bash
python -m pip install -e '.[docs,plot]'
python -m pytest tests/test_notebook_gallery.py -q
python scripts/run_notebooks.py --list
python scripts/run_notebooks.py --fast --in-place --fail-fast
TRENDESTIMATION_DOCS_EXECUTION=off python -m sphinx -b html -W docs build/site
```

Open `build/site/index.html`. The command `--in-place` is intentionally
explicit: without it, executed notebooks and timing logs stay under `build/`
and are not part of tracked sources.

The GitHub Pages workflow runs only through `workflow_dispatch`, not
on each push, because notebook execution/plots can be costly. Review
the PR, configure Pages in GitHub Settings, then dispatch the workflow.

For user-machine cost reporting, use the `--watts` and
`--mxn-per-kwh` options only when measured or documented assumptions
are available.

## Design and API maintenance

The blue-and-white landing page uses a Furo design system in
`docs/_static/css/custom.css`; existing shared styles remain in
`docs/_static/custom.css`. The home page supports accessible keyboard
focus, reduced motion, and responsive layouts.

Public API reference pages are generated from NumPy-style source docstrings
through Sphinx autodoc and Napoleon. Edit docstrings in
`src/trendestimation/` when signatures or behavior change; update
`docs/api.rst` when adding a public API object. Source docstring examples
are shown as text/code by Sphinx and are not automatically doctested.

There are two complementary tutorial collections:
- `docs/examples/`: three small introductory notebooks.
- `docs/notebooks/`: eight detailed research and benchmark notebooks.

To preview the complete site with a warning-strict build, set
`TRENDESTIMATION_DOCS_EXECUTION=off` and build Sphinx. The
`docs-preview.yml` workflow uploads HTML for inspection but does not deploy
it. The separate manual Pages workflow executes the longer notebooks
when explicitly requested.


## Gaussian MLE variance-component examples

The public ``estimate_variance_components`` API reports likelihood-based
observation-noise and latent-difference variances (and their standard
deviations). These are not the fitted-trend variance, residual MSE, or
forecast prediction intervals. The short selection notebook introduces
the method; longer criteria, nonzero-mean, spectral, applied, MLE and
forecast-pipeline notebooks demonstrate the same API in context.

Notebook execution and publication remain separate: run selected notebooks
manually with ``python scripts/run_notebooks.py --fast --only
09-gaussian-mle-and-guerrero-smoothness --fail-fast`` before an explicit
Sphinx build. The forecasting chapter profiles historical data only.
