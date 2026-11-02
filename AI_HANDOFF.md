# AI_HANDOFF — latest

## Experiment005: sparse/iterative PLS, current branch

Branch: feature/experiment005-structured-solvers; PR #94.

Existing SVD/eigh/banded-Cholesky preserved; added banded_lu, sparse_lu
(SuperLU), optional sparse_cholesky (real CHOLMOD), and matrix-free PCG
with fft/dst/jacobi/none preconditioners. The new methods are fit-only.
Matrix A and RHS are built without a high-degree polynomial subtraction.

Review src/trendestimation/_structured_solvers.py, the integration in
src/trendestimation/solvers.py, tests/test_experiment005_structured_solvers.py
and paper/benchmarks/experiment005/run.py. Numerical correctness/parity,
normal-equation residuals, finite lambda, zero & infinity limits,
fixed/plug-in mu, convergence failures and factor-cache reuse are tested.

Do NOT claim fastest sparse Cholesky without separately installing and
timing optional SuiteSparse CHOLMOD. FFT/DST are approximate surrogate
preconditioners; convergence depends on conditioning and boundaries.

The next research step is to run the larger experiment005 preset on the
author's Windows workstation and publish the evidence to the repository,
then compare fit-only performance and full criterion selection separately.

Previous experimental timing data and the two CSDA manuscripts remain
unchanged. Maintain their provenance and do not alter recorded values.


## Experiment006: complete-criterion computational factorial — current research PR #95

The next sequential experiment lives under paper/benchmarks/experiment006/.
Draft branch: research/experiment006-full-computational-factorial; do not
merge while it is under numerical review. Existing Experiments001–005,
manuscripts, notebooks and results remain unchanged.

Core new mathematical algorithm: selected_inverse.py implements exact
banded-Cholesky Takahashi-style selected inversion O(n d^2), giving trace,
conditional EDF, exact fixed-mu LOOCV leverage and S(lambda) inversion
without dense eigendecomposition for d=1,...,6. Independent parity tests
validate across dense inverse and the public spectral scores.

run.py is the first integrated **three-method** full-criterion benchmark:
actual naive dense inverse, full SVD, and banded Cholesky plus selected
inverse. It times one/grid S x one/multiple independent series, and
direct-S versus S-to-lambda pretranslation. Seven n values up to 131072,
fixed mu=0/0.15, two observation amplitude scales and five criteria
are represented. The full n*d*mu*scale*grid*method*criterion tensor is
a *planned* factorial; only small test observations have been performed
by CI, not publication-scale Windows runs. plan.py records explicit
skips and missing complete-criterion implementations for the other
Experiment005 sparse/PCG fit-only methods.

The experiment must NEVER report that PCG fitting time is equivalent
to complete GCV/CV/MLE time. S=1 is lambda infinity (analytical
constrained limit); mu=data is conditional MLE only; RSS-BIC is
degenerate at S->0. Large nonzero-mu high-d polynomials need much
stronger numerical validation. Naive dense inverse is infeasible
for n=131072 (one 128-GiB float64 matrix).

Refer to paper/benchmarks/experiment006/README.md for PowerShell
worktree, factor levels, CLI and source retention. The user prefers
their workstation for heavy experiments and will commit/push raw
measurements on a separate branch. Do not automatically schedule
the full factorial on GitHub runners.

The next tasks are complete sparse/PCG statistical-criterion pathways,
a compiled selected-inverse kernel and adaptive high-precision S-grid
mapping, statistically fair paired CPU timings and analysis of
measured scaling versus theory. This is a draft research PR, not a
claim of final computational superiority.

## Experiment006 hybrid criterion extension (latest)

The experiment006 runner now includes six *explicitly named* complete
hybrid pipelines: banded_lu_banded_trace, sparse_lu_banded_trace,
sparse_cholesky_banded_trace, pcg_fft_banded_trace,
pcg_dst_banded_trace and pcg_jacobi_banded_trace. They add real
sparse/iterative fits PLUS an exact banded selected-inverse trace/
leverage/determinant diagnostic, with both components counted.
No hybrid is advertised as an intrinsic sparse-only exact CV implementation.
Pure Experiment005 methods still lack standalone criterion diagnostics.

The grid reuse cache is gated by estimated resident memory rather than an
arbitrary 1000-point limit; CHOLMOD remains optional and unavailable cases
are explicitly recorded. New parity tests test the resulting complete
criteria against independent SVD for d=1,2,3,6. The PR is draft #95.
The corrected Windows benchmark and complete timing tensor have NOT run.

## Experiment006 Windows runner operational handoff — 2026-11-02

The university Windows PC `PCAG103A-08` is NON-ADMIN. Its Conda installation
is `C:\Users\175199\AppData\Local\miniconda3`, and the **required**
environment is `trendestimation`, not the separate `trend-estimation`.
Do not use `actions/setup-python`, `pip install`, or `conda create`
on this machine. Use the already-tested workflow
`.github/workflows/experiment006-selfhosted-pilot.yml` with
`conda run --no-capture-output -n trendestimation python ...`,
Windows PowerShell (`shell: powershell`) and repository `src` on PYTHONPATH.

Failed attempts #41430441159 (missing pwsh) and #41430529868
(setup-python provisioning) did NOT measure solver performance.
The corrected workflow succeeded:
https://github.com/heri-espino/trendestimation/actions/runs/41437886131
No Python or package installation occurred. Existing numerical tests passed.

**Actual permanent results** are in
`results/experiment006-selfhosted-41437886131`, not only in ephemeral
runner output; additionally GitHub artifact ID 13136414474 captures
the raw files. The measured experiment source was commit
`05edb60c5e9540eecd0a9222dd144a6d1fbd703a`.

Pilot001: n=64, d=2, mu=0, low-amplitude GCV, grid M=100,
R=2 and 2 repetitions. 64/64 rows succeeded (4 backends).
Pilot002: n=128, d=6, mu=.15, high-amplitude ordinary CV,
grid M=100, R=2 and 2 repetitions. Only 40/64 rows succeeded:
24 rows marked `numerical_failed` (eight each for
banded_cholesky, sparse_lu_banded_trace and pcg_fft_banded_trace).
The high-order full-grid failures arise from KKT backward-error
checks near 1.18e-7–1.30e-7 for banded/sparse and PCG
relative-residual checks ~6.1e-9–8.9e-9. The full spectral SVD
returned 16/16 valid rows for this limited pilot.

The GitHub Actions job concluded successfully because it retained
and reported invalid numerical cells; this is **not** scientific
certification of all backends. Never count a partial high-order grid
as an acceptable timing winner. Before a larger timing factorial,
validate all d=6/high-S methods against the high-precision reference,
then decide numerical residual tolerances and which algorithms to
exclude or improve. Do not silently relax tolerances.

The first two-repetition pilot is insufficient to establish any
general fastest-method ranking or amortization exponent. Continue
only with bounded research slices and versioned results branches;
never merge other agents' work.

## Experiment006 verified high-order accuracy and guarded fallback (2026-11-02)

Numerical audit (non-admin Conda PCAG103A-08, Python stdlib Decimal,
85 digits, separate 55-digit convergence check):
https://github.com/heri-espino/trendestimation/actions/runs/41439239921
Permanent branch: results/experiment006-highd-41439239921.

28 cases/backend: n=128, d=5/6, mu=.15, 2 frozen seeds,
S=.75,.85,.90,.91,.95,.99,1. Shift-free SVD accurate 28/28
(relative forward error <=6.18e-9); primal banded Cholesky 16/28
(12 inaccurate, worst error 21.24); sparse SuperLU 22/28
(6 inaccurate, worst 6.86e-2); FFT PCG 14/28 accepted
(14 rejected by strict independent convergence check). No claim
that a small KKT residual guarantees forward accuracy.

The new explicit guarded_svd_cholesky policy selects actual full
shift-free SVD for d>=5 and banded Cholesky for d<=4, correctly
accounting for spectral setup/time. It is subject to dense
memory/runtime gates; it does NOT solve high-d at n=131072.
Tests/test_experiment006_highd_guard.py cross-checks independent
85-digit reference. Successful guarded runner pilot:
https://github.com/heri-espino/trendestimation/actions/runs/41439589986
results/experiment006-selfhosted-41439589986;
first slice 80/80 valid and second high-d slice 56/80
(16 new guarded rows all valid, 24 preexisting failures retained).

The original 24 failures remain scientifically relevant and
must not become falsely successful via looser tolerances. A robust
large-n high-d/very-high-S structured algorithm is still open.
The new evidence supports merging tested research scaffolding
as a *working experiment*, not asserting a universal computational
winner or completed full factorial.

## CSDA computational four-workload manuscript branch — 2026-11-02

Branch: paper/csda-four-workload-20261102; complementary to merged Experiment006 implementation PR #95 and its archived self-hosted runs. The user authorized merging the associated research PRs. Existing baseline paper,
its six AwesomeFigures vector figure families, archived 80,640-row
Windows timing results, and prior numerical companion are preserved.

The existing paper/csda-computational-costs/main.tex now includes:
- sections/structured_criteria.tex: exact banded selected inverse,
  conditional CV/GCV/BIC/AICc/ML computations, nonzero-mu RHS,
  nine honest end-to-end complete criterion pipelines.
- sections/experiment006_design.tex: four M×R workload configurations,
  n to 131072, d=1,...,6, fixed mu zero/nonzero, high/low magnitude,
  100/1000/10000/100000 S grids including exact S=1,
  matched direct-S/onetime-pretranslated-lambda policies.
- sections/experiment006_status.tex: historical measured evidence
  explicitly separated from the unrun large factorial and
  hypothesis testing protocol.
- BibTeX adds Erisman/Tinney (1975), selected inverse prior art.

