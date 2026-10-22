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
- Reusable SVD-based solver, exact infinite-penalty limit, smoothness indices,
  and conditional effective degrees of freedom (EDF).
- Classical **in-sample** CV, GCV, AICc, and BIC smoothing-parameter
  selection for a **fixed numeric** reference mean, as studied by Cortés-Toto,
  Guerrero, and Reyes (2017).
- Reproducible synthetic linear/nonlinear examples and optional Matplotlib plots.

**Not included:** forecast-optimal smoothing, horizon-specific/rolling
time-series cross-validation (TSCV), dynamic local-minimum tracking, Sturm
methods for forecast losses, or prototype estimation of forecast-optimal means.

For `mu="data"`, the standard CV formula is not claimed to be an exact
leave-one-out refit because the plug-in mean would also require re-estimation.
EDF calculations condition on a fixed value of the mean.

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
fit = solver.fit(y, lambda_=choice.lambda_, mu=0.0)
print("lambda:", choice.lambda_)
print("smoothness:", choice.smoothness)
print("conditional EDF:", fit.edf_conditional)
plot_trend(y, fit)

# Guerrero observed-difference plug-in fitting (not ordinary CV for this mu):
fit_with_mean = solver.fit(y, lambda_=choice.lambda_, mu="data")
```

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

Only equally spaced one-dimensional observations are supported. Smoothing
the full series is not an out-of-sample forecast evaluation.

## Development

```bash
python -m pytest -q
python -m ruff check src tests benchmarks
python -m sphinx -b html docs docs/_build/html
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
