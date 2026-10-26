# Experiment002 — Complete S-domain numerical factorial

**Date:** 2026-10-26. **Status:** reproducible in-sample
computational experiment and publication-figure candidate, NOT a
forecasting validation or evidence of a universally fastest solver.

## Historical context

PR #57 created full S-coordinate plots; #59 introduced the six-way
Cholesky study; #61 compared real GCV grid searches with repeated
independent series and orders; #62 selected workload-specific defaults
(banded Cholesky for trend-only, spectral for criteria); #63 added
AwesomeFigures and conditional Gaussian marginal MLE to public
S versus lambda selector comparisons.

Experiment002 removes the finite-grid truncation and extends those
separate efforts into **seven numerical backends × five statistical
criteria × two fixed difference means × all orders d=0..5 × the
complete S=[0,1] candidate domain**.

## 1. The mathematical grid and its endpoints

\[
S_d(\lambda)=\frac1{n-d}\sum_{j=1}^{n-d}
  \frac{\lambda\delta_j}{1+\lambda\delta_j}.
\]

Candidate set: 11 deciles (0,0.1,...,1) plus .95, .99,
.999, .9999, .999999, and .999999999999: **17 distinct
targets, 15 finite interior and two exact endpoints**.

At S=0, lambda=0, tau=y, EDF=n. Ordinary CV/GCV scores
are undefined for the interpolation-only fit, not zero.
At S=1, lambda=+infinity, EDF=d. For d>=1 the trend
is the degree-(d-1) polynomial nullspace projection
adjusted by the fixed reference p_mu,t=mu*binom(t,d);
for d=0 it approaches the constant vector mu*1.
S=1 is **NOT a very large finite lambda**. There is
no finite Cholesky/LU factor at infinite penalty.
End points are evaluated analytically, marked
`analytic_limit`, and NOT assigned fabricated
finite-factorization times.

## 2. Full Cartesian numerical experiment

Seven numerical backends:
`dense_fresh`, `dense_cached`, `general_banded`,
`dense_cholesky`, `banded_cholesky`,
`eigh` (symmetric diagonalization), `svd`.

Five criteria:
`cv` (ordinary fixed-mu exact LOOCV),
`gcv`, `aicc`, `bic`, `mle` (Gaussian profiled
marginal likelihood conditioned on fixed mu).

Fixed mu is 0 or 0.15, and the same seeded observed y
is used for matched mu comparisons. Difference orders
d=0,1,2,3,4,5 are all covered.

**MLE d=0 is NOT APPLICABLE under the implemented
Gaussian model.** The public MLE routine explicitly
requires d>=1. The experiment does not make up a
replacement likelihood; all seven solvers and both
means have `not_applicable_d0_mle` records.

For positive finite lambda, CV needs the diagonal of
the hat matrix; GCV/AICc/BIC need EDF and RSS.
MLE needs a method-specific Gaussian quadratic and
log-determinant, but NOT unnecessary EDF/LOOCV
leverage calculations. It is NOT a seventh solver.
The general banded implementation incurs a distinct
determinant cost because its SciPy solve interface
does not expose it for free. The score calculations
are compared numerically against the library's
spectral `score_lambda` on the SAME penalties.
The baseline validation sits OUTSIDE measured blocks.

## 3. Why extreme S is numerically important

High d and S=.999999999999 can require extremely
large finite penalties. The matrix I+lambda D.T D
then becomes ill-conditioned. A direct solver's score
may be inaccurate even if it returns a number, and
a Cholesky factorization can fail. This is numerical
instability, not a statistical decision to choose a
different smoothing level.

Three distinct data states must NOT be conflated:
`ok` (criterion score matches spectral baseline);
`unstable_numerics` or `factorization_failed_*`
(numerical method fails); and
`criterion_undefined` (the mathematical criterion
does not return an admissible finite score).
Endpoints are always `analytic_limit`; MLE d0
is `not_applicable_d0_mle`.

A valid full-grid speed comparison requires all 15
interior candidate evaluations to be numerically
acceptable and the criterion defined. A method that
fails near S=1 cannot win by being fast on fewer
candidate evaluations.

## 4. Archive, measurements and interpretation

The GitHub-hosted quick run uses n=24, a fixed
seed 20261026, two timed repeats and one BLAS thread.

