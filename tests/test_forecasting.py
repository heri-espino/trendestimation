"""Tests for fixed-smoothness extrapolation and optional gallery visualizations."""
import numpy as np
import pytest
from numpy.testing import assert_allclose

from trendestimation import (
    TrendSmoother,
    forecast_trend,
    plot_forecast,
    plot_forecast_dashboard,
    plot_forecast_methods,
    plot_residual_diagnostics,
    plot_smoothness_comparison,
    plot_smoothness_path,
)


def test_default_smoothness_matches_direct_solver():
    y = np.random.default_rng(51).normal(size=54)
    result = forecast_trend(y, horizon=9)
    direct = TrendSmoother(len(y), 2)
    lam = direct.lambda_for_smoothness(.8)
    assert result.smoothness == pytest.approx(.8, abs=1e-8)
    assert result.lambda_ == pytest.approx(lam, rel=1e-8)
    assert_allclose(result.fit.trend, direct.fit(y, lambda_=lam).trend, atol=1e-9)
    assert_allclose(result.observed, y)
    assert_allclose(result.future_index, np.arange(54, 63))
    assert result.horizon == 9


@pytest.mark.parametrize("smoothness", [0, .2, .8, .95, 1])
@pytest.mark.parametrize("order", [0, 1, 2, 3])
def test_smoothing_targets_and_finite_forecasts(smoothness, order):
    y = np.random.default_rng(17).normal(size=30)
    r = forecast_trend(y, horizon=8, smoothness=smoothness, order=order)
    assert r.smoothness == pytest.approx(smoothness, abs=1e-8)
    assert r.forecast.shape == (8,)
    assert np.all(np.isfinite(r.forecast))
    assert np.isinf(r.lambda_) == (smoothness == 1)


def test_local_linear_exact_unpenalized_trend():
    y = 2.5 + .12 * np.arange(50, dtype=float)
    r = forecast_trend(y, horizon=12, smoothness=.8, order=2, window=15)
    assert_allclose(r.fit.trend, y, atol=1e-9)
    assert r.slope == pytest.approx(.12, abs=1e-10)
    assert_allclose(r.forecast, 2.5 + .12 * np.arange(50, 62), atol=1e-9)


def test_linear_anchoring_and_damped_increment_formula():
    y = 1 + .06 * np.arange(50) + .1 * np.sin(np.arange(50) / 8)
    a = forecast_trend(y, horizon=5, method="local_linear", window=10)
    b = forecast_trend(y, horizon=5, method="damped_linear", damping=.5, window=10)
    assert_allclose(a.forecast, a.fit.trend[-1] + a.slope * np.arange(1, 6))
    assert_allclose(b.forecast, b.fit.trend[-1] + b.slope * np.cumsum(.5 ** np.arange(1, 6)))
    assert_allclose(a.fit.trend, b.fit.trend)


def test_last_value_and_explicit_lambda():
    y = np.random.default_rng(26).normal(size=40)
    result = forecast_trend(y, horizon=3, lambda_=2.5, method="last_value")
    assert result.lambda_ == 2.5
    assert result.slope == 0
    assert_allclose(result.forecast, result.fit.trend[-1])


def test_no_future_observation_leakage():
    rng = np.random.default_rng(7)
    history = rng.normal(size=55)
    future_truth = rng.normal(loc=20, size=8)
    first = forecast_trend(history, horizon=8)
    second = forecast_trend(history.copy(), horizon=8)
    assert_allclose(first.forecast, second.forecast)
    assert not np.allclose(first.forecast, future_truth)


@pytest.mark.parametrize("kwargs", [
    {"horizon": 0}, {"horizon": -1}, {"horizon": 1.1},
    {"horizon": True}, {"smoothness": 1.1}, {"smoothness": np.nan},
    {"smoothness": .8, "lambda_": 2},
    {"lambda_": -2}, {"order": 100},
    {"window": 1}, {"window": 99}, {"window": 3.1},
    {"method": "unknown"}, {"damping": 0}, {"damping": 1.1},
])
def test_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        forecast_trend(np.arange(20, dtype=float), **kwargs)


@pytest.mark.parametrize("y", [[], [np.nan, 4.0], [[1, 2], [3, 4]]])
def test_invalid_observations(y):
    with pytest.raises(ValueError):
        forecast_trend(y)


def test_gallery_smoke_without_gui():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    y = .04 * np.arange(45) + np.random.default_rng(12).normal(0, .3, 45)
    r = forecast_trend(y, horizon=8, smoothness=.8)
    axes = [
        plot_forecast(r),
        plot_smoothness_comparison(y),
        plot_forecast_methods(r),
        plot_smoothness_path(r),
    ]
    for ax in axes:
        assert len(ax.lines) >= 1
        plt.close(ax.figure)
    for make in (plot_residual_diagnostics, plot_forecast_dashboard):
        fig = make(r)
        assert len(fig.axes) == (4 if make is plot_residual_diagnostics else 6)
        plt.close(fig)


def test_plot_helpers_reject_invalid_arguments():
    import matplotlib
    matplotlib.use("Agg")

    y = np.arange(15, dtype=float)
    r = forecast_trend(y, horizon=4)
    with pytest.raises(ValueError):
        plot_smoothness_comparison(y, smoothness_levels=[])
    with pytest.raises(ValueError):
        plot_smoothness_path(r, points=3)
    with pytest.raises(ValueError):
        plot_forecast_methods(r, damping=-.1)
