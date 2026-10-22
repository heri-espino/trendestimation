Smoothing-parameter selection
=============================

Choose a smoothing penalty using CV, GCV, AICc, BIC, or Gaussian marginal
maximum likelihood. The listed criteria are not rolling-origin forecast
validation.

.. autofunction:: trendestimation.select_lambda

.. autofunction:: trendestimation.score_lambda

.. autoclass:: trendestimation.SelectionResult
   :members:
