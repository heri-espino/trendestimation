# Numerical coordinate × solver × criterion: factorial experiment

## Research aim

**Question.** For the same finite-difference penalized-least-squares
estimator and the same fixed-\(\mu\) criterion, is it computationally
preferable to (A) choose \(\lambda\) and report \(S(\widehat\lambda)\),
or (B) search directly over \(s\in[0,1]\) and compute
\(\widehat\lambda=S^{-1}(\widehat s)\)? How does that answer change
under three genuinely different linear-algebra backends and four
classic selection criteria?

This is a **new experimental protocol**, not a previously established
speed result, theorem of algorithmic superiority, or claim of better
out-of-sample forecasting performance. We intend it as candidate
experimental evidence for the Springer *Computational Statistics*
working paper and as a detailed discussion notebook for the professor.

## Statistical setup

For \(n>d\ge1\), fixed numeric \(\mu\), and \(\lambda\ge0\),

\[
\widehat\tau_{\lambda,\mu}
=\arg\min_\tau \bigl\{\|y-\tau\|_2^2+
\lambda\|D_d\tau-\mu\mathbf 1\|_2^2\bigr\},
\qquad H_\lambda=(I+\lambda D_d^\top D_d)^{-1}.
\]

The affine shift is \(p_{\mu,t}=\mu\binom td\),
\(\widehat\tau=p_\mu+H_\lambda(y-p_\mu)\).

The **normalized** smoothness coordinate is

\[
s=S(\lambda)=
\frac{n-\operatorname{tr}(H_\lambda)}{n-d}
=\frac{1}{n-d}\sum_{j=1}^{n-d}
\frac{\lambda\delta_j}{1+\lambda\delta_j},
\quad S(0)=0,\quad S(\infty)=1.
\]

The positive finite-penalty eigenvalues satisfy \(\delta_j>0\).
This is *not* Guerrero's original \(n\)-denominator index.

For each fixed criterion \(C\in\{\mathrm{CV},\mathrm{GCV},
\mathrm{AICc},\mathrm{BIC}\}\),

\[
\min_{\lambda\in[0,\infty]} C(\lambda;\mu)
\quad\text{and}\quad
\min_{s\in[0,1]} C(S^{-1}(s);\mu)
\]

describe the same ideal minimizer set under exact arithmetic and
identical full domains; differences in finite searches are numerical,
grid-selection or implementation effects.

**The question about direction is not a question about a new optimum.**
Searching in \(\lambda\) incurs a single \(S\) conversion at the end;
searching in \(s\) typically entails *one scalar inversion per target*.
But uniform-\(s\) spacing can explore a different part of the
smoother family than a geometric-\(\lambda\) mesh. Compare attained
scores as well as time.

The four criteria follow `src/trendestimation/criteria.py` exactly:

\[
\mathrm{CV}=n^{-1}\sum_i(e_i/(1-h_{ii}))^2,\quad
\mathrm{GCV}=(\mathrm{RSS}/n)/(1-\nu/n)^2,
\]
\[
\mathrm{AICc}=\log(\mathrm{RSS}/n)+(2\nu+1)/(n-\nu-2),
\quad
\mathrm{BIC}=\log(\mathrm{RSS}/n)+\nu\log(n)/n.
\]

Zero-residual and singular-denominator boundary candidates must
retain the source-library undefined/infinite conventions.
These are **in-sample criteria**, not rolling-horizon forecast scores.

## Numerical backends: different workloads

| Backend | Preparation | Criterion and inversion evaluation |
| --- | --- | --- |
| SVD of \(D_d\) | Full dense SVD, store basis | Trace and RSS spectral; CV needs leverage diagonal |
| `eigh(D_d.T @ D_d)` | Form \(Q_d\), diagonalize | Same spectral attenuation equations; weaker conditioning possible |
| Banded Cholesky | Prepare only \(d+1\) penalty bands | Refactor \(I+\lambda Q_d\) per \(\lambda\); obtain needed diagonal and trace via solves of all \(n\) identity columns |

The Cholesky \(\mathrm{CV}\) and \(\mathrm{GCV}\) cells must **not**
borrow precomputed SVD leverage or trace. In
`benchmarks/criterion_coordinate_matrix.py`, Cholesky uses
`scipy.linalg.cholesky_banded` and
`scipy.linalg.cho_solve_banded` for these quantities, including
every iteration of \(S^{-1}\).

This is purposefully a *correct but potentially expensive* direct
trace strategy, not a claim that no specialized diagonal-of-inverse,
recursion or GCV computation could be more efficient.
Weinert (2007, 2012) establish earlier efficient structured
smoothing methods and motivate including them as future competitors.
Do **not** call the old `scipy.linalg.solve_banded` baseline
in `paper/benchmarks/` a measured Cholesky speed.

## Experiment I — 36-cell finite-grid factorial

Cartesian product:
- solver: `svd`, `eigh`, `cholesky`;
- criterion: `cv`, `gcv`, `aicc`, `bic`;
- coordinate: `lambda`, `s_mapped`, `s_uniform`.

For each case (\(n,d,\mu\)), seed and timing block:

1. Construct **identical log-\(\lambda\) candidates** for all three
   solvers. Direct-\(\lambda\) search evaluates these and converts
   only the selected winner to \(S\).
2. **Mapped \(S\)** uses a single *out-of-timing* canonical SVD to
   prepare the \(s_j=S(\lambda_j)\) candidate targets. Each backend
   independently inverts those targets (Cholesky from Cholesky trace).
   This experimental control isolates *per-backend coordinate
   inversion* rather than charging one method for design construction.
   Score and selected penalty should agree numerically with direct
   \(\lambda\) search.
