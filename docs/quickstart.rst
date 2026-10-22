Quickstart and source illustrations
===================================

Install from source
-------------------

The pre-release candidate is not published on PyPI.
From the standalone repository root::

   python -m pip install -e '.[plot,docs]'

Published Cortés-Toto et al. (2017) simulation
----------------------------------------------

The following uses **simulated** series from the publication rather than
newly collected empirical observations. The published settings include
n=50 and n=200, linear/nonlinear trends, Gaussian noise standard
deviations 0.5 or 2.0, and optional quarterly seasonality.

.. code-block:: python

   from trendestimation import (
       TrendSmoother, plot_selection, plot_trend,
       select_lambda, simulate_cortes_toto,
   )

   case = simulate_cortes_toto(n=200, shape="nonlinear", seasonal=True, seed=7)
   y = case.observed
   solver = TrendSmoother(len(y), order=2)
   chosen = select_lambda(solver, y, criterion="gcv", mu=0.0)
   fit = solver.fit(y, lambda_=chosen.lambda_, mu=0.0)
   print("Smoothness:", chosen.smoothness)
   print("Conditional EDF:", fit.edf_conditional)
   plot_trend(y, fit)
   plot_selection(chosen)

Try difference orders 1, 2 and 3, and fixed nonzero mu.

Guerrero (2007) nonzero mean
----------------------------

.. code-block:: python

   solver = TrendSmoother(len(y), order=1)
   fit = solver.fit(y, lambda_=10.0, mu="data")
   print("Observed-difference plug-in mean:", fit.mu)

The observed-difference plug-in mean uses the supplied data; the standard
classical selection formulas are not claimed to be exact leave-one-out
scores for a refitted plug-in mean. Their API requires fixed numeric mu.
