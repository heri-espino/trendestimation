# experiment001 — From normalized smoothness to solver defaults and MLE figures

**Project:** trendestimation / Computational Statistics draft.  
**Status:** reproducible repository experiment and manuscript visuals, not a submitted publication.  
**Research concern:** differentiating *solver arithmetic* from *criterion selection*,
and comparing fixed-mu, normalized-S vs lambda selection without changing
the objective being optimized.

## 1. Roadmap of what has actually been implemented

| Research step | Repository source of truth | What was established |
| --- | --- | --- |
| Core PLS and smoothness | `src/trendestimation/core.py`, `notes/smoothness_parameterization.md` | The monotone map S(lambda), its spectral derivative and exact boundary limits |
| Classical and likelihood criteria | `src/trendestimation/criteria.py`, `src/trendestimation/likelihood.py` | CV/GCV/AICc/BIC plus conditional profiled Gaussian MLE, each lower-is-better |
| Full-range paired S and lambda notebook | `src/trendestimation/_docs_coordinates.py`, docs notebook gallery | Eleven deciles plus S=.95,.99,.999,.9999,.999999; S=0↔lambda=0; S=1↔lambda=inf |
| Original full-fit versus EDF timing | `paper/benchmarks/run_benchmarks.py`, `trace_benchmarks.py` | General banded solve is not Cholesky; spectral EDF can beat full banded traces |
| Six-solver fit/trace with fixed mu | `paper/benchmarks/cholesky_comparison.py`, `cholesky_reference/` | Measured general banded, dense Cholesky and banded Cholesky separately; mu=.15 alters RHS |
| End-to-end grid selection | `paper/benchmarks/grid_reuse_study.py`, `grid_reuse_reference/` | Real GCV timing across d, mu, candidate counts and independent repeated series |
| Production default choice | `src/trendestimation/solvers.py` | Banded Cholesky default for trend-only output; spectral default for CV/GCV/AICc/BIC/MLE and EDF metadata |
| Current five-criterion visualization | `paper/benchmarks/selection_coordinate_mle.py`, `paper/figures/render_mle_benchmarks.py` | Matched 16-point penalty/S grids, independent log grid, five statistical scores; AwesomeFigures PDF/SVG |

**Related completed PRs:** #56 (Windows lecture), #57 (full-range S-grid and paper-timing notebooks),
#59 (six-way Cholesky benchmark), #61 (GCV grid/reuse/d study),
#62 (GCV results manuscript, website, defaults).
Future agents must not assume that a merged PR implies that
the author-generated Windows full-run CSV files are in GitHub.

## 2. Mathematical core and normalization

For equally spaced observations y in R^n, integer order 1<=d<n,
and **fixed numeric** reference-difference mean mu, minimize

\[
L(\tau;\lambda,\mu)=\|y-\tau\|^2+
  \lambda\|D_d\tau-\mu\mathbf1\|^2,\qquad
\lambda\in[0,\infty].
\]

Define Q_d=D_d^T D_d and H_lambda=(I+lambda Q_d)^(-1).
The normal equations and shift are

\[
(I+\lambda Q_d)\widehat\tau=y+
  \lambda\mu D_d^\top\mathbf1,\quad
\widehat\tau=p_\mu+H_\lambda(y-p_\mu),\quad
p_{\mu,t}=\mu {t\choose d}.
\]

For positive eigenvalues delta_1,...,delta_(n-d),

\[
S(\lambda)={n-\operatorname{tr}(H_\lambda)\over n-d}
={1\over n-d}\sum_{j=1}^{n-d}
{\lambda\delta_j\over1+\lambda\delta_j}.
\]

The derivative is positive at every finite nonnegative lambda,
so the extended inverse maps S=0 to lambda=0 and S=1 to lambda=infinity.
**This is normalized smoothness**, not Guerrero's original
1-tr(H)/n, and it is not a probability or measure of predictive accuracy.

A finite 11-decile S grid is interpretable but under-resolves the
S≈1 boundary. The extended default *documentation grid* adds
S=.95,.99,.999,.9999,.999999. Its 16 points do **not** imply
the public selector's own default has changed.

## 3. Distinguish three computational questions

**A. Single or multiple full trends for given penalties.**
Banded Cholesky exploits the half-bandwidth d of I+lambda Q;
new lambda implies a different Cholesky factorization. Actual
six-solver full-fit timings often favored banded Cholesky.

