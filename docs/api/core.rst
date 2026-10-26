Trend smoothing
===============

Construct a reusable spectral solver for EDF and smoothing-criterion
selection, or use the banded Cholesky default for a fit-only trend,
and inspect the resulting effective degrees of freedom when spectral
metadata are requested. See :doc:`../grid_reuse_selection` for matched
workload timings and the rationale for these two defaults. This reference
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
