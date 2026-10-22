Executable notebook gallery
===========================

Nine **real Jupyter notebooks** drive both the standalone tutorial experience
and this Sphinx website. Every notebook includes mathematical exposition,
deterministic source code, plots, and interpretation. The default data are simulated. Chapter 09 optionally loads an equally spaced
local CSV and demonstrates a genuine chronological holdout alongside a
fixed-smoothness trend-extrapolation baseline. Neither a single holdout nor
in-sample fitting proves reliable future forecasting performance.

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
   notebooks/09-forecast-pipeline
   notebooks/09-gaussian-mle-and-guerrero-smoothness

Run the entire gallery or just the forecast pipeline
-------------------------------------

From the repository root::

   python -m pip install -e ".[docs,plot]"
   python scripts/run_notebooks.py --list
   python scripts/run_notebooks.py --fast --fail-fast
   python scripts/run_notebooks.py --fast --only 09-forecast-pipeline --fail-fast

The batch runner writes executed copies, ``timings.csv`` and
``manifest.json`` under ``build/notebook-runs/`` by default. The
manifest records Python, libraries, CPU and thread environment, timings,
failure status, and optional electricity-cost assumptions.

To render executed figures in the Sphinx website::

   python scripts/run_notebooks.py --fast --in-place --fail-fast
   TRENDESTIMATION_DOCS_EXECUTION=off python -m sphinx -b html docs build/site

Alternatively, set the Sphinx execution mode to auto and build directly.
Notebook source lives exclusively under ``docs/notebooks/``.
