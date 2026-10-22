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

Selection criteria
------------------

.. autofunction:: trendestimation.select_lambda

.. autofunction:: trendestimation.score_lambda

.. autoclass:: trendestimation.SelectionResult
   :members:

Gaussian variance components
----------------------------

.. autofunction:: trendestimation.estimate_variance_components

.. autoclass:: trendestimation.VarianceComponents
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

Conditional trend extrapolation
-------------------------------

.. autofunction:: trendestimation.forecast_trend

.. autoclass:: trendestimation.TrendForecast
   :members:

Additional optional plots
-------------------------

.. autofunction:: trendestimation.plot_forecast

.. autofunction:: trendestimation.plot_forecast_dashboard

.. autofunction:: trendestimation.plot_forecast_methods

.. autofunction:: trendestimation.plot_smoothness_comparison

.. autofunction:: trendestimation.plot_smoothness_path

.. autofunction:: trendestimation.plot_residual_diagnostics
