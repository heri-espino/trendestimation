Forecast a smoothed trend
=========================

``trendestimation`` can extrapolate a fitted historical PLS trend into
future equally spaced time steps. **This is an illustrative baseline**, not a
forecasting model trained to minimize future prediction errors, and it has
no calibrated forecast intervals. The PLS trend is fitted using historical
observations only, before an explicit extrapolation rule is applied.

Fixed smoothness: 0.8
---------------------

.. code-block:: python

   import numpy as np
   import matplotlib.pyplot as plt

   from trendestimation import forecast_trend, plot_forecast

   t = np.arange(90)
   rng = np.random.default_rng(2026)
   y = 1.5 + 0.02 * t + 0.3 * np.sin(t / 12) + rng.normal(0, .25, len(t))

   result = forecast_trend(
       y,
       horizon=15,
       smoothness=.8,  # fixed normalized PLS smoothness; NOT accuracy
       order=2,
       method="local_linear",
       window=18,
   )

   print("Lambda:", result.lambda_)
   print("Achieved smoothness:", result.smoothness)
   print("Future integer indices:", result.future_index)
   print("Future extrapolations:", result.forecast)

   ax = plot_forecast(result)
   plt.show()

If ``smoothness`` and ``lambda_`` are both omitted, the library defaults to
``smoothness=0.8``. Providing both raises an error. Setting
``smoothness=1`` uses the exact infinite-penalty limit of the trend estimator.

Smoothness is the normalized index

.. math::

   s(\lambda)=\frac{n-\operatorname{tr}\bigl((I+\lambda D_d^\top D_d)^{-1}\bigr)}
                  {n-d},

where ``d`` is the forward-difference order and ``n`` is the length of
the observed history. **80% smoothness does not mean 80% forecast
accuracy or an 80% confidence interval.**

Extrapolation rules
-------------------

The fitted PLS trend is ``tau``. Let ``b`` be the least-squares slope
calculated over its last ``window`` values. For future step ``h >= 1``:

- ``local_linear``: extrapolate ``tau[-1] + h*b``.
- ``last_value``: extrapolate the last historical fitted trend value.
- ``damped_linear``: extrapolate ``tau[-1] + b*sum(damping**k, k=1..h)``.

The first future value connects directly to the last smoothed trend,
so local regression intercepts do not create an artificial jump at the
boundary. These are assumptions, not competing methods with
established accuracy rankings. If the historical end point changes
when more data arrive, the extrapolation may change.

Full executable notebook pipeline
---------------------------------

:doc:`notebooks/10-forecast-pipeline` combines the entire workflow:
CSV or seeded synthetic observations, chronological training/test split,
fixed 0.8 smoothness, trend extrapolation, all six visualizations, and
out-of-sample MAE/RMSE with a naive baseline.

.. code-block:: console

   python scripts/run_notebooks.py --fast --only 10-forecast-pipeline --fail-fast

The held-out observations are not used to fit the trend. The single
holdout is illustrative, not evidence of robust forecasting performance.

A gallery of six plots
----------------------

The visualization functions return Matplotlib Axes or Figures so
their titles, scales, annotations and exported files can be customized.

.. code-block:: python

   from trendestimation import (
       plot_forecast, plot_forecast_dashboard, plot_forecast_methods,
       plot_residual_diagnostics, plot_smoothness_comparison,
       plot_smoothness_path,
   )

   plot_forecast(result)                 # 1. Individual observations + trend + horizon
   plot_smoothness_comparison(y)          # 2. Compare .2/.5/.8/.95
   plot_forecast_methods(result)          # 3. Constant, linear, damped baselines
   plot_smoothness_path(result)           # 4. Smoothness versus lambda
   plot_residual_diagnostics(result)      # 5. Residual 2x2 dashboard
   plot_forecast_dashboard(result)        # 6. Six-panel trends/assumptions dashboard

All plots use a restrained blue/white style. Forecast-area shading
only marks the **future period**; it is not a confidence band.
Residual diagnostics describe **in-sample** fit, not forecast errors.

Generate six sample PNG files (manual)
--------------------------------------

Run from the repository root (after installing the plotting extra):

.. code-block:: console

   python -m pip install -e ".[plot]"
   python examples/forecast_gallery.py --output-dir build/forecast-gallery

The script uses seeded, **synthetic** history, then produces:

1. ``01-observations-trend-and-forecast.png``
2. ``02-smoothness-comparison.png``
3. ``03-extrapolation-methods.png``
4. ``04-smoothness-path.png``
5. ``05-residual-diagnostics.png``
6. ``06-six-panel-dashboard.png``

No expensive automatic figure-rendering workflow is installed.
You can use an explicit matplotlib ``fig.savefig("my-figure.png", dpi=180)``
on any returned figure. See :doc:`api` for complete signatures.

Scientific scope
----------------

The smoothing stage follows classical finite-difference penalized
least squares and Guerrero's mean-reference formulation. Forecasting
is new **software functionality** consisting of transparent
post-smoothing extrapolation rules. It has **not** been evaluated with
rolling-origin validation, compared against random walks, ARIMA/ETS
or state-space models, nor supplied with statistically calibrated
prediction intervals.

Do not describe the resulting extrapolations as forecasting-optimal.
Validation is required before using the output to make financial
or scientific predictions.
