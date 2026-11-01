# Research prototype: direct normalized-S spectral weights

## Definition and motivation

Users specify normalized S in [0,1], and the fitted curve is the
existing quadratic finite-difference PLS estimator. We do not form the
penalty lambda explicitly when reconstructing the trend.

**Concurrent work:** open PR #79 already implements a convenience
fit_smoothness API, but its implementation internally translates S to
lambda and reuses the lambda-based fitter. Our experimental
fit_spectral_smoothness function uses a *different execution path* and
does not modify that PR or the existing default library backend.

## Mathematical derivation

For D_d=U diag(sigma) V.T, write r=n-d and delta_j=sigma_j^2>0.
Choose delta_* as exp(median(log delta_j)), and ratios
a_j=delta_j/delta_*. Define a reference shrinkage weight u in (0,1).

w_j(u) = a_j u / (1-u+a_j u),

and solve the strictly monotonic scalar equation

(1/r) sum_j w_j(u) = S.

The resulting trend is

tau_S = y - V [w*(V.T y) - mu*(w/sigma)*(U.T 1)].

The numerical routine solves x=logit(u), keeping all calculations
in the log domain and evaluating the complementary smoothness tail
near S=1. At S=0 all shrinkage weights are zero; at S=1 they are one.

**Do not overclaim:** x is related to log(lambda) by an additive
constant. This is precisely the same implicit scalar inversion in
different coordinates. It is not an inversion-free algorithm, a new
smoother, or a guaranteed computational improvement.

## Usage on the independent feature branch

~~~python
import numpy as np
from trendestimation import TrendSmoother
from trendestimation.smoothness_weights import fit_spectral_smoothness

y=np.sin(np.linspace(0,6,80))
model=TrendSmoother(len(y),order=3)
direct=fit_spectral_smoothness(model,y,smoothness=.8,mu="data")
lam=model.lambda_for_smoothness(.8)
mapped=model.fit(y,lambda_=lam,mu="data")
np.testing.assert_allclose(direct.trend,mapped.trend,rtol=1e-8,atol=1e-8)
~~~

## Testing and limitations

Run:

~~~powershell
python -m pip install -e ".[dev]"
python -m pytest -q tests/test_spectral_smoothness_weights.py
~~~

Tests compare identical n,d,data,S,mu settings over d=1..6,
including fixed nonzero and observed d-th-difference means, endpoint
cases, and near-one smoothing targets. The tests certify algebraic
parity within stated double-precision tolerances, not a timing gain.

- One reusable SVD: O(n^3) arithmetic / O(n^2) memory for small d.
- Scalar logit root: O(k(n-d)) work for k iterations.
- One full fitted trend: O(n(n-d)) spectral reconstruction.
- For many series with equal n,d and S, it is better to cache
  the spectral shrinkage vector directly rather than repeat the root.
- The prototype returns the fitted trend and conditional EDF but
  deliberately does not return lambda. If interoperability requires
  lambda, it can be calculated from the implicit logit root.
- mu="data" is an observed-difference plug-in and its trace EDF is
  conditional; it is not jointly refitted LOOCV.
- Exact S=1 is an infinite-penalty polynomial-constrained limit, not
  a dense inverse evaluated at infinite lambda.

## Workflow and next research question

Reconcile PR #79 with the modern main branch first. Its older
fit() implementation must not overwrite the shift-free fitting code
or published numerical accuracy changes. If the distinct direct-weight
backend passes regression tests, run a fresh reproducible timed
experiment comparing:
(a) inversion+fit,
(b) scalar direct-weight root+fit,
(c) cached smoothness weights across repeated series.
Measure setup, per-evaluation, memory, and numerical differences
against the same multiprecision reference. Preserve all raw outputs,
scripts, notes and figures in the repository; do not claim an
efficiency improvement until matched timing confirms it.
