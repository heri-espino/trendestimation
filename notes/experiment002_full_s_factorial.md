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



## 9. Extension: one call, complete grid, repeated grids and coordinate optimization

The follow-up extends Experiment002 rather than replacing or
reinterpreting its validated seven-backend/five-criterion full-S
candidate audit.

### Computational questions that MUST remain separate

1. **One score at a prescribed S=0.5** for a single y. Compare
   known-lambda scoring (no mapping), direct S (invert on each
   invocation) and premapped S-to-lambda (invert once and reuse).
2. **One complete 17-point grid search**, including the exact
   limits S=0 and S=1 (lambda=0 and infinity analytically).
3. **Repeated searches across independent y** with the same
   grid. Compare cold backend preparation for every series
   with preparation shared across 3 or 8 series.
4. **Different finite grids:** direct 17-point log-lambda
   grid with the *same* two finite extreme penalties and
   exact boundary limits, but different interior points.
   A different minimum is discretization, not proof of an
   improved continuous optimization algorithm.
5. **True bounded local continuous optimization:** minimize
   C(S^-1(s)) or C(exp(x)), x=log(lambda). Evaluate the same
   underlying criterion with both analytical boundaries
   considered. The two paths use different evaluation locations
   and variable function-call counts. SciPy bounded minimization
   may miss a global minimum; it must never be described as an
   exhaustive global search.

### Fair computational accounting

Every backend/criterion/series is verified against the canonical
spectral numerical score *outside the measured interval*.
A valid complete-grid winner must score **all 15 finite
interior points** correctly (or report a mathematically
undefined criterion value) and include preparation and
evaluation time. An invalid/unstable backend may not be ranked
as the fastest by computing fewer points.

For each record the experiment stores:
- backend setup time, total scored evaluation time, and
  one-time common S-grid inversion separately;
- standalone elapsed time with inversion charged once for
  pretranslating S into lambda;
- candidate count / local optimizer evaluation count;
- the chosen normalized S and criterion score;
- numerical validity, d0 MLE applicability, n, d, mu, R,
  source host, BLAS threads and seed.

A shared S-grid inversion is paid once for **all**
method/criterion searches that use its mapped penalties,
not once per one of seven backends or five statistical
criteria; sums of per-method standalone times would
double-count that common work. Native S search instead
pays inversion for each evaluated S target and every
repeated run. With a pre-existing directly supplied
lambda grid, no inversion of S is necessary.

Cold and warm repeated runs are compared at matched
d/mu/criterion/backend/grid and observations.
Reuse of a Cholesky factor at a *different* lambda is
not assumed; only d-specific setup is shared by the
existing backend. Exact infinite penalty is always
treated analytically, never by Cholesky.

### Source files

- `paper/benchmarks/full_s_search_modes.py`
- `paper/benchmarks/full_s_search_reference/search_mode_timings.csv`
- `paper/benchmarks/full_s_search_reference/search_grid_preparation.csv`
- `paper/benchmarks/full_s_search_reference/environment.json`
- `paper/figures/render_full_s_search_modes.py`
- `docs/full_s_factorial.rst`
- `paper/sections/full_s_factorial.tex`

AwesomeFigures/Springer-matched vector outputs:
`full_s_single_grid_repeated`,
`full_s_search_reuse_speedup`,
`full_s_grid_coordinate_times`,
`full_s_continuous_coordinate_times`,
`full_s_coordinate_selected_s` (.pdf and .svg).

Quick preset: n=24, all d0..5, both mu, all seven backends,
all five criteria (MLE d0 N/A), R=1 and R=3, cold/shared
preparation, three 17-point grid policies, three single
evaluation variants and two local continuous optimizers.
The full Windows preset adds n=48, R=8 and a second seed.
A focused smoke preset exists for CI and incremental testing.
Keep Linux reference timings and Windows/VM timings separate.

**No claims of universal fastest method or forecasting accuracy
follow from one-host microbenchmarks.** The continuous-coordinate
optimization and fixed discrete candidate-grid comparisons answer
different numerical questions. An optimized S is a coordinate, not
a new statistical selection criterion.



### Actual GitHub reference measurements (2026-10-26, quick preset)

The complete 13,440-row quick experiment passed the numerical
tests and all five PDF/SVG publication graphs compiled. Its source
of truth is
`paper/benchmarks/full_s_search_reference/search_mode_timings.csv`,
with independent machine/BLAS provenance in `environment.json`.
These are **not Windows VM numbers**.

For a single seeded observation series, n=24, d=2,
fixed mu=0, spectral SVD, one BLAS thread and two repetitions,
all numbers below are observed **milliseconds**, and stand-alone
mapped timings include the corresponding one-time inversion:

| Criterion | Single known lambda | Single native S | Single mapped S | 17-pt native S | 17-pt mapped S, once | 17-pt log lambda |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CV | 0.166 | 0.391 | 0.264 | 2.220 | 2.165 | 0.612 |
| GCV | 0.144 | 0.374 | 0.276 | 2.113 | 2.019 | 0.384 |
| AICc | 0.148 | 0.376 | 0.258 | 2.170 | 2.046 | 0.413 |
| BIC | 0.156 | 0.390 | 0.267 | 2.154 | 2.063 | 0.427 |
| Conditional MLE | 0.184 | 0.405 | 0.274 | 2.215 | 2.122 | 0.483 |

For the 17-point **matched** S-based grids, each selected
value agreed between native S and pretranslation:
CV 0.7, GCV 0.7, AICc 0.8, BIC 0.1 and MLE 0.6.
The independent log-lambda grid uses DIFFERENT interior
candidates, so it can choose a different optimum.

