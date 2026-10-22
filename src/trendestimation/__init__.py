"""trendestimation: classical PLS smoothing and transparent trend extrapolation."""
from .core import FitResult, TrendSmoother, difference_matrix, fit_trend
from .criteria import SelectionResult, cv_derivative, score_lambda, select_lambda
from .likelihood import VarianceComponents, estimate_variance_components
from .examples import SimulatedSeries, simulate_cortes_toto
from .plotting import plot_selection, plot_trend
from .forecasting import TrendForecast, forecast_trend
from .forecast_plots import (
    plot_forecast, plot_forecast_dashboard, plot_forecast_methods,
    plot_residual_diagnostics, plot_smoothness_comparison, plot_smoothness_path,
)

__all__ = [
    "FitResult", "TrendSmoother", "difference_matrix", "fit_trend",
    "SelectionResult", "cv_derivative", "score_lambda", "select_lambda",
    "VarianceComponents", "estimate_variance_components",
    "SimulatedSeries", "simulate_cortes_toto",
    "plot_selection", "plot_trend",
    "TrendForecast", "forecast_trend",
    "plot_forecast", "plot_forecast_dashboard", "plot_forecast_methods",
    "plot_residual_diagnostics", "plot_smoothness_comparison", "plot_smoothness_path",
]
__version__ = "0.1.0a0"
