# trendestimation

[![CI](https://github.com/trendestimation/trendestimation/actions/workflows/ci.yml/badge.svg)](https://github.com/trendestimation/trendestimation/actions/workflows/ci.yml)

**Candidate v0.1.0a0** — a Python library for finite-difference penalized
least-squares (PLS) trend estimation. Both distribution and import names are
`trendestimation`.

The library implements **published trend-smoothing methods**, not the experimental
forecast-optimal smoothing algorithms under development in separate research.
The canonical project repository is [trendestimation/trendestimation](https://github.com/trendestimation/trendestimation).

## Capabilities

- Integer differencing orders `0 <= d < n`; very high orders may be ill-conditioned.
- Zero, fixed nonzero, and Guerrero (2007) observed-difference plug-in reference means (`mu="data"`).
- Alternative full-trend reconstruction backends (SVD, dense symmetric eigendecomposition,
  and banded Cholesky) with matched reproducible benchmarks via
  `PreparedPLSSolver` / `fit_penalized`. Their **fit-only default is banded
  Cholesky**; these return trends only, without replacing the established
  **spectral default for CV/GCV/AICc/BIC/MLE selection**, EDF, and normalized smoothness.
- Reusable SVD-based solver, exact infinite-penalty limit, both smoothness
  indices (normalized and Guerrero's original), and conditional EDF.
- Smoothness-first fitting with `fit_smoothness(y, smoothness=0.86, order=2)`
  or `TrendSmoother.fit_smoothness(...)`, which hides the internal lambda
  inversion without changing the classical PLS estimator. The existing
  lambda API remains supported for compatibility.
- Optional parameter search in either penalty **lambda** (existing default)
  or bounded, normalized **smoothness S in [0, 1]**. Classical CV supports
  analytical derivative refinement in both coordinates; other criteria
  use a grid. This is a reparameterization, not a new score.
- Classical **in-sample** CV, GCV, AICc, and BIC smoothing-parameter
  selection for a **fixed numeric** reference mean, as studied by Cortés-Toto,
  Guerrero, and Reyes (2017).
- Gaussian **marginal maximum likelihood** (MLE), with observation variance
  profiled out and unpenalized trend coordinates removed (REML-style).
  Accepts a fixed numeric mean or observed-difference plug-in mu="data".
  This is a marginal statistical likelihood, not minimization of the PLS
  objective over lambda; it relies on Gaussian variance-component assumptions.
- Gaussian variance-component estimates at a selected positive penalty:
  observation-noise and latent *d*-th-difference variance (plus standard
  deviations). Their model ratio equals lambda. These are profile-likelihood
  estimates, not raw residual MSE or the variance of the full latent trend.
- Reproducible synthetic linear/nonlinear examples and optional Matplotlib plots.
- Fixed-smoothness conditional historical-trend extrapolation with three transparent
  rules and six blue-and-white visualization helpers (not validated forecasts).

**Not included:** forecast-optimal smoothing, statistically calibrated forecast intervals,
horizon-specific/rolling
time-series cross-validation (TSCV), dynamic local-minimum tracking, Sturm
methods for forecast losses, or prototype estimation of forecast-optimal means.

For mu="data", the library sets mu = mean(D_d @ y): the arithmetic mean
of the observed d-th differences, not the raw mean of y unless d=0.
The standard CV/GCV/AICc/BIC formulas require fixed numeric mu; CV is
not an exact leave-one-out refit of this plug-in mean. The Gaussian MLE
criterion permits mu="data", but then conditions on the empirical plug-in
rather than performing joint maximum likelihood over mu and lambda.
Reported effective degrees of freedom likewise condition on mu.

## Installation

Python 3.10 or newer. From the root of a checkout:

```bash
python -m pip install -e .
```

For plotting, testing, documentation, and package checks:

```bash
python -m pip install -e '.[dev,docs,plot]'
```

You may alternatively use `python -m pip install -r requirements.txt`
or `python -m pip install -r requirements-dev.txt`. For Conda:

```bash
conda env create -f environment.yml
conda activate trendestimation
```

This is a **source-installation** workflow; the package is not represented
as published on PyPI.

## Example

```python
import numpy as np
from trendestimation import TrendSmoother, select_lambda, plot_trend

y = 0.03 * np.arange(100) + np.random.default_rng(42).normal(0, 0.25, 100)
solver = TrendSmoother(len(y), order=2)
choice = select_lambda(solver, y, criterion="gcv", mu=0.0)
# Same GCV criterion, but search a normalized smoothness grid:
choice_s = select_lambda(
    solver, y, criterion="gcv", mu=0.0,
    search_space="smoothness",
)
print("selected smoothness:", choice_s.smoothness)
print("corresponding lambda:", choice_s.lambda_)
fit = solver.fit(y, lambda_=choice.lambda_, mu=0.0)
print("lambda:", choice.lambda_)
print("smoothness:", choice.smoothness)
print("conditional EDF:", fit.edf_conditional)
plot_trend(y, fit)

# Guerrero's original n-denominator smoothness:
original_smoothness = solver.smoothness(choice.lambda_, normalized=False)
same_lambda = solver.lambda_for_smoothness(
    original_smoothness, normalized=False,
)
print("Original smoothness:", original_smoothness)

# Gaussian marginal maximum likelihood, numeric or plug-in mean:
ml = select_lambda(solver, y, criterion="mle", mu="data")
ml_fit = solver.fit(y, lambda_=ml.lambda_, mu="data")
print("MLE lambda:", ml.lambda_, "plug-in mu:", ml_fit.mu)

# Both Gaussian variance components at the selected penalty:
from trendestimation import estimate_variance_components
variances = estimate_variance_components(
    solver, y, lambda_=ml.lambda_, mu="data",
)
print("Noise variance:", variances.observation_variance)
print("Latent difference variance:", variances.difference_variance)
```

## Fixed-smoothness trend extrapolation and plots

The package provides a deliberately simple conditional extrapolation of an
**estimated historical trend**. It is not a model selected for forecasting accuracy.

```python
import numpy as np
from trendestimation import forecast_trend, plot_forecast, plot_forecast_dashboard

history = np.arange(100) * .04 + np.random.default_rng(7).normal(0, .3, 100)
result = forecast_trend(history, horizon=12, smoothness=.8, window=20)
print(result.lambda_, result.smoothness, result.forecast)
plot_forecast(result)
figure = plot_forecast_dashboard(result)
figure.savefig("trend-dashboard.png", dpi=160)
```

Other plots compare smoothing targets, forecast extrapolation assumptions, the
penalty/smoothness curve and in-sample residual diagnostics. Generate six
reproducible synthetic PNGs **manually** with:

```bash
python examples/forecast_gallery.py --output-dir build/forecast-gallery
```

See [forecasting and visualization documentation](docs/forecasting.rst).
The future region is a visual demarcation, not a prediction interval.
An 80% normalized smoothness level **does not imply 80% accuracy**.

## Reproducible notebook gallery

The [thirteen research Jupyter notebook tutorials](docs/gallery.rst) cover trend fitting,
finite-difference matrices, CV/GCV/AICc/BIC, fixed and plug-in difference means, Gaussian MLE and Guerrero smoothness,
published-style simulations, spectral diagnostics, numerical benchmarks, and
illustrative economic, actuarial, and engineering use cases. The notebooks use
seeded synthetic data; they are not evidence of future forecasting accuracy.

The [full trend-forecast pipeline](docs/notebooks/10-forecast-pipeline.ipynb)
combines smoothness 0.8, an optional numeric CSV, plotting the observed
points, multiple extrapolation assumptions, six visualization functions,
and genuine chronological holdout MAE/RMSE against a naive baseline.

Run notebook examples and record timings using:

```bash
python scripts/run_notebooks.py --list
python scripts/run_notebooks.py --fast --only 10-forecast-pipeline --fail-fast
python scripts/run_notebooks.py --fast --fail-fast
```

To write executed notebook output for the documentation build, explicitly pass
`--in-place`. Timing logs and machine metadata are saved under
`build/notebook-runs/`; illustrative electricity costs require explicit
watts and tariff inputs in MXN/kWh. The GitHub Pages workflow is manual and
does not automatically deploy on pushes.

## Statistical and numerical scope

For the order-`d` forward difference operator `D_d`, the fitted
trend is a minimizer of

$$
\|y-\tau\|_2^2 + \lambda\|D_d\tau-\mu\mathbf{1}\|_2^2.
$$

The reusable full SVD costs `O(n^3)` preprocessing time and `O(n^2)` memory.
Once the observations are projected, spectral traces and GCV/AICc/BIC
scores require `O(n)` per candidate parameter; full trend reconstruction
and ordinary CV leverage scoring cost `O(n^2)` each. Specialized banded
solvers can be faster for long time series or single fits; no universal
speed advantage is claimed.

The Gaussian MLE criterion uses covariance eigenvalues
sigma^2 * (1 + 1/(lambda*delta_j)) on the n-d positive-penalty coordinates
(delta_j > 0), profiles sigma^2 and minimizes twice negative profiled
marginal log-likelihood (up to constants). The nullspace is treated as an
unpenalized nuisance component. lambda=0 is excluded as an improper
infinite-variance prior; lambda=infinity is evaluated exactly. Near-degenerate
constant or polynomial data may not identify a finite likelihood optimum.
This is inspired by Gaussian marginal-likelihood smoothing discussed by
Biessy (2026), Section 5.3, with an additional profiled-variance step.

Only equally spaced one-dimensional observations are supported. Smoothing
the full series is not an out-of-sample forecast evaluation.

## Formal solver benchmark study

A publication-oriented, *manual* matched benchmark of SVD, symmetric
`eigh` and banded Cholesky saves **all raw times**, numerical parity,
CPU/BLAS metadata, seed-level bootstrap confidence intervals, two-sided
paired sign-flip p-values and Holm adjustments for primary comparisons.
The outputs include LaTeX tables, Markdown interpretation and SVG/PNG/PDF
figures for future paper and Marp integration. No presentation branch is
modified.

```bash
python -m pip install -e . threadpoolctl matplotlib
python benchmarks/formal_solver_study.py --preset quick --seeds 20 --repeats 5 --threads 1 --output-dir paper/benchmarks/solver_study_runs/pilot-01
python benchmarks/analyze_formal_solver_study.py --input-dir paper/benchmarks/solver_study_runs/pilot-01 --bootstrap 10000 --permutations 50000
```

Alternatively run the [manual formal benchmark workflow](.github/workflows/formal-solver-study.yml), optionally archiving its evidence permanently to a dedicated results-only Git branch. See [the statistical protocol](docs/benchmark_statistical_protocol.rst) before interpreting p-values; timing blocks are *not* independent samples.


## Publish generated research outputs to the repository

After running the benchmarks and statistical analysis on your own machine,
publish the **actual local evidence**, optional manuscript PDF and generated
Marp figures without staging unrelated files. In Windows PowerShell:

~~~powershell
git switch main
git pull --ff-only origin main
python scripts/publish_generated_outputs.py
python scripts/publish_generated_outputs.py --publish
~~~

The first command is a preview; the second creates a separate
results-only branch, commits allowlisted outputs with SHA-256 provenance,
and pushes it to GitHub. If GitHub CLI is configured it also creates
a pull request; otherwise it prints a direct link. Ignored outputs
under build/solver-study are automatically copied to a publishable
study-run directory. No source code or Marp presentation branch is changed.

For details and safety restrictions, see
[Publishing research outputs](docs/publishing-research-outputs.md).

## Development

```bash
python -m pytest -q
python -m ruff check src tests benchmarks
TRENDESTIMATION_DOCS_EXECUTION=off python -m sphinx -b html -W docs build/site
python -m build
python -m twine check dist/*
```

Lint and unit tests run automatically in lightweight CI. Package builds and
documentation validation require manual triggering; publication to PyPI and
deployment of documentation are **not** automated. Run the numerical
benchmark manually via `python benchmarks/compare_banded.py`.

See [CONTRIBUTING.md](CONTRIBUTING.md), [CHANGELOG.md](CHANGELOG.md),
[LICENSE](LICENSE), and [CITATION.cff](CITATION.cff).

## Author and affiliation

**Heriberto Espino-Montelongo**  
Universidad de las Américas Puebla (UDLAP)  
ORCID: [0009-0009-1230-2931](https://orcid.org/0009-0009-1230-2931)

The affiliation identifies the author's institution and does not imply
institutional ownership or endorsement.

## Methodological references

1. Guerrero, V. M. (2007). *Time series smoothing by penalized least squares*.
   *Statistics & Probability Letters*, 77, 1225–1234.
2. Cortés-Toto, D., Guerrero, V. M., and Reyes, H. J. (2017).
   *Trend smoothness achieved by penalized least squares with the smoothing
   parameter chosen by optimality criteria*. *Communications in Statistics –
   Simulation and Computation*, 46(2), 1492–1507.
   [DOI 10.1080/03610918.2015.1005236](https://doi.org/10.1080/03610918.2015.1005236).
3. Weinert, H. L. (2007). *Efficient computation for Whittaker–Henderson
   smoothing*. *Computational Statistics & Data Analysis*, 52, 959–974.

The MIT license applies to the **original software and project-authored
documentation**, not to third-party scientific papers or figures.


## Measured solver choices by task

For a **known lambda** and trend-only output, use the banded-Cholesky
default; for **parameter selection or spectral diagnostics**, use the SVD
selector (unchanged):

```python
from trendestimation import fit_penalized, TrendSmoother, select_lambda

trend_only = fit_penalized(y, lambda_=30, order=2, mu=0.15)
solver = TrendSmoother(len(y), order=2)
choice = select_lambda(solver, y, criterion="gcv", mu=0.15)
diagnostics = solver.fit(y, lambda_=choice.lambda_, mu=0.15)
```

Our [GCV grid/reuse benchmark](docs/grid_reuse_selection.rst) uses six
solvers, matched normalized-S/log-penalty candidate budgets, fixed
nonzero mu, multiple difference orders and repeated independent series.
Banded Cholesky often wins full-trend sweeps, while SVD was fastest for
GCV selection in the recorded reference cases. Results and
[executed charts](docs/notebooks/13-grid-search-repeated-solvers-orders.ipynb)
are specific to a declared hosted-Linux environment; no universal
ranking or faster uniform-S search is claimed.
