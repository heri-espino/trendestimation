Quickstart and source illustrations
===================================

Install from source
-------------------

The PyPI release is not published. From the repository root::

   python -m pip install -e "packages/trendestimation[plot,docs]"

Published Cortés-Toto et al. (2017) simulation
----------------------------------------------

The following reproduces **simulated** linear/nonlinear scenarios from
Section 3 of the cited paper, not a newly collected empirical dataset.
Try n=50 or n=200, linear/nonlinear shapes, noise standard deviations
0.5 or 2.0, and seasonal/nonseasonal variants.

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

Try differencing orders 1, 2 and 3 and fixed nonzero mu.

Guerrero (2007) nonzero mean
----------------------------

.. code-block:: python

   solver = TrendSmoother(len(y), order=1)
   fit = solver.fit(y, lambda_=10.0, mu="data")
   print("Observed-difference plug-in mean:", fit.mu)

The observed-difference plug-in mean is computed using all supplied
observations. For this mode the classical selection formulas are NOT
claimed to be exact leave-one-out refits of the mean. Their package
entry points require fixed numeric mu.
