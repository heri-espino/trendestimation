Quickstart
==========

Installation
------------

Clone the repository, then install from its root directory.

.. code-block:: console

   python -m pip install -e ".[docs,plot]"
   python -m pytest -q
   python scripts/run_notebooks.py --list

Your first smoothed trend
-------------------------

.. code-block:: python

   import numpy as np
   from trendestimation import TrendSmoother, select_lambda, plot_trend

   rng = np.random.default_rng(42)
   t = np.arange(80)
   y = .04*t + .2*np.sin(t/8) + rng.normal(0,.4,len(t))

   smoother = TrendSmoother(len(y), order=2)
   choice = select_lambda(smoother, y, criterion="gcv", mu=0.)
   fit = smoother.fit(y, lambda_=choice.lambda_, mu=0.)
   print("Penalty:", choice.lambda_)
   print("Normalized smoothness:", choice.smoothness)
   plot_trend(y, fit)

The full :doc:`gallery` shows multiple values of `d`,
different selection criteria, fixed/nonzero means, diagnostics,
simulations from Cortés-Toto et al. (2017), and timing comparisons.

Publish the visualizations
--------------------------

.. code-block:: console

   python scripts/run_notebooks.py --fast --in-place --fail-fast
   python -m sphinx -b html docs build/site

The finished HTML site is available at `build/site/index.html`.
Only a manually dispatched GitHub Actions workflow deploys the site.
