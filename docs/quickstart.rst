Quickstart
==========

Installation
------------

This alpha candidate is not yet published on PyPI. Clone the standalone
repository, then install from its root directory.

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

Guerrero's original smoothness and Gaussian marginal MLE
-------------------------------------------------------

.. code-block:: python

   # Denominator n (original), rather than n-d (normalized):
   original = smoother.smoothness(choice.lambda_, normalized=False)
   restored_lambda = smoother.lambda_for_smoothness(
       original, normalized=False,
   )
   print("Guerrero original smoothness:", original)

   # Gaussian marginal MLE with observed-difference plug-in mu:
   ml = select_lambda(smoother, y, criterion="mle", mu="data")
   result = smoother.fit(y, lambda_=ml.lambda_, mu="data")
   print("Empirical mean of d-th differences:", result.mu)
   print("MLE smoothness (original):", result.guerrero_smoothness)

Here mu="data" means mean(D_d @ y), the mean of the observed d-th
differences. It is not generally the mean of the raw series. The MLE
criterion profiles Gaussian observation variance and treats the polynomial
nullspace as unpenalized; with plug-in mu, it does not claim *joint* maximum
likelihood for the reference mean and penalty. The classical CV/GCV/AICc/BIC
formulas still require fixed numeric mu.

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