The one-time 17-point inversion was about **1.627 ms**.
Adding five native-S selector times gives **10.872 ms**.
For a common once-mapped grid used by all five criteria,
sum the five *backend-only* times (**2.278 ms**) and
charge the mapping once (**1.627 ms**), giving about
**3.905 ms**. Ratio: **2.78x** in this setup.
By contrast, for one isolated GCV grid search the
standalone cost is nearly equal: native 2.113 ms versus
mapped-once 2.019 ms. The difference between a
one-off operation and amortization across multiple
criteria is the substantive finding.

The direct log-lambda sample can be much faster here
because it does not invert the S grid, **but evaluates
different candidate penalties**. The observed speed
difference does NOT imply that its discrete optimum
has lower loss or that it explores the same S nodes.

True bounded local optimizers were also measured.
For GCV, bounded S took **1.826 ms** and bounded
log-lambda **0.554 ms**, with matching selected
S approximately 0.695064 on this dataset.
For BIC the two bounded optimizers selected distinct
local solutions (approximately S=0.1 versus S=0.698721);
this is a **non-global local-search warning**, not
evidence of a different criterion or mathematical
failure of the monotone coordinate transform.
The finite 17-point grid itself selected BIC S=0.1.

With three independent series at d=2, GCV SVD,
the total *backend-only* time was approximately
**0.936 ms shared** versus **1.132 ms cold**,
a measured cold/shared ratio of **1.21x**.
Both approaches selected identical smoothness values
for the paired series; ratio precision is descriptive
only. Banded Cholesky and other backends should not
be given universal speed rankings when their extreme
tail candidates are numerically invalid.

These numbers use one hosted Linux runner, fixed seed,
two timer repetitions, n=24 and BLAS threads=1;
they are not multi-session inferential evidence.
Mapped-S timing comparisons must never double-count
one shared inversion across methods, criteria or series.


## 11. Completed Windows full run: source archive and reproducible report

The author's `full` search-mode benchmark has been uploaded as
**80,640 original records**, at
`paper/benchmarks/results/full_s_search_modes/search_mode_timings.csv`.
It is an independent **Windows** machine run, not the hosted Linux
quick-preset timing dataset.

The actual `environment.json` records two simulated seeds
(20261026 and 20261027), `n=24,48`, all orders `d=0..5`,
fixed `mu=0,.15`, all five criteria, all seven backends,
`R=1,3,8`, cold/shared preparation, eight search policies,
seven timing repeats, one BLAS thread, and Python 3.11.
A separate grid-preparation CSV measures the once-per-order
smoothness-to-penalty conversion.

Source-preserving integration is implemented by
`paper/benchmarks/report_windows_full_s.py`.
The script validates the **entire 80,640-cell factorial**, aggregates
the two seeds per cell (median), checks pairwise native-S versus
premapped-lambda selected smoothness on successful paired runs,
and writes `paper/benchmarks/windows_full_s_analysis/`.
It produces measured Springer tables and five PDF/SVG AwesomeFigures
pairs using the **Windows** CSV alone.

The resulting manuscript section is
`paper/sections/windows_full_s_results.tex`; its table is
data-generated as `paper/sections/windows_full_s_generated.tex`.
The website is `docs/windows_full_s_results.rst` with an
automatically regenerated data summary. These outputs are
part of the same GitHub integration PR as the original uploaded
Windows results, and the original Linux reference records remain intact.

**Important analysis limitations:**
(a) S-grid and converted-lambda grid use the SAME candidates,
so they must select equivalent statistical optima;
(b) independent log-lambda grid uses DIFFERENT interior candidates;
(c) continuous bounded optimization is only local;
(d) invalid or incomplete high-S backends cannot be ranked as
complete-grid winners;
(e) MLE at d=0 is not applicable;
(f) exact S=1 has lambda=infinity and is handled analytically;
(g) timings on Windows and Linux must not be pooled as if
they were a single randomized cross-platform trial.

For a complete rebuild from the already-uploaded data (no
80,640-cell recomputation), use:

~~~powershell
conda activate trendestimation
python paper/benchmarks/report_windows_full_s.py
python paper/build.py --figures --pdf --package
$env:TRENDESTIMATION_DOCS_EXECUTION="off"
python -m sphinx -W --keep-going -b html docs build/site
~~~

All derived outputs, compiler artifacts, metadata, tests, and
next research steps must be committed and pushed before an
ephemeral VM is discarded.



## 12. Marp lecture integration (2026-10-27)

Professor research lecture source:
`slides/professor_lecture/main.md`, chapter X-D, with five
vector illustrations staged by `slides/professor_lecture/windows_full_results.py`
from the EXACT paper SVGs. Manifest includes SHA-256 hashes and
explicitly labels the originating Windows 80,640-cell run.
No new numerical observations are synthesized.
The lecture distinguishes complete 17-target grid searches,
single scores, cold/warm R=8 experiments, bounded local
optimization, and proper equal-candidate S-to-lambda parity.
It records illustrative n=48, d=2, mu=0 timings
(CV 2.004/1.879ms, GCV 1.851/1.800ms, AICc 1.887/1.810ms,
BIC 2.016/1.810ms, MLE 3.477/2.035ms) and the
11.234ms native-versus-3.980ms once-mapped combined five-criterion
comparison. The independent log-lambda grid does NOT visit
the same interior candidate set.

Compile from root without re-running the expensive experiment:

```powershell
conda activate trendestimation
python -m pip install -r paper/requirements.txt
python paper/benchmarks/report_windows_full_s.py
python paper/build.py --figures --pdf --package
powershell -ExecutionPolicy Bypass -File slides/professor_lecture/build.ps1
```

The paper PDF is already versioned in GitHub. New local PDF builds
should be committed/pushed, retaining all upstream data and source
code; do not stage unrelated cache or licensed literature.
