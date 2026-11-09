# AI_HANDOFF — latest

**Newest mathematical clarification (2026-11-09):**
The author intended the fixed-reference Gaussian restricted
likelihood for (z=Dy-mumathbf1) with covariance
(sigma_u^2(I+lambda DD^	op)).
Read [the complete proof and unknown-μ caveat](paper/ngsim-jerk-case-study/notes/GUERRERO_GAUSSIAN_REML_EQUIVALENCE.md).
The repo's existing criterion="mle" is **exactly the same
objective up to −log|DDᵀ|**; PLS MLE comparisons in
Experiments004/005 thus already used the intended
fixed-μ Gaussian variance-ratio estimation *on a 15-value
smoothness grid*. Do not rerun previous experiments solely
to replace this algebraic representation. Data-derived
μ in these experiments is held fixed when scoring lambda
and is **not mean-adjusted REML**. A correct additional
unknown-mean REML would require GLS estimation μ_hat(lambda)
and a reduced (n−d−1) residual dimension plus determinant
term; treat as separate future science. Guerrero 2007
provided the variance-ratio PLS estimator without a Gaussian
likelihood hypothesis. The independent PCAG103A-08
Experiment005 workflow previously marked queued has now
**completed successfully**; verify its archived manifests
before making detailed cross-platform comparisons.


