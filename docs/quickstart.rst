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

For the precise distinction between grid CV, analytical derivatives and
smoothness inversion, consult :doc:`smoothness_optimization`.
For a concise, section-by-section formula reference (PLS, CV, GCV,
AICc, BIC, derivatives, Guerrero smoothness, and root solvers), see
:doc:`handbook/index`.

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
they require a **fixed numeric reference mean**. Gaussian marginal MLE
is also available with criterion="mle" (numeric or plug-in mu).

Searching over normalized smoothness
-------------------------------------

The same criterion can also be searched directly over normalized S
on the unit interval. The previous lambda search stays the default.

.. code-block:: python

   choice_s = select_lambda(
       smoother, y, criterion="gcv", mu=0.0,
       search_space="smoothness",
   )
   print(choice_s.lambda_, choice_s.smoothness)

   grid_s = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
   custom = select_lambda(
       smoother, y, criterion="gcv", mu=0.0,
       search_space="smoothness", grid=grid_s,
   )
   print(custom.search_grid)  # S coordinates
   print(custom.grid)         # Corresponding lambda values

For derivative-guided classical CV, setting
**search_space="smoothness"** also searches for stationary points
within S using the existing analytical CV derivative and the chain
rule. This is not joint estimation of mu and lambda and it is not
rolling-origin forecast validation. See :doc:`smoothness_optimization`.

Guerrero's original smoothness and Gaussian MLE
-------------------------------------------------

Guerrero's original index uses denominator :math:`n` rather than
:math:`n-d` and has upper limit :math:`1-d/n`.

.. code-block:: python

   original = smoother.smoothness(choice.lambda_, normalized=False)
   restored = smoother.lambda_for_smoothness(original, normalized=False)
   mle = select_lambda(smoother, y, criterion="mle", mu="data")
   fit_ml = smoother.fit(y, lambda_=mle.lambda_, mu="data")
   print("MLE lambda:", mle.lambda_)
   print("Observed difference mean:", fit_ml.mu)
   print("Original smoothness:", fit_ml.guerrero_smoothness)

   from trendestimation import estimate_variance_components
   variances = estimate_variance_components(
       smoother, y, lambda_=mle.lambda_, mu="data",
   )
   print("Observation noise variance:", variances.observation_variance)
   print("Latent difference variance:", variances.difference_variance)
   print("Noise SD:", variances.observation_sd)
   print("Difference SD:", variances.difference_sd)

The data-derived reference mu is mean(D_d @ y), i.e., the average of
the observed order-d differences. MLE uses a Gaussian marginal likelihood
with observation variance profiled out and the polynomial nullspace
unpenalized. A data-derived mu is only a conditional plug-in; this is not
joint optimization over mu and lambda. The classical four criteria
continue to require a fixed numeric mu.

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

Reproducibility gallery
-----------------------

The nine longer :doc:`gallery` notebooks provide published-style simulation
scenarios, spectral diagnostics and computational benchmarks. To execute
and record their results manually, use::

   python scripts/run_notebooks.py --fast --fail-fast

To prepare cached figures before publishing a site, explicitly add
``--in-place``. Only the manual Pages workflow deploys a public site.

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
