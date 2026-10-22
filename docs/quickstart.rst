Getting started
===============

Install from source
-------------------

``trendestimation`` is currently a pre-release candidate, not an announced
PyPI release. Clone the `GitHub repository
<https://github.com/heri-espino/trendestimation>`_ and run these commands
**from the repository root**:

.. code-block:: console

   python -m pip install -e ".[plot,docs]"
   python -m pytest tests -q

For a documentation-only environment, ``python -m pip install -e ".[docs]"``
is sufficient. Build the website locally with:

.. code-block:: console

   python -m sphinx -n -W --keep-going -b html docs docs/_build/html

Open ``docs/_build/html/index.html`` in a browser.

Your first trend
----------------

Use the order-2 finite-difference penalty and choose its smoothing parameter
using generalized cross-validation (GCV). This is **in-sample** smoothing
parameter selection, not an evaluation of future forecast accuracy.

.. code-block:: python

   import numpy as np
   from trendestimation import TrendSmoother, select_lambda

   rng = np.random.default_rng(42)
   y = np.linspace(0, 3, 100) + rng.normal(0, 0.3, 100)

   smoother = TrendSmoother(len(y), order=2)
   choice = select_lambda(smoother, y, criterion="gcv", mu=0.0)
   fit = smoother.fit(y, lambda_=choice.lambda_, mu=0.0)

   print("Selected lambda:", choice.lambda_)
   print("Normalized smoothness:", fit.smoothness)
   print("Conditional EDF:", fit.edf_conditional)
   trend = fit.trend

The solver can be reused for the same series length and differencing order.
Available classical criteria are ``cv``, ``gcv``, ``aicc``, and ``bic``;
they require a **fixed numeric reference mean**.

Reproduce published simulation settings
---------------------------------------

The library includes a synthetic data generator following the linear and
nonlinear configurations examined by Cortés-Toto et al. (2017). These are
simulations, not newly collected empirical observations.

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

   plot_trend(y, fit)
   plot_selection(chosen)

Try ``n=50`` or ``n=200``, linear/nonlinear shapes, noise standard deviations
of ``0.5`` or ``2.0``, and seasonal/nonseasonal variants. Plots require the
``plot`` optional dependency group.

Guerrero's observed-difference mean
-----------------------------------

.. code-block:: python

   solver = TrendSmoother(len(y), order=1)
   fit = solver.fit(y, lambda_=10.0, mu="data")
   print("Observed-difference reference mean:", fit.mu)

For ``mu="data"``, the mean is estimated from the supplied observations.
The conditional effective degrees of freedom do not automatically account
for estimating that mean. Classical parameter-selection formulas in this
package **cannot** be called with ``mu="data"`` as if they represented exact
leave-one-out refits of a data-dependent mean.

Notebook tutorials
------------------

The :doc:`notebooks` page provides runnable Jupyter examples for a first
trend, selection criteria, and comparisons between differencing orders.
These notebooks are the canonical worked examples, while the API reference
is generated from Python docstrings.

Next steps
----------

Read :doc:`notebooks` for examples, :doc:`mathematics` for the estimator and its assumptions, then
:doc:`api` for the callable Python interface.
