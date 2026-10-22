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
- Fixed-smoothness (e.g., 0.8) conditional trend extrapolation, with six blue/white Matplotlib visualization styles.

**Not included:** forecast-optimal smoothing, validated forecast intervals, horizon-specific/rolling
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

The [eight Jupyter notebook tutorials](docs/gallery.rst) cover trend fitting,
finite-difference matrices, CV/GCV/AICc/BIC, fixed and plug-in difference means,
published-style simulations, spectral diagnostics, numerical benchmarks, and
illustrative economic, actuarial, and engineering use cases. The notebooks use
seeded synthetic data; they are not evidence of future forecasting accuracy.

Run notebook examples and record timings using:

```bash
python scripts/run_notebooks.py --list
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

Only equally spaced one-dimensional observations are supported. Smoothing
the full series is not an out-of-sample forecast evaluation.

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