The main.tex abstract reports only confirmed historical d=2/d=3
n=48 grid-reuse times; no new full-factorial results are claimed.
New paper CI: .github/workflows/csda-four-workloads-paper.yml.
GitHub-hosted LaTeX build copies original CAS class and references
pre-existing TeX-native AwesomeFigures assets without rerunning figures.
Outputs: main.pdf, publication hashes, archived GitHub Actions ZIP.

To extend results, retrieve real raw CSV and numerical status from
the Experiment006 results-only branch after a successful runner run.
Keep machine-specific timings and conditional performance conclusions
explicit. Confirm author order, coauthor consent, and citation metadata
before submission. The full factorial is NOT completed.


## Experiment007 — empirically locate backend switching surfaces for mu='data'

Research PR #97 (branch research/experiment007-data-mu-backend-frontier).
User correctly questioned the previous d-only guarded rule. No
production automatic backend selection is changed. Review
paper/benchmarks/experiment007/README.md and source under that folder.

The *primary* practical reference mean is mu='data',
mu_hat=mean(np.diff(y,n=d)), computed separately for every observed
series. Fixed mu=0 is retained ONLY as a controlled comparison;
no fixed arbitrary mu=.15 is used in this new experiment.
The mean of differences of known synthetic latent tau_true is an
oracle diagnostic, never passed to any solver.
A jointly optimized mu=mean(D tau_hat) is a DIFFERENT centered
penalty and requires independent theory and smoothness normalization.

The first successful Windows pilot on PCAG103A-08 (existing Conda
trendestimation, no installations) was:
https://github.com/heri-espino/trendestimation/actions/runs/41510249404
Results on branch results/experiment007-selfhosted-41510249404.
It produced 2304 fit-only timing rows and 12096 per-fit QA rows.
A script joined every method/time block to all required S and series
accuracy results; 1893/2304 timing rows were eligible for
PROVISIONAL descriptive comparison. Only 512 of 12096 QA records
used an independent 85-digit decimal reference, for selected
n<=128, high-d, high-S cells; remaining SVD proxy matches are
not certified forward accuracy.

First provisional mu='data' 7-S/3-series winners varied with n,
d and amplitude, contradicting any justified d-only switch:
d1-2 Cholesky across n=64/128/256; d3 switches among Cholesky,
SVD and sparse LU by n and scale; d4 among SVD, sparse LU and PCG;
d5-6 SVD often wins by being the only complete accurate method.
This is TWO-SEED exploratory evidence; e.g. a 1–3% PCG speed
advantage at n=256,d=4 is not a justified production choice.

The current runner workflow also has a 12-seed, three-repeat,
counterbalanced-method-order confirmation preset, with each
new run in its own results-only branch. Do not merge or set an
automatic default until this evidence and full criterion
requirements are reviewed. The five standard fixed-mu statistical
criterion formulae are not automatically the correct data-refitted
criteria for mu='data'.


## Experiment009 SVD vs banded Cholesky theory and empirical surfaces

Open PR #99 on research/experiment009-cost-crossover-surface.
Read paper/benchmarks/experiment009/README.md and source
crossover.py before modifying. Frozen Windows data:
data/experiment007_fit_pair.csv (12-seed fits; n64/128/256,
d1-6, mu=data/0, M1/7 and R1/3) and
data/experiment008_aicc_data_n{64,128,256,512}.csv
(complete AICc selection, mu=data, high amplitude, mapped
lambda, M1/100 and R1/2). Both are from immutable results
branches, provenance paths preserved per record.

First completed run:
https://github.com/heri-espino/trendestimation/actions/runs/41537222327.
Updated analytic M* and class-balance run:
https://github.com/heri-espino/trendestimation/actions/runs/41537747991.
Committed figures/CSV/calibration JSON on
results/experiment009-crossover-41537747991.
Fit-only NNLS trained n64/128, holds out n256:
61/61 of comparable predictions correct, but all 61 true
winners are Cholesky. AICc trained n64/128/256,
holds out n512: 8/8 correct, BUT all 8 winners
Cholesky (M1 only), and SVD M100 grid n512 was
not eligible. Thus NO successful empirical boundary
validation; training classification 137/142 fit,
46/60 AICc. Do NOT quote 100% holdout as evidence
of universal crossover. The model extrapolates M/n and
is constrained by poor numerical high-d Cholesky cases.
README and notes/experiment009_crossover_findings.md
give actual comparison tables and next experiments.

The derived theoretical conditional break-even grid size is
M*=(a n^3+b R n^2)/(u n d^2+v R n d-c_C R n^q),
when denominator positive and factors shared. q=1
for global scalar scores and q=2 for CV/leverage or
full fitted trend. Fit-only Cholesky WITHOUT reuse has
MR n d^2 factor cost; use the distinct equation.
Empirical calibration found some coefficients zero due
to underidentification—do not misread this as eliminating
the corresponding asymptotic theoretical work.

Proposed output: provide theoretical and empirical
multi-parameter surfaces with separate numerical
reliability/memory masks; no production switch yet.