- `paper/benchmarks/full_s_reference/candidate_scores_and_times.csv`:
  all individual criterion/backend/target results, timings,
  errors, undefined/failure states and endpoints.
- `paper/benchmarks/full_s_reference/full_grid_summary.csv`:
  406 meaningful complete-grid records (excluding
  d0 MLE N/A) with validity flags and selected S.
- `paper/benchmarks/full_s_reference/s_lambda_grid.csv`:
  all 17 S-to-lambda mappings per d, including
  lambda=0 and lambda=infinity, for each d.
- `paper/benchmarks/full_s_reference/environment.json`:
  Python/SciPy/NumPy, host, BLAS threads and seed.

For the quick GCV results with n=24, mu=0, the
spectral implementation completes all fifteen
interior points for d=0..5. For d>=2, the direct
methods typically fail to agree at the extreme
finite near-1 candidate. This is precisely why
the original bounded lambda study cannot establish
a solver winner for the entire smoothness range.
Some high-order AICc scores become mathematically
undefined at very extreme penalties; those are
not solver failures.

The measurements describe **one Linux-hosted
runtime environment**, not the author's separate
Windows full run and not statistically supported
cross-machine universal speed differences.

## 5. Figures, paper and site

The pinned AwesomeFigures renderer
`paper/figures/render_full_s_factorial.py`
reads the raw real CSVs, using the actual Springer
manuscript's measured font size and text width.
It emits matching PDF/SVG vectors:
- `full_s_time_{cv,gcv,aicc,bic,mle}`: time by d,
  hiding methods that do not complete the full grid;
- `full_s_validity_{gcv,mle}`: numerical agreement
  count out of 15 interior candidates;
- `full_s_selected_{mu0,mu015}`: selected S
  by criterion and d, including endpoint candidates;
- `full_s_lambda_tail`: finite lambda growth
  near S=1, excluding infinite penalty only from
  the logarithmic axis, never from the evaluated grid.

Website page: `docs/full_s_factorial.rst`.
Springer manuscript: `paper/sections/full_s_factorial.tex`.

## 6. Run it from Windows PowerShell

~~~powershell
git switch main
git pull --ff-only origin main
conda activate trendestimation
python -m pip install -e ".[dev,docs,plot]"
python -m pip install -r paper/requirements.txt
python paper/benchmarks/full_s_backend_criteria.py --preset full --repeats 5
~~~

The full preset adds n=48 and a second independent seed,
and by default writes to
`paper/benchmarks/results/full_s_backend_criteria/`.
Do NOT overwrite Linux reference results with Windows
results. Persist meaningful raw CSV, machine environment,
failure logs, plots, interpretation and next steps on GitHub.
Never rely on an ephemeral machine or chat transcript
as the only copy of research.

## 7. Remaining research questions

1. Repeat under independent seeds and sessions and
   estimate uncertainty on paired solver runtime ratios.
2. Analyze conditioning and score accuracy at each high-S
   candidate; potentially test higher precision or
   structure-aware methods rather than claim all backends
   numerically interchangeable at huge lambda.
3. Test continuous derivative-CV, Brent and native-S
   optimization separately; the present experiment is a
   complete 17-point *grid*, not certified continuous
   global optimization.
4. Test chronological forecast-horizon validation rather
   than call ordinary GCV or CV a forecasting comparison.
5. MLE for d0 would need a separately derived likelihood
   and should not bypass the public model guard.
6. Compare multiple n and reference means, and keep
   the prior 16-point S-vs-lambda timing experiment
   distinct from this 17-point domain study.
7. Regenerate journal PDFs and website SVGs whenever
   results change, with real AwesomeFigures source and
   exact manuscript typography, and archive all outputs.


## 8. Verified publication artifacts and CI evidence

The complete hosted quick run, pinned AwesomeFigures rendering, strict
Sphinx build, Springer PDF build and ZIP packaging all succeeded in
[GitHub Actions run 40386201940](https://github.com/heri-espino/trendestimation/actions/runs/40386201940).
Ten PDF/SVG figure pairs, the four reference data/provenance files,
`paper/main.pdf` and `paper/computational-statistics-submission.zip`
were committed to the feature branch before merge. The run's downloadable
artifact includes the measurements and rendered publication output.

The separate numerical and publication smoke tests passed; figure paths
are verified as actual files rather than placeholders.