**B. Full *criterion* search.**
Classical GCV needs RSS and EDF=tr(H_lambda); classical LOOCV
needs diagonal leverages; marginal Gaussian MLE needs a profiled
likelihood. An inexpensive trend solve alone is insufficient.
The GitHub quick-preset GCV experiment found spectral SVD fastest
in recorded n=48,d=1..4,M=11 cases *including setup*. This is why
the default spectral TrendSmoother/select_lambda was preserved.

**C. Repeat exactly the same candidate grid on independent y.**
SVD/eigenstructure is independent of y and mu (for fixed numerical mu).
At a fixed candidate penalty the Cholesky factor and EDF can also be
cached across independent series; factors **cannot** be shared across
different lambda. Cold/warm comparisons must count real preparation
and score evaluations, and may depend on cache memory.

A GCV-only benchmark is not evidence for CV, AICc, BIC, MLE or
rolling-horizon forecast validation. Solver methods and criterion
methods must not be counted as the same factorial axis.

## 4. Criterion definitions and MLE's role

For conditional EDF nu and residual sum of squares RSS:

\[
GCV={RSS/n\over (1-\nu/n)^2},\quad
CV={1\over n}\sum_i (r_i/(1-h_{ii}))^2,
\]
\[
AICc=\log(RSS/n)+{2\nu+1\over n-\nu-2},\quad
BIC=\log(RSS/n)+{\nu\log n\over n}.
\]

For r=n-d **positive-penalty spectral coordinates** z_j
after eliminating unpenalized polynomial coordinates, with
c_j=1+1/(lambda delta_j), the implemented *conditional marginal*
Gaussian variance-profile score is

\[
C_{MLE}(\lambda)=r\log\left(
\frac{1}{r}\sum_j\frac{z_j^2}{c_j}\right)
+\sum_j\log c_j.
\]

It is twice negative profiled log-likelihood up to constants,
with observation variance profiled out. Lambda=0 is excluded as
an improper infinite-variance prior: C_MLE(0)=+infinity.
MLE here is neither a seventh numerical factorization nor joint
(mu,lambda) MLE. For mu="data" the empirical difference mean
is plugged in and the inference conditions on that plug-in.

**Important visualization rule:** Never compare raw values of MLE,
AICc, BIC or CV/GCV on one shared loss scale. Curves can be
shifted/rescaled individually to compare *shape/location*, with
explicit disclosure of the normalization. Compare chosen S,
chosen lambda and elapsed time separately. Minima of two genuinely
different grid policies may differ because their candidate sets differ.

## 5. Which S/lambda search is faster? Three policies

- `matched_lambda`: convert the same 16 S targets to lambda **once**
  (conversion cost stored separately), then reuse those penalties for
  *all five* public selection criteria.
- `native_s`: supply the same S targets directly to each selector;
  it independently inverts S for each method. Scores and selected
  lambda must agree with matched_lambda up to numerical tolerance.
- `log_lambda`: independent geometric finite-lambda interior,
  with lambda=0 and +inf endpoints. Equal candidate count but
  different interior candidates; descriptive alternative sampling
  *not* an algorithm-parity test.

The selection benchmark times the public select_lambda call with
the TrendSmoother object already constructed; separately records SVD
construction and precomputed grid inversion.
For full total cost add those common costs with correct reuse accounting.
All five criteria use the same fixed numeric mu=0 or mu=.15 within
an experimental cell. No claim about a universally fastest grid.

## 6. Measured evidence and provenance

The archived quick results in `paper/benchmarks/cholesky_reference/`
and `grid_reuse_reference/` were measured by **GitHub Linux runner**,
not by the author Windows VM.
The GCV comparison has n=48, R=1, M=11, mu=0, lambda-log:
spectral SVD total times near 0.63ms at d=1..4, with banded
Cholesky approximately 1.2–1.4ms. With R=4,d=2,M=11,
cold/warm ratio was approximately 2.76 (SVD) and 2.82
(banded Cholesky). These are observed timing-block ratios, not
multi-session statistical significance tests.

The separate Windows 11 VM full GCV run was reported by console:
360 cells, final examples n=80,d=5,M=11/21,R=4/10 at mu=0/.15;
all numerical parity checks passed, with spectral winning the
printed warm cases. **The full Windows CSVs have not yet been
uploaded**; do not cite, derive figures from, or merge them with
GitHub Linux CSV timings without their own metadata.

