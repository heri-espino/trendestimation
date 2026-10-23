Smoothing-parameter selection
=============================

Choose a smoothing penalty using CV, GCV, AICc, BIC, or Gaussian marginal
maximum likelihood. The listed criteria are not rolling-origin forecast
validation. The mathematical derivations, scoring conventions,
limits of ordinary LOOCV, and numerical optimization trade-offs are covered
in :doc:`../smoothness_optimization`. For a concise formula reference,
see :doc:`../handbook/index`.

To change the optimization coordinate, supply
**search_space="lambda"** (default) or **search_space="smoothness"**.
When providing an explicit grid, its values are interpreted in that
coordinate; normalized smoothness targets must be between zero and one.
The SelectionResult grid attribute always reports penalty values,
while search_grid reports the searched coordinates. Both are aligned
with scores. See the linked optimization guide for the chain rule,
endpoints, numerical limitations and reproducible examples.

.. autofunction:: trendestimation.select_lambda

.. autofunction:: trendestimation.score_lambda

.. autoclass:: trendestimation.SelectionResult
   :members:
