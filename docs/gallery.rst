Executable notebook gallery
===========================

Twelve **real Jupyter notebooks** drive both the standalone tutorial experience
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
   notebooks/11-paper-solver-timing-comparison
   notebooks/12-six-solvers-cholesky-nonzero-mu

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
   python scripts/run_notebooks.py --fast --all --in-place --fail-fast
   python scripts/run_notebooks.py --fast --only 09-gaussian-mle-and-guerrero-smoothness --fail-fast
   python scripts/run_notebooks.py --fast --only 03-classical-criteria 04-nonzero-mean --fail-fast
   python scripts/run_notebooks.py --fast --only 10-forecast-pipeline --fail-fast

The batch runner writes executed copies, ``timings.csv`` and
``manifest.json`` under ``build/notebook-runs/`` by default. The
manifest records Python, libraries, CPU and thread environment, timings,
failure status, and optional electricity-cost assumptions.

To render executed figures in the Sphinx website::

   python scripts/run_notebooks.py --fast --all --in-place --fail-fast
   TRENDESTIMATION_DOCS_EXECUTION=off python -m sphinx -b html docs build/site

Alternatively, set the Sphinx execution mode to auto and build directly.
Notebook source lives exclusively under ``docs/notebooks/``.

SVG figure display
------------------

All 15 notebooks set the ``awesomefigures`` ``elegante`` style with the
Okabe–Ito palette, then ``set_matplotlib_formats("svg", "png")`` for crisp
inline SVG figures with GitHub-compatible PNG fallbacks. The dependency is pinned to GitHub in
``docs/requirements-figures.txt``; a PyPI release is not required.

The **manual** executed-notebook workflow embeds SVG outputs in Sphinx HTML.
The normal PR build disables expensive notebook execution but runs one short
SVG smoke notebook. In chapter 10, set ``SAVE_SVG=True`` to also export
individual SVG files rather than PNG.

Paired penalty and normalized smoothness
----------------------------------------

Every introductory and research notebook now contains an executable visual
comparison of the same fixed-mu PLS criteria against ``lambda`` and
``S(lambda)``. It displays the monotone map and its inverse,
CV/GCV/AICc/BIC in both coordinates, their selected mapped-grid points,
using a native 11-decile S grid enriched at 0.95, 0.99, 0.999, 0.9999,
and 0.999999, with exact endpoint penalties 0 and infinity. The grid is
inverted once and the resulting lambda candidates reused for CV/GCV/AICc/BIC;
an illustrative four-criterion timing comparison separates this reuse from
repeated S inversion. The published factorial
study instead times three linear-algebra solvers across three search
policies with independent seeds and host metadata. Single notebook timings
are not publication-grade speed conclusions.

Use ``python scripts/run_notebooks.py --fast --all --in-place --fail-fast``
from the repository root to execute and save **all 15** notebooks. The
``Commit rendered notebook outputs`` workflow also runs the full gallery
on GitHub Actions and commits the executed SVG/PNG cells to the branch.

The new :doc:`notebooks/11-paper-solver-timing-comparison` notebook plots
recorded paper timing CSV results (not invented measurements), comparing
four numerical methods for complete trend fits and separate EDF/trace sweeps.
The associated environment.json and numerical-parity errors are inspected.
The paper's general banded solver is not a Cholesky implementation.

The new :doc:`notebooks/12-six-solvers-cholesky-nonzero-mu` extends the
four original solvers with dense Cholesky and true banded Cholesky,
measuring paired full-fit workloads for both fixed ``mu=0`` and ``mu=0.15``.
A separate six-way trace comparison is shown only once because the
smoothing matrix and EDF are independent of fixed numeric ``mu``.
Machine-specific reference timings are checked into
``paper/benchmarks/cholesky_reference/`` with their provenance;
the original four-method paper benchmark tables remain unchanged.