No measured results should ever be replaced by guessed values
for a paper figure; the figure renderer fails or skips clearly
when required inputs are missing. The newest five-criterion CSV
experiment is separate, records its own environment.json, and
should not be presented as multi-host predictive evidence.

## 7. Figures, source of truth and where they appear

All figures are regenerated with pinned GitHub `awesomefigures`,
its Okabe–Ito palette, and `af.latex_style` against the real
official Springer Nature manuscript. The paper uses exact-width
PGF-rendered vector PDFs and the Sphinx site uses matching SVG.

- `paper/figures/gcv_solver_by_order.pdf/svg`:
  six *native* GCV solver timings by difference order.
- `paper/figures/gcv_repeated_search.pdf/svg`:
  six-backend cold versus warm GCV factor reuse ratio.
- `paper/figures/criteria_with_mle_s_paths.pdf/svg`:
  five within-criterion normalized score shapes in S, including MLE.
- `paper/figures/criteria_with_mle_search_time.pdf/svg`:
  public selector runtime for matched lambda/native S/log lambda.

Underlying inputs are recorded CSV and environment metadata, not
values hard-coded into the plot script. The manuscript uses
`paper/sections/gcv_grid_reuse.tex` and
`paper/sections/selection_visuals.tex`; website page
`docs/mle_coordinate_figures.rst` links each browser SVG.
Current Jupyter research gallery contains the independent fit and
GCV benchmark notebooks, plus earlier theoretical MLE examples.

## 8. Exact reproduction commands (Windows PowerShell)

~~~powershell
git switch main
git pull --ff-only origin main
conda activate trendestimation
python -m pip install -e ".[dev,docs,plot]"
python -m pip install -r paper/requirements.txt

# Hosted quick reference can be regenerated locally under a NEW path:
python paper/benchmarks/selection_coordinate_mle.py --preset full --repeats 9 --output-dir paper/benchmarks/results/selection_coordinate_mle
python paper/benchmarks/grid_reuse_study.py --preset full --repeats 7

# Paper / website figures from the pinned reference CSVs:
python paper/figures/render_awesomefigures.py --benchmarks-only
python paper/build.py --pdf --package
$env:TRENDESTIMATION_DOCS_EXECUTION="off"
python -m sphinx -W --keep-going -b html docs build/site
~~~

Paper figures use source-compiled TeX and require pdflatex
(MiKTeX/TeX Live) on PATH. Web-only browsing of committed
SVGs does not require LaTeX.

For the user's existing full Windows results, **check git status before
switching or pulling** and use
`python scripts/publish_generated_outputs.py` (preview) followed by
`--publish` to create a safe results-only branch/PR. Never hard reset
or mix measured CSV files from different machines.

## 9. Open research questions / handoff to future agents

1. Obtain **actual Windows full-run CSVs**, provenance and independent
   seeds; pair and quantify uncertainty rather than repeating a
   single microbenchmark and declaring a universal winner.
2. Benchmark **true full CV, GCV, AICc, BIC and MLE** under alternative
   algebraic backends, not simply one GCV winner assumed for all.
3. Evaluate native-S versus lambda search at matched and independently
   sampled grids, reporting time *and* criterion attainment, not
   just overhead or selected lambda.
4. Evaluate high-order conditioning and floating-point sensitivity near
   S=1; λ=∞ is a limit and cannot be represented by a finite
   Cholesky matrix.
5. Keep conditional MLE distinct from not-yet-implemented joint
   (lambda,mu) MLE.
6. For forecast-oriented claims use chronological origin/horizon
   validation; ordinary LOOCV and in-sample GCV are not TSCV.
7. Regenerate vector plots on every source/CSV change, verify TeX
   fonts, website SVG legibility and the full Springer PDF/flat ZIP.
   Never publish old figures against new measurements.
8. Record experiment design, actual rows, decisions, outputs, tests
   and next steps in this file, and update `notes/README.md` for handoff.

**Primary scientific references** are in
`notes/cholesky_prior_art_cortes2017.md`,
`notes/criterion_coordinate_factorial.md`,
`paper/bibliografia.bib` and the manuscript. Existing PLS smoothing,
Whittaker–Henderson algorithms, and Gaussian likelihood are prior art.
The contribution being evaluated is a carefully validated numerical
comparison and interpretable reparameterization, not a new penalty.
