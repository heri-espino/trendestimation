Smoothing-parameter selection
=============================

Choose a smoothing penalty using CV, GCV, AICc, BIC, or Gaussian marginal
maximum likelihood. The listed criteria are not rolling-origin forecast
validation. The mathematical derivations, scoring conventions,
limits of ordinary LOOCV, and numerical optimization trade-offs are covered
in :doc:`../smoothness_optimization`.

.. autofunction:: trendestimation.select_lambda

.. autofunction:: trendestimation.score_lambda

.. autoclass:: trendestimation.SelectionResult
   :members:
