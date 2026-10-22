# trendestimation — publication-scope package (candidate v0.1)

A standalone Python distribution dedicated to published finite-difference
penalized least-squares (PLS) trend smoothing. The **distribution name** and
**import name** are both **trendestimation**. This subproject is distinct from
the existing research distribution, which also exposes experimental forecasting
methods.

## What is included

- Arbitrary admissible integer difference orders 0 <= d < n. Very high orders
  can be numerically ill-conditioned.
- Zero, fixed nonzero, and Guerrero (2007) observed-difference plug-in mean
  (mu="data").
- Reusable spectral solver, exact infinite-penalty limit, and smoothness/EDF.
- Classical **in-sample** CV, GCV, AICc, BIC for **fixed numeric mu** as in
  Cortés-Toto, Guerrero, and Reyes (2017).
- Reproducible linear/nonlinear synthetic examples from that 2017 article.
- Optional Matplotlib plots of fitted trends and classical selection curves.

**Not included:** forecast-optimal smoothing, horizon-h/rolling TSCV,
time-dependent local-minimum tracking, Sturm methods for forecast losses,
or prototype estimation of a forecast-optimal mean.

For mu="data", classical selector formulas are intentionally not exposed as
exact leave-one-out methods, because the plug-in itself changes under deletion.
Conditional EDF is not the EDF of a jointly data-selected mu procedure.

## Local installation

From the root of the existing Trend-Estimation repository:

    python -m pip install -e "packages/trendestimation[dev,docs,plot]"
    python -m pytest packages/trendestimation/tests -q
    python -m sphinx -b html packages/trendestimation/docs packages/trendestimation/docs/_build/html

After scientific review, a wheel can be built with:

    python -m build packages/trendestimation

**No PyPI publication or documentation-site deployment has been performed.**
Package-name reservation/availability and release credentials require review.

## Example

    import numpy as np
    from trendestimation import TrendSmoother, select_lambda, plot_trend

    y = 0.03 * np.arange(100) + np.random.default_rng(42).normal(0, 0.25, 100)
    solver = TrendSmoother(len(y), order=2)
    choice = select_lambda(solver, y, criterion="gcv", mu=0.0)
    fit = solver.fit(y, lambda_=choice.lambda_, mu=0.0)
    print(choice.lambda_, choice.smoothness)
    ax = plot_trend(y, fit)

    # Published Guerrero observed-difference plug-in:
    fit_with_mean = solver.fit(y, lambda_=choice.lambda_, mu="data")

## Computation and claims

For D_d the order-d forward-difference matrix, we solve the penalized
objective ||y-tau||^2 + lambda ||D_d tau - mu*1||^2.

A reusable full SVD costs O(n^3) once and O(n^2) memory. For a fixed n, d,
and projected series, the spectral trace, normalized smoothness, GCV, AICc,
and BIC evaluations require O(n) operations per candidate lambda. A full
trend fit and exact CV leverage scoring require O(n^2) operations each.
Banded solvers may be faster for a single fit or very long series; the
forthcoming SMCCA paper must include measured, fair comparisons rather
than claim unconditional performance superiority.

## Literature

1. Guerrero (2007), Time series smoothing by penalized least squares,
   Statistics & Probability Letters 77, 1225-1234.
2. Cortés-Toto, Guerrero, and Reyes (2017), Trend smoothness achieved by
   penalized least squares with the smoothing parameter chosen by optimality
   criteria, Communications in Statistics - Simulation and Computation
   46(2), 1492-1507. DOI 10.1080/03610918.2015.1005236.
3. Weinert (2007), Efficient computation for Whittaker-Henderson smoothing,
   Computational Statistics & Data Analysis 52, 959-974.
