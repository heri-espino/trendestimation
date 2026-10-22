# trendestimation

**Published-methods Python software for finite-difference penalized least-squares trend smoothing.**

[Documentation](https://trendestimation.github.io/trendestimation/) ·
[Source repository](https://github.com/trendestimation/trendestimation) ·
[Executable notebook gallery](docs/gallery.rst)

`trendestimation` implements the finite-difference penalized trend estimator
discussed by Guerrero (2007) and Cortés-Toto, Guerrero & Reyes (2017).
It is intentionally separated from unpublished trend forecasting research.

## Capabilities

- Every admissible integer difference order `0 <= d < n`, subject to floating-point conditioning.
- Fixed difference mean `mu=0`, fixed nonzero `mu`, and Guerrero's `mu="data"` plug-in.
- Reusable spectral solver and exact infinite-penalty nullspace projection.
- Conditional effective degrees of freedom and normalized smoothness.
- Published **in-sample** CV, GCV, AICc and BIC criteria for **fixed numeric mu**.
- A reproducible illustrated gallery containing **eight Jupyter notebooks**.
- Timing, memory-scaling and optional assumption-based energy/cost measurements.

The package **does not** implement forecast-horizon TSCV, predictive
smoothness selection, temporal local-minimum branches or prototype optimizers.

## Install

Clone this repository and run these commands **from its root**:

```bash
python -m pip install -e ".[dev,docs,plot]"
python -m pytest -q
```

## First example

```python
import numpy as np
from trendestimation import TrendSmoother, select_lambda, plot_trend

y = 0.03*np.arange(100) + np.random.default_rng(42).normal(0, 0.25, 100)
solver = TrendSmoother(len(y), order=2)
choice = select_lambda(solver, y, criterion="gcv", mu=0.0)
fit = solver.fit(y, lambda_=choice.lambda_)
print("lambda =", choice.lambda_, "normalized smoothness =", choice.smoothness)
plot_trend(y, fit)

# Guerrero (2007) observed-difference plug-in for fitting:
fit_with_mean = solver.fit(y, lambda_=10, mu="data")
```

The classical selector formulas require fixed `mu`. The reported
conditional EDF is not the complete degrees of freedom of a method
that estimates `mu` from the same data.

## Illustrated notebook gallery

| Notebook | Scope |
| --- | --- |
| [01 — Your first trend](docs/notebooks/01-first-trend.ipynb) | Fits, residuals, penalty trade-off |
| [02 — Differencing orders](docs/notebooks/02-differencing-orders.ipynb) | `d=1,2,3,4`, difference matrices and null spaces |
| [03 — Selection criteria](docs/notebooks/03-classical-criteria.ipynb) | CV, GCV, AICc, BIC and recovered trends |
| [04 — Nonzero mean](docs/notebooks/04-nonzero-mean.ipynb) | Guerrero fixed/reference means |
| [05 — Cortés-Toto atlas](docs/notebooks/05-cortes-toto-atlas.ipynb) | Published-style simulations and comparisons |
| [06 — Spectral diagnostics](docs/notebooks/06-spectral-diagnostics.ipynb) | Eigenvalues, attenuation, EDF and smoothness |
| [07 — Runtime benchmarks](docs/notebooks/07-computational-benchmarks.ipynb) | Spectral vs banded, cost and machine metadata |
| [08 — Applied workflows](docs/notebooks/08-applied-workflows.ipynb) | Illustrative economic, actuarial and sensor uses |

Each chapter includes **explanatory Markdown, executable Python and figures**.
The website renders the *same* notebooks without maintaining separate copies
of their source material.

## Execute every notebook, with timing records

```bash
python scripts/run_notebooks.py --list
python scripts/run_notebooks.py --fast --fail-fast
python scripts/run_notebooks.py --fast --in-place --fail-fast
python -m sphinx -b html docs build/site
```

Results, `timings.csv`, and a machine/versions `manifest.json` are stored
under `build/notebook-runs/`. Only `--in-place` writes displayed notebook
outputs into tracked notebook paths. Timing measurements are specific to the
machine where you run the script. The runner can estimate electricity cost
in MXN only if you supply average watts and MXN per kWh, **not** otherwise.

The GitHub Pages workflow is **manual** (`workflow_dispatch`) to avoid
running heavy examples automatically every time a developer pushes.

## Mathematical and computational positioning

For the order-`d` difference matrix `D`, the estimator minimizes

`||y - tau||² + lambda ||D tau - mu*1||².`

With the penalty spectral decomposition computed once, scalar
trace-based scores and GCV/AICc/BIC can be evaluated quickly for many
lambda candidates. Full SVD setup requires `O(n³)` work and `O(n²)`
storage; full trend reconstruction takes `O(n²)` per lambda. In many
single-fit cases a structured banded solve is faster, so performance claims
must compare full setup and repeated-fit costs against that baseline.

## References

- Guerrero, V. M. (2007). *Time series smoothing by penalized least squares*,
  Statistics & Probability Letters 77, 1225–1234.
- Cortés-Toto, D., Guerrero, V. M., and Reyes, H. J. (2017).
  *Trend smoothness achieved by penalized least squares with the smoothing
  parameter chosen by optimality criteria*,
  Communications in Statistics — Simulation and Computation 46(2), 1492–1507.
  DOI: 10.1080/03610918.2015.1005236.
- Weinert, H. L. (2007). *Efficient computation for Whittaker–Henderson
  smoothing*, Computational Statistics & Data Analysis 52, 959–974.

See [SMCCA research positioning](SMCCA_REFOCUS.md). This pre-release is
software implementing established mathematics; it is not a claim of
a newly discovered smoothing estimator or improved future forecasts.