**Newest verified Paper C simulations (2026-11-08):** [Experiment005 RUN_LEDGER](paper/ngsim-jerk-case-study/experiments/experiment005/RUN_LEDGER.md) and [GitHub-hosted success #42547883064](https://github.com/heri-espino/trendestimation/actions/runs/42547883064): 96 pilot + **1,296 disjoint confirmation trials** with analytic known jerk, complete clean/noisy per-trial x/v/a/j and all first-party outputs preserved in Git branch **results/paper-c-exp005-cloud-42547883064-a1**. Confirm: **12,960 valid GCV/profile-ML selections, 15,552 known-jerk fits, 89,424 future clean-position forecasts, 62,208 fit/reference crossings, zero invalid**. File inventory: 33 generated files / ~44.8MB. Pooled historical jerk RMSE: PLS profile-ML+global cubic OLS mean **2.918 m/s³** vs GCV spline **60.913**, SG **36.829**, PLS GCV zero **68.242**. Profile-ML PLS zero-mu local25 future RMSE **0.276/0.413/0.861 m** at 0.5/1/2s vs GCV spline **0.567/0.971/2.170 m**. Nonzero global OLS mu helps constant ±jerk, hurts sign reversal; raw sample mu is unstable. **All of these are synthetic DGP-conditional results**, not empirical physical jerk validation or population inference. Actual 200-episode NGSIM Experiment004 favored the spline. The separately configured PCAG103A-08 [Windows workflow #42547250403](https://github.com/heri-espino/trendestimation/actions/runs/42547250403) remained queued: **NO VM simulation completion is claimed**. Use [sync_cloud_results_to_vm.ps1](paper/ngsim-jerk-case-study/experiments/experiment005/sync_cloud_results_to_vm.ps1) to copy/verify the complete cloud archive on VM, clearly labeling it as imported (not rerun). Older notes below are historical and superseded by this record.


**Newest author decision, 2026-11-08:** Proceed with
**synthetic known-jerk simulations** after real-data
Experiment004. The previous instruction to use only real
data was specific to Experiment004, not a permanent ban.
[Experiment005](paper/ngsim-jerk-case-study/experiments/experiment005/README.md)
is now a predeclared 96-trial pilot followed by 1,296 disjoint
confirmation trials on PCAG103A-08.
Methods: `d=3` PLS GCV and profiled Gaussian `mle`,
mu zero/sample/cubic OLS global/tail25/true oracle,
two extrapolation rules; GCV cubic spline and Savitzky-Golay.
Primary known-truth endpoints: historical D3 jerk RMSE
(m/s^3) and clean-future-position forecast RMSE (m),
with full fixed-S mu fit/continuation 2x2 attribution.
Raw per-trial known/noisy trajectories, all selection/error
rows, plots, config, seeds, logs, and file inventory
persist at `%USERPROFILE%\Documents\TrendEstimation-PaperC\experiment005\run-<id>-a<attempt>`
and in a separate results-only Git archive branch.
**Important:** workflow creation is not proof of completed
simulation, or that its results favor PLS. Check source
version/manifest/CI. Synthetic oracle mu is not feasible
on real FHWA data. Preserve Experiment004 results on
the VM and its existing Git results branch, without
editing the older CAS manuscript or Springer work.


**Paper C expanded real NGSIM run COMPLETE (2026-11-08):**
[Experiment004 run ledger](paper/ngsim-jerk-case-study/experiments/experiment004/RUN_LEDGER.md)
and [successful PCAG103A-08 #42538556206](https://github.com/heri-espino/trendestimation/actions/runs/42538556206)
document the 100 US-101 plus 100 I-80 episodes, downloaded
400,000 raw source CSV rows in 20 paginated pages, 6,600/6,600
valid forecast records, 800 model selections, and 38 VM files
with path/SHA inventory. The permanent VM root is
`C:\Users\175199\Documents\TrendEstimation-PaperC\experiment004\run-42538556206-a1`,
and the compact complete rows + file inventory were independently
archived in Git branch `results/paper-c-exp004-pc08-42538556206-a1`.
The revised existing paper compiled on the VM. **Result: tuned
GCV cubic splines with quadratic continuation outperform the
tested PLS methods in pooled future-position RMSE at all
three horizons**; profile marginal ML is only modestly different
from GCV. This reverses the smaller earlier pilot's advantage.
There are only **five coarse recording-session proxies** across
200 convenience-sampled episodes, reused numeric Vehicle_IDs
and no ground-truth physical jerk; bootstrap intervals are
exploratory, not population-level inference. No prior Paper C
experiments, source data or other paper outputs were overwritten.
Review [stacked PR #122](https://github.com/heri-espino/trendestimation/pull/122)
before merging anything. The older “in progress” handoff
below is a historical entry and is superseded by this success.


**Current Paper C run (2026-11-08):** The author selected only real
NGSIM data, not known-jerk simulations, and asked to preserve
every generated directory/data file/results file on the university
Windows VM (PCAG103A-08). A new bounded, page-hashed US-101/I-80
episode downloader and GCV versus Gaussian profiled marginal MLE
evaluation are in
[experiment004](paper/ngsim-jerk-case-study/experiments/experiment004/README.md).
GCV/profile MLE x zero/data-derived third-difference mean x last3/
local25 forecast compares to GCV spline, Savitzky--Golay and local
quadratic, always using training-only choices and the same recorded
future position targets. Paired site-stratified episode bootstrap is
**exploratory** and not a physical jerk accuracy measure.
The job is launched from a new branch layered on Paper C PR #121;
do not merge unrelated PRs. Source FHWA raw CSVs, per-episode losses,
run logs, compiled PDF and full SHA-256 file inventory are retained
in a non-overwriting persistent Documents/TrendEstimation-PaperC/
experiment004/run-<id>-a<attempt> directory on PCAG103A-08.
The small full loss tables, data provenance and directory inventory
are also pushed to a separate GitHub results branch (the VM's raw
page bytes are NOT in Git). **Check the workflow before claiming
numerical results.** Existing source manifest and studies are unchanged.


**Paper C extrapolation/jerk-reference continuation (2026-11-05):**
Read [the new research handoff](paper/ngsim-jerk-case-study/notes/EXTRAPOLATION_RESEARCH_HANDOFF.md),
[exact fixed-S attribution](paper/ngsim-jerk-case-study/notes/EXTRAPOLATION_DECOMPOSITION.md),
[mu-policy catalog](paper/ngsim-jerk-case-study/notes/MU_POLICY_CATALOG.md),
[predeclared follow-up experiment](paper/ngsim-jerk-case-study/notes/EXTRAPOLATION_ABLATION_PLAN.md),
and [Biessy WH-extrapolation annotation](paper/ngsim-jerk-case-study/notes/papers/biessy_2026_extrapolation.md).
The user proposes that the specific d=3, nonzero-mu PLS trend
**plus a separate local-polynomial forecast** could be distinctive;
this remains an unverified **applied novelty hypothesis**, not a
claim of first PLS extrapolation (Biessy already extrapolated WH).
An exact algebraic 2x2 counterfactual separates the impact of mu
on the **historical fit** from its impact on the **cubic continuation**,
at the *same* smoothing parameter. The raw training mean of third
differences telescopes to boundary second differences; proposed
replacement mu policies are NOT implemented. This update contains
research notes, handoffs and **one deterministic algebra regression test**;
no Paper C empirical data, simulations, benchmarks, forecasts,
algorithm changes or manuscript changes.
Next agent: run a deterministic algebraic test and planned Paper C
experiment001 on a separate branch with reproducible output. Do not
merge or conflate with Springer Experiment011.


**Paper C literature notes (2026-11-05):** A source-grounded Markdown
literature review and annotations now live in
[paper/ngsim-jerk-case-study/notes/](paper/ngsim-jerk-case-study/notes/README.md),
with source inventory, individual paper notes, mathematical analysis,
manuscript outline and a future sequential experiment plan. The earlier
[NOVELTY_AUDIT.md](paper/ngsim-jerk-case-study/NOVELTY_AUDIT.md) is
preserved. The strongest close prior study is Fan et al. (2024);
Guerrero's nonzero-mean PLS formulation is established. A new essential
observation is that `mean(D3*y)` telescopes to endpoint second differences.
The six candidate BibTeX records have been staged in Paper C's references.
**No new simulations, NGSIM data downloads, results, figures or LaTeX
manuscript edits were performed.** The five-vehicle pilot and publication
ownership remain unchanged. Next: coauthor-approved literature incorporation,
a known-truth jerk simulation, and independent-vehicle evaluation.


**Parallel manuscript edit, 2026-11-04:** Draft [PR #112](https://github.com/heri-espino/trendestimation/pull/112) improves prose in the four primary papers and the direct-spectral-weights draft, corrects the CSDA B fixed-mean CV leverage diagonal and the CSDA A nonzero-mean polynomial endpoint, and adds a deterministic test plus [paper/EDITORIAL_LITERATURE_AUDIT.md](paper/EDITORIAL_LITERATURE_AUDIT.md). This is not a claim of exhaustive publisher-PDF verification. It does not produce Windows Experiment011 timing measurements, change scientific manuscript ownership or authorize submission/merge. Read the PR and source-to-claim ledger before revising any affected section.

**Integration status (2026-11-04):** the author authorized merging the open research PRs.
Read [cleanup audit](paper/REPOSITORY_CLEANUP.md) and the current session handoff.
Use `origin/main` after integration; older “open/unmerged” statements below
are historical. Experiment011 remains 29 cases; Windows measurements are pending.


**Session continuation (2026-11-04): read [SESSION_HANDOFF.md](paper/SESSION_HANDOFF.md) first.** It records the four-paper split, approved 29-case scope, current PRs, Windows missing-file diagnosis, exact results-worktree commands, and pending measurements. The next author action is the small 16-series/16-worker GCV pilot; the Windows campaign is not yet measured.

## Current author decision — focused Experiment011 (November 4, 2026)

Keep the original 21-case Experiment011 protocol and add only targeted
CV/GCV comparisons at **d=4** for **n=256, 1024, 2048, 4096**:
two pilot cases at n=256 and six confirm-stage cases at larger n,
**29 cases in total**. The n1024 confirm cells explicitly permit
a 750-million-work-unit cap so SVD can be compared with banded Cholesky
on the full M=100, R=3 grid; n2048/4096 use the feasible banded
backend only. All larger cases require the existing opt-in
`--allow-confirm`. No older run, criterion, or historical result
is overwritten.

An **optional throughput-only** `campaign.py parallel-series`
mode runs independent small series (n<=256, M<=1000) in spawned
processes, up to 32 workers, each with one BLAS thread. It writes
`runs_parallel/` with per-series checkpoints and real wall times.
It deliberately **does not replace** the serial shared-cache
single/multiple-series latency benchmark. The author's 32 logical
processors are a capacity ceiling, not proof that 32 workers
will run faster than 8 or 16. The old 252,000-cell factorial is
retained only as an archival index, **not** a new study mandate.


The user has now explicitly approved the focused Experiment011 design, extended to d=4 and n=1024/2048/4096 (29 cases total). The earlier 252,000-cell Experiment008 full factorial remains archived provenance, NOT the authorized execution campaign. To preserve the prior validated design instead of multiplying ad-hoc scripts, `paper/benchmarks/experiment011/full_plan.py` invokes the Experiment008 manifest generator, validates all n=64/128/256/512/1024/16384/131072, d=1..6, mu=0/data/0.15, high/low amplitude, CV/GCV/BIC/AICc/MLE, ten complete pipelines, direct_s/mapped_lambda, and four workloads with M=100/1000/10000/100000 for grid workloads, deduplicating single-S cells. This is 252,000 PLANNED cells, not a 252,000-run result. The explicit 2GiB/compute-budget preflight marks infeasible operations. Real timing samples will be archived per independent block/repeat/host and paired to the naive baseline where feasible. No RMSE analysis. Caveat: current direct_s versus mapped_lambda is *on-demand versus cached S→lambda mapping of the SAME candidate set*, not two independent continuous minimizers.




## ACTIVE: Springer implementation article and Experiment011 (2026-11-03)

The user selected a **four-manuscript** structure:
(1) CSDA spectral numerical reliability at
`paper/csda-spectral-smoothness/`;
(2) CSDA theoretical computational costs at
`paper/csda-computational-costs/` (open PR #109);
(3) Springer *Computational Statistics*, measured
complete-criterion software implementation and runtime,
canonical `paper/main.tex` (main's old 36-page draft already
compiled);
(4) separate real FHWA NGSIM d=3/jerk application at
`paper/ngsim-jerk-case-study/`.
Also preserve the historical distinct SN Computer
Science `paper/computational-statistics-submission/` draft.

NEW branch `paper/springer-implementation-experiment011`
introduces `paper/PUBLICATION_MAP.md`,
`paper/AGENTS.md`, `paper/SPRINGER_AGENT_BRIEF.md`,
`paper/SPRINGER_READINESS.md`, and
`paper/SPRINGER_MANUSCRIPT_PLAN.md`.
Root/paper agent handoffs must route all future agents
there; do not duplicate CSDA B theory in Springer.

Experiment011 under `paper/benchmarks/experiment011/`:
29 predeclared case configurations in `cases.json`
(2 smoke, 15 pilot, 12 confirm), `campaign.py`
one-block runner (no implicit heavy run; confirm must
pass `--allow-confirm`), `verify.py` independent
status and parity validator, tests, source-controlled
plan, CI smoke workflow, Windows reproduction README,
and frozen `reference/experiment010_matched_n64_d1_bic.csv`
(48 real one-worker BIC rows, not new measurements).
It invokes `paper/benchmarks/experiment006/run.py`
from main instead of copying open Experiment010 research
branches (#100/101/103/104/105). Rotating method order
across 3 blocks supports a later paired pilot; an isolated
single worker measures latency, not 8-way task throughput.

CI hosted smoke run: https://github.com/heri-espino/trendestimation/actions/runs/41767817861
SUCCESS, 24/24 actual rows `ok`, 16 float64
paired comparisons, 0 reported parity issues.
Source SHA for that hosted run:
`c52291e77b6375c77e4aecfef55e2dd53362b0b7`.
The original 21-case plan declared 187 eligible and 5 budget
exceeded method/scenario cells (historical, not measurements or current
29-case counts). Generate the current checksum-versioned plan when needed.
Results, plan and environment committed to the
source branch by CI. **No Windows multi-criterion
pilot has yet been measured.** The Windows command and
result-branch workflow are in Experiment011 README.
Any numerical winner or confidence claim requires
independent multi-block Windows data and stronger
numerical checks where appropriate.

The existing Springer main-branch Experiment010
table mixes 8-worker SVD/naive with 1-worker CHOLMOD
archived runs; it must not be used for an
unconfounded solver rank. The independent matched
one-worker BIC source is
`results/experiment010-uncapped-PCAG103A-08-20261103T222938857Z-shard0-offset20`;
it has two repeats, one n/d/criterion setting only.
Current Springer's new study must compare full
CV and scalar GCV on matched candidate grids
and identical machine conditions, with all
resource skips and hybrid diagnostics accounted for.

DO NEXT: review preparation PR; run the two
smoke cases/targeted pilot on idle university Windows
VM (not whole factorial), store all raw output
on a new `results/experiment011-PCAG103A08-001`
branch, update `paper/SPRINGER_READINESS.md`,
independently audit, THEN write results-driven
Springer figures and revise `paper/main.tex`.
Do not merge without user authorization.

## Current Paper B revision — theory, exact CV and real implementation examples (2026-11-03)

PR #109 on branch `paper/csda-computational-theory` now includes
a compact exact-backend Table 2 and separate hybrid Table 3,
explicit SVD-versus-Cholesky regime guidance for scalar
GCV/AICc/BIC/ML versus exact CV, and four pinned
AwesomeFigures CAS-ready plots. Source script is
`paper/csda-computational-costs/render_theory_figures.py`.
Analytic work landscapes are illustrative arithmetic
units with assumed unit coefficients, **not measured
speed ranks**. Actual frozen one-worker/one-BLAS-thread
BIC timings come from 48 Experiment010 raw rows
copied verbatim to the paper's `data/` directory;
original archive timestamp 20261103T222938857Z
from source SHA f16f2bab6cfa37c6423c7f2d4554208efa9f683a.
No repeated large experiment.

The jerk illustration is from existing separate third
manuscript `paper/ngsim-jerk-case-study`, using real
FHWA NGSIM US-101 vehicle positions (CC BY-SA 3.0),
track 1 origin 185, 80 training positions, 20
chronological held-out positions, d=3, GCV S=.4 and
`mu='data'` measured only on training. The forecast is
an explicitly separate local polynomial continuation,
not intrinsic PLS or true jerk measurement.

The CSDA theory workflow installs pinned AwesomeFigures,
renders PDF/PGF/SVG from the exact CAS LaTeX template,
checks frozen numerical provenance, compiles the PDF and
archives all output and hashes on the PR branch. Before
editing read `paper/csda-computational-costs/THEORY_HANDOFF.md`.
Never merge PR #109 without authorization.


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


## Experiment008: full-criterion computational timing tensor

Research PR #98, branch research/experiment008-full-factorial-timing.
The user explicitly wants all requested times (no RMSE), repeating
on PCAG103A-08 and preserving raw observations in GitHub. All
Cartesian cells are enumerated with resource eligibility in
paper/benchmarks/experiment008/run_batches.py, saved as a compressed
long-form full_factorial_plan.csv.gz. Actual measured times are written
only to per-slice raw_times.csv and their summary and paired naive
speedups; don't mistake planned/skipped rows for observed timings.

Actions run #41526378012 launched pilot and broad bounded batches;
large-n action #41527345441 covers n=16384/131072, d=1/6
with resource gates. The existing university runner uses
C:\Users\175199\AppData\Local\miniconda3\envs\trendestimation,
nonadmin, PowerShell 5.1 and no dependency installations.

All four workloads, exact S=1, full CV/GCV/BIC/AICc/MLE and
direct-S versus mapped-lambda coordinate policies are retained.
Actual mu='data' is each observed series' mean d-th difference.
For the fixed-mu criteria, opt-in conditional data-derived mean
is a CONDITIONAL PLUG-IN score, NOT a fully refitted-mean CV.
A fixed nonzero mu=.15 is retained solely as a controlled
reference case. The naive explicit-inverse method is baseline
only where feasible. Record every resource skip, fail and actual
measurement, and archive each workflow run under results/experiment008-*.
The entire 100000-grid x n131072 naive-inversion experiment is
physically infeasible and must not be falsely represented as completed.


## Experiment008 measured data (completed-hosted batches)

The full factorial design is **252000 planned cells**, but only
actual raw CSV rows with status=ok are timing observations.
Completed and archived measurements as of this handoff:

- results/experiment008-hosted-41528426191: 392 valid rows;
  initial CLI forwarding bug excluded other mu=data attempts.
- results/experiment008-hosted-41529170696: 632 valid rows,
  mu=data conditional flag correctly forwarded, no execution errors.
- results/experiment008-hosted-broad-41529218986: 2214 valid rows
  across 42 completed n,d slices, 8 timeouts, 2374 unrun slices.
- results/experiment008-naive-41530425009: 1008 valid rows;
  168 explicit-inverse GRID observations, all 5 criteria, mu0/data.

4246 actual valid timing records in 4 independent hosted batches
with different VMs; DO NOT pool hardware timing scales blindly.
See notes/experiment008_measured_computational_times.md for
sample measured means and theory caveats, source links and
exact counts. Run-level dataset includes environment.json,
paired_speedups.csv, batch manifest and full planned tensor status.

The Windows large-series and Windows bounded batch runs were also
launched. Only count them after Github pushes their raw data to
results/experiment008-* branches; do not invent large-n performance.
The original unbounded process was canceled; a corrected per-slice
45-second timeout and explicit slice statuses were implemented.

Research PR #98 has complete source + tests; no production solver
auto-selection default change, no RMSE optimization.


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


### Springer paper final empirical table and compilation (2026-11-03)

The user asked for final main paper/main.tex, real empirical tables,
paper PR merge and GitHub Actions PDF compilation. The dedicated
paper/computational-statistics-final-evidence branch adds
paper/sections/experiment010_three_backend.tex and 48 genuine timing
rows copied from immutable results branches:
results/experiment010-uncapped-PCAG103A-08-20261103T165925192Z-shard0-offset20
(SVD and naive) and
results/experiment010-uncapped-PCAG103A-08-20261103T193236486Z-shard0-offset26
(sparse CHOLMOD). All three have 16 valid rows. Compared with SVD,
maximum relative selected-BIC score differences were 2.321e-12
for naive and 4.463e-13 for CHOLMOD. Numerical times are
DESCRIPTIVE because source parallel worker counts differ (8 vs 1).
The check_table.py script validates source metadata and all recorded
medians. The computational-statistics-paper.yml workflow rebuilds the
Springer PDF and uploads artifacts; on the dedicated paper branch it
also commits the PDF and submission ZIP. Do not automatically merge
the separate nested Experiment010 research stack with this paper PR.

### CHOLMOD 0.5 code fix for main (2026-11-03)

Standalone fix/scikit-sparse-v05-main cherry-picks only the library
CSC-array CHOLMOD 0.5 adapter and the two mocked compatibility tests
from the already verified Experiment010 research PR #106. User's real
Windows CHOLMOD fit agreed with banded Cholesky to maximum error
1.2948756650255078e-13, and 110 targeted tests passed. The mainline
source fix remains independent from the nested Experiment010 runner
PR stack and from the Springer paper manuscript PR. Full handoff is in
notes/scikit_sparse_v05_windows.md.


### Paper B scope decision and new archived three-method run (2026-11-03)

The user chose to focus on a theoretical Paper B at
paper/csda-computational-costs/, with a distinct future Springer
implementation/real-runtime article. Branch
paper/csda-computational-theory introduces the formal full-criterion
T_A(n,d,M,R,C;epsilon,theta) model, exact banded Gaussian
likelihood identity, spectral and selected-inverse cost proofs,
d=1 cosine spectrum, conditional crossover proposition, and
a small deterministic regression checker. The new CSDA main.tex
omits the existing empirical timing/result/experimental-plan
sections (preserved unchanged in Git), and the new CSDA theory
GitHub workflow compiles exact Elsevier CAS without benchmarks.
Consult paper/csda-computational-costs/THEORY_HANDOFF.md.

A new matched serial Experiment010 three-method run was completed
and pushed to results/experiment010-uncapped-PCAG103A-08-20261103T222938857Z-shard0-offset20,
source f16f2bab6cfa37c6423c7f2d4554208efa9f683a. It has
three completed methods (SVD, naive, sparse-Cholesky+banded
diagnostics), one worker, one BLAS thread, n64/d1/BIC
mu=mean(Dy), 100000 candidate grid, 2 repeats, 48 valid
timing rows and matched score-parity records. Keep this
experimental archive unchanged, label as a single-case
runtime check only, and reuse it for the Springer methods paper.

## Historical Experiment010 runner handoff (not the active Experiment011 schedule)

## Experiment010 proposed cross-backend research after merged #98/#99

As explicitly requested by the user, PR #98 and PR #99 have been merged
into main. New design-only research branch:
research/experiment010-multibackend-frontier-design.
Primary protocol: paper/benchmarks/experiment010/README.md.

Scientific objective: predict and empirically validate the fastest
*complete* PLS criterion pipeline for each n,d,M,R,criterion,mu-policy,
S-grid,cache/hardware regime, while excluding numerically inaccurate,
unavailable and memory-infeasible candidates. Cross mu=0 versus
mu='data'=mean(D_d y) per series versus fixed mu=c (starting with
c=0.15), keeping conditional plug-in CV/GCV/AICc/BIC/MLE semantics
honest. Include all existing ten Experiment006/008 method names rather
than only SVD/Cholesky; guarded is a derived policy, hybrids charge their
banded diagnostics, CHOLMOD is never silently substituted. Compare
native S selection with a *single pretranslated lambda grid of exactly
those S candidates*, shared across criteria/series where appropriate.
S=1 is an exact infinite-penalty constrained fit. Include translation
cost and cache memory; no blanket claim that pretranslation always wins.

The new empirical claim to test is a calibrated *theoretical* minimum
among independently numerically certified and computationally feasible
methods, plus fallback to the next candidate on unexpected resource or
accuracy failure. Cost models, one-class boundary holdout limitations,
paired measured regret versus an observed oracle, and invalid/missing
statuses must be documented. No new numerical runs, production selector,
or manuscript timing claims were performed in this protocol branch.

Follow repository-first experiment-numbering and archive every result
with source/environment provenance. University PCAG103A-08 uses the
existing non-admin Conda environment trendestimation; no reinstall.


### Experiment010 runnable all-method work and first Windows execution (2026-11-03)

PR #100 now contains paper/benchmarks/experiment010/run_batches.py,
tests/test_experiment010_runner.py, the full-factorial manifest and
bounded checkpointed experimental batches. Existing Experiment006 exposes
an optional --seed CLI for deterministic paired repetitions.
The university Windows workflow was launched on the user's own
PCAG103A-08 and passed local numerical prerequisites:
https://github.com/heri-espino/trendestimation/actions/runs/41586066141
Its smoke/pilot jobs archive raw timing CSVs, machine environment, exact
failure statuses, and score-parity outputs on immutable per-run branches.
DO NOT claim a finished 50,400-case execution until actual outputs prove
it; run the remaining shards with --start-attempt cursors. A score-parity
check is NOT a high-precision numerical forward-error certificate.

The general PR CI initially failed only for a lint-unused import in
tests/test_experiment010_runner.py; fixed in the next commit. The
Windows workflow push trigger is deliberately gated to an explicit
REQUEST_RUN.md path to prevent any subsequent code/doc fix from
restarting costly university-VM measurements. The existing active
run is unaffected. To rerun the workload later, explicitly update
that request file or use a supported workflow_dispatch after merging.
No new numerical dispatcher or all-backend timing conclusion is yet
verified, and this draft PR must not be merged without approval.


### Experiment010 first measured outcomes, bug diagnosis and remediation

Actions #41586066141 completed both jobs successfully on PCAG103A-08.
Source SHA fc76c8c9d5366870e665b0897137da71e00f0dd7.
Smoke result branch results/experiment010-41586066141-a1-smoke:
30 completed method-cases, 420 valid timing rows, 420 spectral selected-score
parity successes (no independent high-precision forward certificate).
Pilot branch results/experiment010-41586066141-a1-pilot:
60 of 1800 planned method-case attempts (next_attempt_offset=60),
720 valid raw timing rows, 616 score parity, 104 disagreements, 180 partial.
All ten method *policies* attempted; CHOLMOD optional backend not installed.
The run is NOT the complete 50,400-case factorial.

Diagnosis: 100 discrepancies at n64,d5,mu=data,MLE largely reflect a
normalization omission in the finite-lambda banded/hybrid/naive MLE
benchmarks; exactly logdet(D D.T)=66.32448169 for n64,d5 was omitted,
while spectral MLE and S=1 use the normalized score. We fixed the
experimental scoring functions using an analytic log-gamma determinant
formula in paper/benchmarks/experiment006/selected_inverse.py and the
naive benchmark, with new tests/test_experiment010_mle_normalization.py.
4 discrepancies at n64,d6,mu=0.15,CV remain for independent numerical
analysis. Raw original results are permanently preserved and NOT
retroactively repaired. A fresh corrected run is required and must
be archived independently. See
notes/experiment010_mle_normalization_audit.md and
paper/benchmarks/experiment010/RESULTS_INDEX.md.


### Experiment010 corrected rerun and extended pilot (2026-11-03)

The MLE normalization fix was validated in GitHub Actions
#41587467639 (smoke and pilot both successful; all 4 CI checks pass).
Corrected raw archives are on
results/experiment010-41587467639-a1-smoke and
results/experiment010-41587467639-a1-pilot.
Corrected pilot: 60 method-case executions, 720 actual valid timing
rows, 704 spectral selected-score parity-only matches, 16 mismatches
(ALL naive inverse: 12 n64d5 mu=data MLE, 4 n64d6 mu=0.15 CV),
180 invalid/partial rows. Old pilot #41586066141 had 104 mismatches;
do not pool old unnormalized and new corrected MLE score values.
In progress: continuation run #41587723422 with bounded
offset windows 60,120,180,240 and immutable result branches.
Refer to paper/benchmarks/experiment010/RESULTS_INDEX.md.


### Experiment010 pilot through cursor300 and targeted n256/n512

All four windows of Actions #41587723422 passed on the
university Windows VM; offsets 60,120,180,240 each
finished 60 method-case attempts with valid rows
680,840,840,840 (total 3,200). All 3,200
selected-score parity-only audits passed; remaining
recorded statuses were invalid/partial. Together with
corrected first pilot, 300 of 1,800 pilot method-case
attempts have been run and 3,920 successful timing
records preserved. Corrected smoke adds 420 records.
Result branches are
results/experiment010-41587723422-a1-pilot-offset60,
...offset120, ...offset180, ...offset240.
All full runs are immutable and traceable via source SHA.

The next targeted balanced n256/n512 run is
Actions #41642508020 with two nonoverlapping
frontier offsets0/60, 120 scheduled method-case
attempts. Examine results/experiment010-*frontier*
before making numerical conclusions. All 3 mu
policies crossed for (n,d,criterion) blocks
(256,1,GCV),(256,5,MLE),(512,2,AICc),(512,6,CV).
This is not a 50,400-combination exhaustive sweep.
Independent high-precision forward certification,
calibrated cost-model regression, and held-out oracle
regret are still future work; never silently
conflate criterion parity with numerical validity.


### Actual n256 higher-n empirical evidence

Actions #41642508020 first offset0 finished successfully,
archive results/experiment010-41642508020-a1-frontier-offset0.
60 complete method-case attempts, 666 valid raw timing
rows, 664 criterion parity-only matches, 2 disagreements
(naive inverse n256d5 mu=data MLE), 222 failed/partial.
Three-reference-mean paired n256d1 GCV comparisons:
one S cold banded Cholesky approximately 8ms vs
SVD 13ms, but M100 grid Cholesky approximately
60ms vs SVD approximately 25ms; consistent
workload-specific crossover for all mu=0/data/0.15.
Two repeats only. n256d5 MLE: Cholesky single-S
recorded status ok but 100-S did not have valid full
repeats; SVD/guard did. Numerical accuracy must be
independently validated before calling a fast solver
admissible, especially at d5. The n512 second block
offset60 is independently archived and must be read
before any claims. See RESULTS_INDEX.md.


### Experiment010 full grid continuation (2026-11-03)

The independent research/experiment010-comprehensive-grid branch
implements full plan-only output and safe sharded actual runs.
The immutable complete plan at
results/experiment010-41647428485-a1-comprehensive-plan
contains 5040 cases, 50400 method-case attempts and
403200 method/workload/coordinate planning records:
264240 conservatively eligible, 106320 work-budget-exceeded,
26880 dense-memory-infeasible, 5760 naive-runtime-infeasible.
These are not measured timings. The first actual measurement
workflow is https://github.com/heri-espino/trendestimation/actions/runs/41647428485;
check each shard's results branch before claiming success.
Two repeated timings, R=2 for multiple-series mode, fixed
80M work-unit cap, 2 GiB dense-memory cap and 25-second
per-method timeout. Continuation offset comes ONLY from
a prior batch_summary.json for the same shard index/count.
See paper/benchmarks/experiment010/COMPREHENSIVE_GRID.md.
Paper scope limited to independent numerical correctness,
actual all-ten-method end-to-end timing and failure rates.
No added cost-oracle/fallback policy research per user direction.


### Experiment010 uncapped local rerun / source handoff

User rejected the 25-second artificially censored timings and
requested uncapped execution manually on university Windows VM.
See paper/benchmarks/experiment010/UNCAPPED_LOCAL.md, source
research/experiment010-uncapped-checkpointed and draft PR #103.
Optional `--no-time-limit` in Experiment010 removes outer method
and batch wall-clock thresholds and sets estimated max_work=inf.
Experiment006 `--allow-unbounded-runtime` permits physically
feasible methods to run without guessed n-only runtime exclusions.
The original experiment result branches and PR #101 are preserved.
Physical dense RAM guard remains. Experiment006 saves atomic
raw_times.csv after each completed row, outer controller streams
method stdout/stderr to logs, PowerShell launcher archives each
batch on a unique `results/experiment010-uncapped-*` Git branch
and prints cursor. No uncapped measurement has been verified or
claimed merely because the source was published; the user will
run it on PCAG103A-08 and can supply the GitHub result branch.


### Experiment010 parallel local VM revision — 2026-11-03

The user showed actual sequential n64 d1 AICc high M=100000
subprocess durations: naive_inverse 139.45s, spectral_svd 88.31s,
banded_cholesky 220.56s, guarded_svd_cholesky 220.67s,
banded_lu_banded_trace 244.08s. These are self-reported VM
subprocess durations, **not** numerical accuracy certification.
The user requested acceleration with 32 logical processors.
Branch research/experiment010-parallel-local, draft PR #104
stacked on #103, implements 8-worker process-level parallelism
(one BLAS thread per process) with adjustable count up to 32,
explicit aggregate dense-memory reservation, disjoint raw result
paths, streaming errors and checkpointed central ledger. Read
paper/benchmarks/experiment010/PARALLEL_LOCAL.md for exact
safe PowerShell commands; do not overlap the still-running
serial shard0 offset10 attempt IDs. No parallel run should be
claimed completed without its actual GitHub results branch.
Parallel timing is throughput under load, not comparable to
isolation-based timing without a controlled comparison.


### Windows WinError 5: preserved uncapped offset10 results / fix

The user's VM sequential uncapped batch of 10 method-case attempts
on shard0 starting at offset10 finished all ten subprocesses, but
`archive_ledger()` failed on the final `Path.replace` with
Windows `PermissionError: [WinError 5]`. The launcher archived
all the raw results, `method_attempts.csv`,
`method_attempts.tmp`, environment, logs, and outcomes.json:
results/experiment010-uncapped-PCAG103A-08-20261103T155726693Z-shard0-offset10.
Both ledgers contain 10 completed_with_csv subprocess statuses;
9 have 16 valid timing rows each; sparse Cholesky has 0.
No batch_summary.json exists because of the final checkpoint
exception; next shard0 cursor is nevertheless **20**, not 10.
The correction in PR #104 adds Windows atomic-replace retries,
preserves an explicit versioned fallback CSV, and tests both
transient and persistent locks. Parallel summary points to the
actual checkpoint file. Do not confuse operating-system access
errors with numerical failure, do not re-execute archived attempts,
and do not infer high-precision accuracy from status=ok.


### Experiment010 focused large three-method decision (2026-11-03)

Following the successful parallel uncapped batch on
results/experiment010-uncapped-PCAG103A-08-20261103T165925192Z-shard0-offset20
(n64,d1,mu=data, high amplitude,BIC,M100000; 8 workers,
1109.304s; 144 valid selected-score parity rows, 8
`setup_failed_ImportError` CHOLMOD rows), the user explicitly
chose to keep *only* naive_inverse, spectral_svd and
sparse_cholesky_banded_trace for the larger grid.
New independent research/experiment010-focused-three branch
implements explicit selected methods while preserving all original
10 method slots in the shard cursor, and marks the seven omitted
methods as `method_not_selected` in the ledger/manifest.
Sksparse/CHOLMOD is missing on the user's Windows Conda VM;
new code tests the optional import once and records
`dependency_unavailable` rather than repeatedly launching
failed processes. This leaves two operational selected solvers
unless the dependency is installed; do not claim a valid three-way
numerical comparison. Dense memory gates remain. Shard0 cursor
now **30** for future work. Read
paper/benchmarks/experiment010/FOCUSED_THREE.md and do not
merge active research PRs without approval.


### Experiment010 optional scikit-sparse 0.5 API migration

The user's Conda Windows VM now imports `sksparse.cholmod`,
but the old verification call `cholesky(A)(b)` failed with a
`tuple object is not callable` exception: scikit-sparse 0.5
changed to `cho_factor(A).solve(b)` and CSC sparse arrays.
Branch `research/experiment010-cholmod-v05-compat` introduces
explicit `csc_array` conversion in the new CHOLMOD adapter,
keeps 0.4 `cholesky(...).solve_A` compatibility and mock-based
regression tests. Experiment010 optional preflight now exercises
an actual small CHOLMOD PLS fit and compares to banded Cholesky
rather than treating an import as proof. Read FOCUSED_THREE.md
for commands. The user's real VM must pass the tests before a
new sparse-only backfill; prior results branches remain immutable.


### CHOLMOD verified on Windows VM — November 3, 2026

On the Windows Conda `trendestimation` environment, the user ran
`tests/test_experiment005_structured_solvers.py` and
`tests/test_experiment010_parallel.py`: **110 passed in 3.15s**.
They also compared the *real installed* `PreparedPLSSolver`
sparse-Cholesky fit versus banded Cholesky with
`n=64,d=2,lambda=2,mu=0.15,seed=42`: maximum absolute
difference **1.2948756650255078e-13**, `PASS: True`.
This verifies the sparse fitting backend for one case, not the
full criterion pipeline or accuracy over all n,d,lambda.
Seven GitHub CI checks on compatibility commit `ab3a427` also
passed. See `paper/benchmarks/experiment010/FOCUSED_THREE.md`
for reproducible commands and one-slot sparse-only backfill
(offset 26, shard0, count16, one method attempt). Do not overwrite
original n64 BIC result branch or redo nine successful methods.
The fate of the prior focused offset30 batch is unverified;
inspect and preserve VM-local outputs before assuming its
resume cursor.

## Historical empirical manuscript handoff (superseded by four-paper map)

## Evidence-bounded computational manuscript snapshot (3 November 2026)

Independent paper branch: paper/observed-computational-study,
based on the exact head of the still-open draft Experiment010 PR #100,
not merged into main. Existing paper location:
paper/csda-computational-costs/main.tex. Its newly completed
result section is sections/experiment010_observed.tex, and
full source/run ledger is OBSERVED_RESULTS_SNAPSHOT.md.

The manuscript uses **only actual archived corrected data**:
450 executed method-case attempts, 5570 status=ok timing rows,
5480 selected-score parity-only matches, 18 disagreeing records,
72 lacking spectral reference, and 1102 failed/partial observations.
All ten full-criterion policies appear; no synthetic times for
CHOLMOD unavailable, dense infeasible or incomplete methods.
Matched n256,d1,GCV,mu=0 one S: Cholesky 8.13ms, SVD 13.80ms;
matched 100 S: Cholesky 61.31ms, SVD 26.68ms. Three mu
policies zero/data/fixed 0.15 support this descriptive reversal.
Pre-correction MLE normalization discrepancy and its exact log
determinant correction are reported with both immutable source
versions. Separate high-precision Experiment006 reference is
never equated with criterion-score parity.

No validated ten-method dispatcher, cross-machine universal
winner, full factorial or untested n>=1024 timing is claimed.
Prior historical manuscript and figure records are preserved.
Build final PDF from author-supplied Elsevier CAS template
without re-running numerical experiments. Do not merge paper
branch or PR #100 without explicit authorization. Check
the CI/PDF outcome and inspect figures/text after compilation.


### Finished computational-paper index and PDF

Paper branch paper/observed-computational-study, review PR #102.
Published branch PDF: paper/csda-computational-costs/main.pdf
(Elsevier CAS, 15 pages; compiled by Actions run #41649687050,
whose original TeX source SHA and final PDF hash are committed).
LaTeX results: sections/experiment010_observed.tex.
Observed full-case and raw timing provenance:
OBSERVED_RESULTS_SNAPSHOT.md. Reproducible project chronology:
PROJECT_HISTORY.md (Experiments005–010 and earlier historical corpus).
Do not confuse the completed **bounded empirical paper** with
the uncompleted factorial or a numerically certified dispatch policy.
Both PR #100 and dependent paper PR #102 remain unmerged,
pending coauthor review and explicit authorization.
