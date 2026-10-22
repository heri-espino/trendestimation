API reference
=============

This reference is **generated from the Python source docstrings** using
Sphinx autodoc and Napoleon. It is not a hand-maintained copy of function
signatures. For reproducible worked examples, see :doc:`notebooks`.

Trend estimation
----------------

.. autoclass:: trendestimation.TrendSmoother
   :members: fit, smoothness, lambda_for_smoothness, degrees_of_freedom

.. autofunction:: trendestimation.fit_trend

.. autofunction:: trendestimation.difference_matrix

.. autoclass:: trendestimation.FitResult
   :members:

Classical selection criteria
----------------------------

.. autofunction:: trendestimation.select_lambda

.. autofunction:: trendestimation.score_lambda

.. autoclass:: trendestimation.SelectionResult
   :members:

Reproducible synthetic data
---------------------------

.. autofunction:: trendestimation.simulate_cortes_toto

.. autoclass:: trendestimation.SimulatedSeries
   :members:

Optional visualization
----------------------

.. autofunction:: trendestimation.plot_trend

.. autofunction:: trendestimation.plot_selection