3. **Native \(S\)** uses the same *number* of uniformly spaced
   interior \(s\)-targets, but **not the same penalties**.
   These different grids permit examining time/score trade-offs,
   **not** inferring that one factorization computes the same candidate
   list faster.
4. All cells measure setup, inversion, score-evaluation,
   winner-to-\(S\) conversion and end-to-end time. Record exact
   factorization type, trace evaluations, criterion calls and
   \(\widehat\lambda,\widehat s,C(\widehat\lambda)\).
5. Before timing, test cross-backend agreement at matched penalties.
   Randomize method/criterion/coordinate order in each timing block.
   Repeat **independent data seeds**, not merely repeated micro-timers.

**No global optimization claim:** the finite penalty/S grids do not
guarantee the absolute global minimum and omit exact boundary points
from the initial timed factorial. Boundary behavior is independently
tested by existing library regressions and warrants its own stress
experiment. Strong \(\lambda\) extremes and large \(d\) can make
Cholesky trace calculations and \(\mathrm{eigh}(Q_d)\) numerically
unstable. Explicit errors are preferable to silently changing solvers.

## Experiment II — actual default selector

`benchmarks/public_coordinate_optimizer_benchmark.py` measures the
**released** `select_lambda(...,method="auto")` for
`search_space="lambda"` and `"smoothness"` across all four
criteria, including model construction.

For CV, the current implementations do not use the same candidate
budget. The \(\lambda\) mode samples 97 log-penalty candidates plus
refinements and boundary evaluations; the \(S\) mode samples a
uniform plus logit-spaced \(S\) mesh, adds inversion and refines
derivative roots. For GCV, AICc and BIC, default grids also differ.

Therefore **report evaluated candidate count, attained criterion score
and total time** before drawing practical conclusions.

These experiments test different questions:
- **Factorial mapped grids** isolate arithmetic differences and
  inverse overhead at matched statistical candidate values.
- **Public auto selectors** measure the currently released user
  experience, including different search policies.

## Run manually, preserve raw observations

From repository root:

```bash
python -m pip install -e ".[plot]" threadpoolctl

python benchmarks/criterion_coordinate_matrix.py \
  --preset smoke --seeds 1 --repeats 2 --threads 1
python benchmarks/public_coordinate_optimizer_benchmark.py \
  --preset smoke --seeds 1 --repeats 2 --threads 1

python benchmarks/criterion_coordinate_matrix.py \
  --preset quick --seeds 3 --repeats 4 --threads 1
python benchmarks/public_coordinate_optimizer_benchmark.py \
  --preset quick --seeds 3 --repeats 4 --threads 1

python slides/professor_lecture/make_figures.py
bash slides/professor_lecture/build.sh --html-only
```

Windows users should use
`powershell -ExecutionPolicy Bypass -File slides/professor_lecture/build.ps1`.

The default outputs under `build/criterion-coordinate-study/` are:

- `raw_trials.csv`, `summary.csv`, `environment.json`
  for factorial selection;
- `public_raw.csv`, `public_summary.csv`,
  `public_environment.json` for the released API.

The lecture generator creates its objective plots deterministically
from a seeded series. Its runtime plots are built **only from actual
CSV measurements** and display an explicit missing-data panel until
those files exist. It does not invent or hard-code winners.

Prior to a journal claim, increase repetitions and independent seeds;
check numerical errors and convergence failures; record CPU, library,
BLAS, OS, source revision, benchmark process, and timing environment.
Perform matched paired-seed inference and report uncertainty and
multiple-testing methodology. The standalone script reports medians
and median absolute deviations, not automatically validated
confidence intervals or Holm-adjusted tests.

## Follow-up extensions after the factorial

1. Add direct, well-defined optimization algorithms (Brent,
   derivative bracketing, logit-\(s\) multistart) at matched budgets
   and numerical tolerances. Do not conflate root inversion with
   criterion optimization.
2. Accelerate trace and leverage for banded Cholesky without
   requiring a full dense hat matrix, citing existing fast
   diagonal-of-inverse/Whittaker–Henderson algorithms.
3. Compare actual penalized splines and discrete difference-penalized
   trends **as distinct estimators**, making any knot, boundary and
   penalty-normalization choices explicit. A spline result is not
   automatically transferable to the discrete PLS family.
4. For forecast-optimal selection, evaluate chronological origin/
   horizon validation independently of ordinary LOOCV.
5. Test noisy smooth and kinked trends, seasonality, autocorrelation
   and adversarial high-order condition numbers. Do not represent
   a single synthetic family as comprehensive evidence.

## Key sources

- Cortés-Toto, D., Guerrero, V. M., and Reyes, H. J. (2017),
  _Trend smoothness achieved by penalized least squares with the
  smoothing parameter chosen by optimality criteria_,
  DOI 10.1080/03610918.2015.1005236.
- Weinert, H. L. (2007), _Efficient computation for
  Whittaker–Henderson smoothing_,
  DOI 10.1016/j.csda.2006.11.038.
- Weinert, H. L. (2012, Springer copyright 2013), _Fast Compact
  Algorithms and Software for Spline Smoothing_,
  DOI 10.1007/978-1-4614-5496-0.
- Current `notes/smoothness_parameterization.md` and
  `src/trendestimation/criteria.py` for the actual implemented
  smoothness map and criterion conventions.
