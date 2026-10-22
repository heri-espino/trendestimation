"""trendestimation: published finite-difference PLS, no forecasting extensions."""
from .core import FitResult, TrendSmoother, difference_matrix, fit_trend
from .criteria import SelectionResult, score_lambda, select_lambda
from .examples import SimulatedSeries, simulate_cortes_toto
from .plotting import plot_selection, plot_trend

__all__ = [
    "FitResult", "TrendSmoother", "difference_matrix", "fit_trend",
    "SelectionResult", "score_lambda", "select_lambda",
    "SimulatedSeries", "simulate_cortes_toto",
    "plot_selection", "plot_trend",
]
__version__ = "0.1.0a0"
