import numpy as np
import pytest
from numpy.testing import assert_allclose

from trendestimation import TrendSmoother, difference_matrix, select_lambda, fit_trend


@pytest.mark.parametrize("d", [0, 1, 2, 3, 5])
@pytest.mark.parametrize("mu", [0.0, 0.3])
def test_finite_matches_direct_normal_equations(d, mu):
    rng = np.random.default_rng(31 + d)
    y = rng.normal(size=14)
    D = difference_matrix(len(y), d)
    lam = 3.25
    rhs = y + lam * mu * D.T @ np.ones(D.shape[0])
    expected = np.linalg.solve(np.eye(len(y)) + lam * (D.T @ D), rhs)
    actual = fit_trend(y, order=d, lambda_=lam, mu=mu).trend
    assert_allclose(actual, expected, rtol=3e-8, atol=3e-8)


@pytest.mark.parametrize("d", [0, 1, 2, 3])
def test_infinite_penalty_enforces_reference_difference(d):
    rng = np.random.default_rng(17)
    y = rng.normal(size=20)
    smoother = TrendSmoother(len(y), d)
    mu = 0.3
    fit = smoother.fit(y, lambda_=np.inf, mu=mu)
    assert_allclose(smoother.D @ fit.trend, mu, atol=1e-8)
    assert_allclose(smoother.smoothness(np.inf), 1.0)
    assert_allclose(smoother.degrees_of_freedom(np.inf), d)


def test_data_mu_matches_mean_observed_differences():
    y = np.linspace(2, 8, 50) + np.sin(np.arange(50))
    solver = TrendSmoother(len(y), 1)
    result = solver.fit(y, lambda_=50.0, mu="data")
    assert result.mu == pytest.approx(float(np.mean(np.diff(y))))
    with pytest.raises(ValueError):
        select_lambda(solver, y, mu="data")


def test_smoothness_inverse_and_monotonicity():
    solver = TrendSmoother(35, 2)
    assert solver.smoothness(0) == pytest.approx(0)
    for s in (0.05, 0.3, 0.75, 0.95):
        assert solver.smoothness(solver.lambda_for_smoothness(s)) == pytest.approx(s, abs=1e-8)
    assert np.isinf(solver.lambda_for_smoothness(1))


@pytest.mark.parametrize("criterion", ["cv", "gcv", "aicc", "bic"])
def test_classical_selection_returns_reported_minimum(criterion):
    rng = np.random.default_rng(21)
    y = np.linspace(0, 2, 45) + rng.normal(scale=0.3, size=45)
    solver = TrendSmoother(45, 2)
    choice = select_lambda(solver, y, criterion=criterion, mu=0.1)
    assert np.isfinite(choice.score)
    assert choice.score == pytest.approx(min(choice.scores))
    assert 0 <= choice.smoothness <= 1


def test_source_simulations_are_reproducible():
    from scipy.stats import beta
    from trendestimation import simulate_cortes_toto

    case = simulate_cortes_toto(n=50, shape="linear", seasonal=True, seed=7)
    assert_allclose(case.trend, 4.0 * np.arange(1, 51) / 50)
    assert_allclose(case.seasonality[:4], [1, -0.5, -2.5, 2])
    assert_allclose(case.observed, case.trend + case.seasonality + case.noise)
    other = simulate_cortes_toto(n=50, shape="linear", seasonal=True, seed=7)
    assert_allclose(other.observed, case.observed)
    nonlinear = simulate_cortes_toto(n=50, shape="nonlinear", noise_sd=0)
    x = np.arange(1, 51) / 50
    assert_allclose(nonlinear.trend, 0.6 * beta.pdf(x, 30, 17) + 0.4 * beta.pdf(x, 3, 11))


def test_plotting_returns_axes():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from trendestimation import plot_selection, plot_trend

    y = np.arange(20.0) + np.sin(np.arange(20))
    sm = TrendSmoother(len(y), 2)
    fit = sm.fit(y, lambda_=20)
    selection = select_lambda(sm, y, criterion="gcv")
    assert plot_trend(y, fit) is not None
    assert plot_selection(selection) is not None
    plt.close("all")


def test_cv_matches_explicit_leave_one_out_fixed_nonzero_mu():
    from trendestimation import score_lambda
    rng = np.random.default_rng(99)
    n, d, lam, mu = 15, 2, 7.0, 0.15
    y = rng.normal(size=n)
    sm = TrendSmoother(n, d)
    cv = score_lambda(sm, y, lambda_=lam, mu=mu, criterion="cv")
    errors = []
    for withheld in range(n):
        weights = np.ones(n)
        weights[withheld] = 0
        D = sm.D
        A = np.diag(weights) + lam * (D.T @ D)
        b = weights * y + lam * mu * D.T @ np.ones(n - d)
        prediction = np.linalg.solve(A, b)[withheld]
        errors.append((y[withheld] - prediction) ** 2)
    assert cv == pytest.approx(np.mean(errors), rel=1e-9)
