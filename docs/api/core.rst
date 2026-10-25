Trend smoothing
===============

Construct a reusable spectral solver, fit a penalized least-squares trend,
and inspect the resulting effective degrees of freedom. This reference
is generated directly from the library's source docstrings.

.. autoclass:: trendestimation.TrendSmoother
   :members: fit, smoothness, lambda_for_smoothness, degrees_of_freedom

.. autoclass:: trendestimation.PreparedPLSSolver
   :members: fit, fit_many, stored_bytes

.. autofunction:: trendestimation.fit_penalized

.. autofunction:: trendestimation.fit_trend

.. autofunction:: trendestimation.difference_matrix

.. autoclass:: trendestimation.FitResult
   :members:
