Executable notebook gallery
===========================

Ten **real Jupyter notebooks** drive both the standalone tutorial experience
and this Sphinx website. Every notebook includes mathematical exposition,
deterministic source code, plots, and interpretation. The default inputs are simulated. The final chapter can also read an equally
spaced local CSV and illustrates chronological holdout evaluation of a
conditional trend-extrapolation baseline. A single holdout cannot establish
reliable future forecasting performance.

Notebook chapters
-----------------

.. toctree::
   :maxdepth: 1
   :numbered:

   notebooks/01-first-trend
   notebooks/02-differencing-orders
   notebooks/03-classical-criteria
   notebooks/04-nonzero-mean
   notebooks/05-cortes-toto-atlas
   notebooks/06-spectral-diagnostics
   notebooks/07-computational-benchmarks
   notebooks/08-applied-workflows
   notebooks/09-gaussian-mle-and-guerrero-smoothness
   notebooks/10-forecast-pipeline

Gaussian variance-component examples
------------------------------------

Gaussian marginal MLE and ``estimate_variance_components`` are illustrated
in chapters 3, 4, 6, 8 and especially 9, alongside the classical criteria
and Guerrero's difference-reference mean. Chapter 10 estimates these
variances from historical data only, separately from held-out forecast
metrics. Latent-difference variance is not variance of the fitted trend,
residual mean squared error, or forecast-error uncertainty.

Run the entire gallery or selected examples
-------------------------------------------

From the repository root::

   python -m pip install -e ".[docs,plot]"
   python -m pip install -r docs/requirements-figures.txt
   python scripts/run_notebooks.py --list
   python scripts/run_notebooks.py --fast --fail-fast
   python scripts/run_notebooks.py --fast --only 09-gaussian-mle-and-guerrero-smoothness --fail-fast
   python scripts/run_notebooks.py --fast --only 03-classical-criteria 04-nonzero-mean --fail-fast
   python scripts/run_notebooks.py --fast --only 10-forecast-pipeline --fail-fast

The batch runner writes executed copies, ``timings.csv`` and
``manifest.json`` under ``build/notebook-runs/`` by default. The
manifest records Python, libraries, CPU and thread environment, timings,
failure status, and optional electricity-cost assumptions.

To render executed figures in the Sphinx website::

   python scripts/run_notebooks.py --fast --in-place --fail-fast
   TRENDESTIMATION_DOCS_EXECUTION=off python -m sphinx -b html docs build/site

Alternatively, set the Sphinx execution mode to auto and build directly.
Notebook source lives exclusively under ``docs/notebooks/``.

SVG figure display
------------------

All 13 notebooks set the ``awesomefigures`` ``elegante`` style with the
Okabe–Ito palette, then ``set_matplotlib_formats("svg")`` for crisp
inline figures. The dependency is pinned to GitHub in
``docs/requirements-figures.txt``; a PyPI release is not required.

The **manual** executed-notebook workflow embeds SVG outputs in Sphinx HTML.
The normal PR build disables expensive notebook execution but runs one short
SVG smoke notebook. In chapter 10, set ``SAVE_SVG=True`` to also export
individual SVG files rather than PNG.
