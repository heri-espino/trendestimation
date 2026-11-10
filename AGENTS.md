**Paper C verified 2026-11-10:** Draft [PR #133](https://github.com/heri-espino/trendestimation/pull/133) has a compiled 12-page method-first physical jerk manuscript, source-derived plots and a frozen-data paired audit. [PC08 run #42767882100](https://github.com/heri-espino/trendestimation/actions/runs/42767882100) passed (PDF SHA-256 `5b6c5305c928e42f4a8b0665f5b2eb0a3a31f9238f86cf427cc3b6defb9ace3f`). Read [full reproducibility handoff](paper/ngsim-jerk-case-study/notes/SCIENCE_EDITORIAL_REVIEW.md) for conditional plug-in TSVD-GCV, nominal EDF (not exact full EDF), 145 high-rank failures, 54-cell paired RMSE bootstrap [0.3227, 0.7134] m/s³, and cumulative horizon RMSE definitions. Original Experiments004–008 not rerun; PRs unmerged; no submission.

**Paper C scientific-editorial continuation (2026-11-09):** Review branch `paper/paper-c-scientific-editorial-review` is derived from the unchanged open PR #131, not PR #132. Read [scientific editorial audit](paper/ngsim-jerk-case-study/notes/SCIENCE_EDITORIAL_REVIEW.md) for method-dependent reference-jerk comparability, conditional plug-in TSVD-GCV/EDF caveats, the exact archival near-interpolation error decomposition, and improved known-jerk-before-calibration reading order. **No Experiment004--008 rerun, no merge and no submission.** Publication PDF/build status must be checked against this branch's latest Actions run; the earlier PR #131 11-page PDF remains a valid historical build, not evidence that these new edits have compiled.

# AGENTS.md — trendestimation research repository
**LATEST PAPER C EDITORIAL DECISION (Nov 9, 2026):** The user explicitly wants the physical/statistical third-order PLS method with normalized interpretable smoothness S, known-jerk simulations and 200 real NGSIM episodes, **not a numerical solver/backend-timing paper**. Read the [method-first editorial handoff](paper/ngsim-jerk-case-study/notes/METHOD_FIRST_EDITORIAL_HANDOFF.md) before making changes. The canonical Elsevier main.tex now includes two simulation cases (Experiment007 relative-noise calibration, 72 independent parent draws/1944 factorial cases; Experiment005/006/008 known jerk, 1296 cases) and the real 200-episode case. A **truncated SVD hard-roughness-filter** is the actual alternative estimator; using full SVD instead of Cholesky to fit PLS is NOT a statistical baseline. Experiment008 [PC08 run #42717662044](https://github.com/heri-espino/trendestimation/actions/runs/42717662044) succeeded, preserving all source rows. **Compiled revised journal PDF** [on Paper C review branch](https://github.com/heri-espino/trendestimation/blob/paper/paper-c-methods-simulation-real-svd/paper/ngsim-jerk-case-study/main.pdf), [audited PC08 run #42719535746](https://github.com/heri-espino/trendestimation/actions/runs/42719535746): 11 pages, 734107 bytes, both figure/semantic audits passed. Open stacked [PR #131](https://github.com/heri-espino/trendestimation/pull/131); no merge authorized. Preserve original figures/backend results and all other Springer/CSDA work, but OMIT solver-timing narrative from Paper C.

**Paper C Experiment007 VERIFIED (2026-11-09):** [Full methods, findings, true-data/calibration figures, complete SHA-256 inventory](paper/ngsim-jerk-case-study/experiments/experiment007/RUN_LEDGER.md). The user requested a new controlled test of whether normalized d=3 PLS smoothness S tracks **known observation noise separately from true jerk volatility**. [Successful Windows PCAG103A-08 run #42660204414](https://github.com/heri-espino/trendestimation/actions/runs/42660204414) and [hosted Linux run #42660028292](https://github.com/heri-espino/trendestimation/actions/runs/42660028292) completed 162 pilot, 1,944 confirmation factorial cases, 7,776 valid S estimates and zero invalid cases. Only 72 independent parent random draws underlie confirmation; all 27 crossed treatments per parent share noise and jerk innovations. In correct iid Gaussian trials, joint-REML S had Spearman 0.965 with the theoretical spectral noise fraction, MAE 0.0115; paired increasing measurement noise raised S by 0.1498 and increasing true jerk variability lowered S by 0.1387. **S is relative covariance noise attribution, NOT absolute sensor precision**: scaling both SDs proportionally preserves S despite a 16x change in observation variance. AR(1) errors substantially degrade calibration (MAE up to 0.1111), even when the directional relationship persists. Raw/clean generated trajectories, theory cells, all 6,048 paired contrasts, analyses, figures, environment, hashes and every path remain in 39-file VM archive at C:\Users\175199\Documents\TrendEstimation-PaperC\experiment007\run-42660204414-a1 and Git results branch results/paper-c-exp007-pc08-42660204414-a1. Never call the 1,944 dependent conditions independent replicates or assert S detects NGSIM sensor accuracy. Preserve other experiments, separate PRs and Springer/CSDA papers, and do not merge without authorization.

**Paper C Experiment006 completed (2026-11-09):** Read [experiment006 complete numerical ledger](paper/ngsim-jerk-case-study/experiments/experiment006/RUN_LEDGER.md), the [frozen study protocol](paper/ngsim-jerk-case-study/experiments/experiment006/README.md), and [stacked PR #127](https://github.com/heri-espino/trendestimation/pull/127). The verified self-hosted PCAG103A-08 [run #42639588117](https://github.com/heri-espino/trendestimation/actions/runs/42639588117) reused 96 original pilot trials, 1,296 original known-jerk confirmations and 200 original real NGSIM episodes, with full source hashes, every new forecast and selection, nested training-only alpha CV, known jerk errors and 47-file VM inventory. Fixed global cubic OLS mu + Gaussian profile ML had the best historical synthetic jerk RMSE among the five tested estimators (2.441 m/s³); joint unknown-mean REML had 3.295. Under real NGSIM, continuous joint REML selected the lambda->0 boundary in 161/200 episodes; GCV splines still forecast recorded positions better in pooled RMSE. The corrected **15-point grid does NOT include lambda=0**; historical earlier runs with that grid bug are preserved but superseded. All source observations and older experiments remain untouched. No population-level jerk truth exists in real camera data, and no stacked PRs should be merged without authorization. Latest repository CI should be verified separately from the successful science workflow.


**Fixed-(mu) Gaussian REML verification (2026-11-09):** The author
confirmed they intended the Gaussian variance-ratio restricted
likelihood of z=Dy−mu·1 and covariance
σ_u²(I+λ DDᵀ), not some distinct forecasting estimator.
[Exact dense/spectral proof and μ-estimation correction](paper/ngsim-jerk-case-study/notes/GUERRERO_GAUSSIAN_REML_EQUIVALENCE.md)
and [numerical regression tests](tests/test_paper_c_guerrero_reml_identity.py)
demonstrate the existing criterion="mle" already minimizes the
**same fixed-μ objective** up to an additive constant
−logdet(DDᵀ). No expensive Experiment004 or 005 rerun is needed
to change this notation. However, replacing μ with sample or
cubic OLS means is **conditional plug-in estimation**, not
mean-adjusted joint/REML mean estimation; a separate REML
method must remove that nuisance mean direction explicitly.
Do not attribute Gaussian likelihood optimization to Guerrero
(2007), whose original PLS variance ratio used second moments.
The PCAG103A-08 Experiment005 workflow previously marked queued
has now completed successfully; verify both source and results
branches before making detailed VM reproducibility claims.
No old results or other PRs were changed in this clarification.


**Paper C Experiment005 VERIFIED synthetic run (2026-11-08):** Read [RUN_LEDGER.md](paper/ngsim-jerk-case-study/experiments/experiment005/RUN_LEDGER.md), [frozen config](paper/ngsim-jerk-case-study/experiments/experiment005/config.json) and [successful cloud action #42547883064](https://github.com/heri-espino/trendestimation/actions/runs/42547883064). The 96 pilot plus 1,296 disjoint-seed confirmation trials produced 89,424 future clean-position errors, 15,552 historical known-jerk fits, 62,208 fixed-S reference crossings, and **zero invalid cases**, all first-party synthetic trajectories and files permanently archived on Git branch **results/paper-c-exp005-cloud-42547883064-a1** (33 files, ~44.8MB). A Gaussian profile-ML selected d=3 PLS trend recovers the known discrete jerk strongly in these simulated error models; raw sample mu can be unstable, a global cubic mean helps sustained nonzero jerk but not reversal. This does **not** establish real-vehicle jerk accuracy. Separate 200-episode NGSIM Experiment004 favors the spline for recorded-position forecasts. PCAG103A-08 simulation job was still queued; use [verified import script](paper/ngsim-jerk-case-study/experiments/experiment005/sync_cloud_results_to_vm.ps1) for cloud archive copy once Windows VM is available, never claim imported outputs were recomputed on VM. Keep full reproducibility/experiment numbering and no merges without authorization.


**Paper C simulation decision and Experiment005 (2026-11-08):**
The author has now **explicitly requested known-jerk simulations**
after the completed real NGSIM Experiment004. This *supersedes* the
older real-data-only note below; neither experimental dataset replaces
the other. Source code, fixed pilot/confirm seed matrix and
[full artifact protocol](paper/ngsim-jerk-case-study/experiments/experiment005/README.md)
are on isolated branch
`research/paper-c-experiment005-known-jerk-simulations`.
A self-hosted [PCAG103A-08 workflow](.github/workflows/paper-c-known-jerk-simulations-pc08.yml)
runs a **96 independent-seed pilot**, followed (only if valid)
by **1,296 disjoint-seed confirmatory trials**. Each trial saves
known analytic x,v,a,j, noisy observations, GCV and profile-ML
PLS fits with zero/sample/OLS/oracle mu, spline and SG comparisons,
known-discrete-jerk errors, future clean-position forecasts, and
fixed-S fit-versus-continuation crossings.
The **oracle** is synthetic-only and must never be offered
as an implementable real-data method. VM storage is persistent
`Documents\TrendEstimation-PaperC\experiment005\run-<id>-a<attempt>`;
the workflow writes and checksums **every output file** and
archives the complete first-party results and compressed trajectories
in an immutable GitHub results branch. **Read the workflow run
and per-stage manifests before claiming completion or superiority.**
Keep original Paper C real-data records and all other paper
workstreams unchanged. Do not merge without authorization.


**Verified Paper C expanded real NGSIM run (2026-11-08):**
[Experiment004 ledger](paper/ngsim-jerk-case-study/experiments/experiment004/RUN_LEDGER.md)
records a successful PCAG103A-08 download/evaluation/compilation
and full persistent VM SHA-256 file tree: 200 qualifying real
episodes, 6,600 valid forecast errors, 800 GCV/profile-ML
PLS selections. Source raw pages (400,000 NGSIM records) remain
on the VM, all model rows plus file inventory also live on
Git results branch `results/paper-c-exp004-pc08-42538556206-a1`.
The observed-position RMSE of a tuned cubic spline is **lower
at all horizons** than the tested PLS strategies in this sample,
contradicting a generalizable reading of the small earlier pilot.
Five coarse capture-time proxies and reused Vehicle_IDs limit
statistical independence; do not call its bootstrap population
inference or jerk-truth evaluation. The user explicitly chose
only real data (not simulations). Open [PR #122](https://github.com/heri-espino/trendestimation/pull/122)
is stacked on separate Paper C PR #121. Do not merge either PR
or edit the Springer/CSDA papers without authorization.


**Paper C expanded real-data follow-up (2026-11-08):** The author
explicitly chose **real NGSIM trajectory data only** (no simulated
physical jerk series), with exploratory vehicle/episode-level paired
forecast inference. See
[experiment004 protocol](paper/ngsim-jerk-case-study/experiments/experiment004/README.md),
[downloader](paper/ngsim-jerk-case-study/experiments/experiment004/fetch_real_ngsim.py),
[evaluator](paper/ngsim-jerk-case-study/experiments/experiment004/evaluate.py)
and [Windows workflow](.github/workflows/paper-c-real-ngsim-gcv-mle-pc08.yml).
It compares profile Gaussian marginal **mle** and GCV from the existing
library, under zero/sample mu and both PLS continuation rules, against
GCV splines and Savitzky--Golay. The two likelihood choices are
different selection criteria, not different PLS estimators. Persist
**all original FHWA CSV pages and complete results on PCAG103A-08**,
outside temporary Actions workspaces; the VM file inventory and
repository results-only branch must report complete paths/hashes.
Existing experiment001-003 results and Springer/CSDA workstreams must
not change. Do not claim true jerk accuracy or independent populations
from observed NGSIM positions. The run is pending verification until
a successful GitHub Actions record and manifest exist.


**Paper C empirical follow-up (2026-11-08):** New
[reproducible Experiment001–003 records](paper/ngsim-jerk-case-study/README.md)
for a (d=3) Guerrero-inspired PLS three-point forecast recurrence,
splines, Savitzky--Golay, and GCV spline continuation; successful
PCAG103A-08 runs and a revised compiled manuscript are linked there.
**There are only two distinct vehicle IDs among the five NGSIM segments.**
Results are observed future-position errors and do not establish
independent physical jerk accuracy or first historical use. Read
[PR #121](https://github.com/heri-espino/trendestimation/pull/121)
and experiment-specific READMEs before changing numerical results.
The earlier "no Paper C experiments run" notes are historical.
Keep separate future known-jerk/independent-vehicle study under the
next available Paper C sequential number (`experiment004`). Preserve
old raw data and figures; do not interfere with Springer Experiment011.


**New Paper C handoff (2026-11-05):** Future agents working on
the FHWA NGSIM application **must** begin with
[nonzero-reference extrapolation research](paper/ngsim-jerk-case-study/notes/EXTRAPOLATION_RESEARCH_HANDOFF.md)
and its [exact fit-vs-continuation decomposition](paper/ngsim-jerk-case-study/notes/EXTRAPOLATION_DECOMPOSITION.md),
[training-only mu options](paper/ngsim-jerk-case-study/notes/MU_POLICY_CATALOG.md),
and [planned experiment001 protocol](paper/ngsim-jerk-case-study/notes/EXTRAPOLATION_ABLATION_PLAN.md).
The `d=3, mu!=0` extrapolation claim is **unverified novelty**;
Whittaker-Henderson extrapolation is established by Biessy (2025/2026).
The current code implements a **separate** local continuation and
only `zero`/`sample` mu. Do not mistake planned policies or
2x2 ablations for completed experiments. Preserve original NGSIM
figures, raw data, results, and other agents' branches/PRs.


**Paper-only compilation (2026-11-04):** See [paper/BUILD_ON_PC08.md](paper/BUILD_ON_PC08.md). The manual workflow uses `PCAG103A-08` and Conda `trendestimation` to compile seven LaTeX entrypoints without figure regeneration, downloads or benchmarks. Its output is an independent archive branch with PDF/log/hash provenance, not a direct write to `main`. Do not confuse this with the Experiment011 Windows benchmark runner. Editorial PR #112 has been merged; older descriptions of it as unmerged are historical.

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


The current author-approved Springer timing study is the focused 29-case Experiment011 design. The historical 252,000-cell Experiment008 planned factorial is retained for provenance but is **not** a requested execution schedule. `paper/benchmarks/experiment011/full_plan.py` reuses the existing Experiment008 planner to index all n,d,mu,amplitude,criteria, 10 methods, four workloads and grid densities, including explicit memory/work skips. The full index does NOT contain observed times. Experiment011 `cases.json` is the author-approved targeted experiment, avoiding rerunning expensive old samples; the end dataset is long-form raw timing plus eligibility/status masks, paired naive speedups, mean/median and independent-block uncertainty. Direct-S and mapped-lambda compare mapping strategies over the same S values, not separately optimized continuous objectives. No RMSE. Preserve all original Experiment008–010 rows and do not trigger 252,000 full runs without explicit review.




## Publication map and Springer experiment011 agent routing (2026-11-03)

**First read** `paper/PUBLICATION_MAP.md`, `paper/AGENTS.md`,
`paper/SPRINGER_AGENT_BRIEF.md` and
`paper/SPRINGER_READINESS.md` before touching any manuscript,
paper figure or benchmark. The canonical Springer *Computational
Statistics* source is `paper/main.tex`; it is **not** the
historical `paper/computational-statistics-submission/` SN
Computer Science paper, the two Elsevier CSDA drafts, or the
separate FHWA NGSIM jerk/forecast application.
CSDA A owns numerical precision, CSDA B owns the theory of
complexity, Springer owns measured complete-criterion implementation
and criterion-specific crossover, and NGSIM owns physical
third-difference applications.

New `paper/benchmarks/experiment011/` is a **prepared,
bounded** 29-case design (2 smoke, 15 pilot, 12 confirm) that calls the existing reviewed
Experiment006 complete-criterion runner without pulling in the
open nested Experiment010 research PR stack. It has explicit
smoke/pilot/confirm gates, independent blocks with rotated
method ordering, source/hardware provenance and float64
selected-S/score QA; do not claim its plan is measured
data. A successful hosted smoke is not Windows benchmark
evidence. Never run the full factorial automatically.
Future agents must work on separate branches and scopes,
push all actual raw results with QA, and update the readiness
ledger. Never merge without explicit authorization.

## Paper B reproducibility revision (November 2026)

Open PR #109 targets the theory-first CAS article
`paper/csda-computational-costs/main.tex`. Read its new
`sections/decision_examples.tex`, `THEORY_HANDOFF.md`,
`SOURCE_AUDIT.md`, frozen `data/` CSV, and
`render_theory_figures.py` before changing figures or
theory claims. The four new plot sets include two theoretical
unit-coefficient **work counts** (never claim machine time),
one controlled isolated 48-row n64/d1/BIC timing illustration,
and one real NGSIM jerk-proxy vehicle-position training/heldout
illustration (d3 training-only mean, GCV S=.4; separately appended
local polynomial forecast). The large theoretical picture is
**criterion-dependent**: dense spectral SVD can amortize scalar
scores on many S candidates, but exact CV can favor banded
Cholesky with selected inversion for large n and small d.
Do not conclude a universal optimal method, mix runtimes from
different contention, rerun archived full grids unnecessarily,
or publish an implied PLS-native forecast. Preserve
the third NGSIM paper's original FHWA attribution/CC BY-SA
3.0 source. Do not merge concurrent branches without consent.


Read README.md, this file, paper/benchmarks/README.md,
paper/benchmarks/experiment005/README.md, source modules, and tests
before editing. Existing numerical decisions and archived results are
authoritative. Preserve all experiment artifacts, metadata and manuscript
figures in Git; never invent or overwrite measured timings.

## Non-negotiable scientific contracts

- PLS objective: ||y-tau||^2 + lambda ||D_d tau - mu 1||^2.
- For fixed mu, A = I + lambda D_d.T D_d is SPD at finite lambda>=0.
- Guerrero's normalized smoothness coordinate depends only on n,d,lambda,
  not on y or fixed mu; preserve spectral S and inversion.
- The default fit-only method remains full SVD with shift-free reconstruction.
- New structured backends calculate trends only; selection and EDF remain
  spectral until separately validated equivalent criterion implementations exist.
- A fast incorrect, incomplete, or nonconverged result cannot win a timing
  comparison. Failed and optional-dependency cases must be retained.
- CHOLMOD/scikit-sparse is optional; SciPy SuperLU is not Cholesky.

## Concurrent agent workflow

Work on your own branch. Preserve other agents' branches, worktrees, PRs
and experiments. Name experiments sequentially as experiment001,
experiment002, etc. Include rationale, commands, seeds, actual outputs,
machine environment, findings and next steps. Never merge unrelated PRs.
Commit/push scripts, raw benchmark data, figures, numeric QA, and handoffs.
Use Git LFS or documented storage for oversized outputs and never commit secrets.

## Experiment005 handoff

See paper/benchmarks/experiment005/README.md for the new sparse,
banded-LU and PCG parity benchmark and run presets. Python tests:

    python -m pytest tests/test_experiment005_structured_solvers.py -q
    python paper/benchmarks/experiment005/run.py --preset smoke

Large timing presets are manual on a designated machine; CI does not
establish universal performance rankings. See AI_HANDOFF.md for status.


## Experiment006 repository-first rules

For any experiment006 work first inspect README.md, this AGENTS.md,
AI_HANDOFF.md, paper/benchmarks/experiment006/README.md, actual source,
tests and current draft PR #95. Preserve all previous experiments.
Keep source, numerical validation, full-factorial manifest and measured
results in Git. Use independent branches/worktrees for Windows runs.
The primary outcomes are computation time, memory, exactness and
failure status. No trend RMSE claims. The three implemented complete
criterion pipelines must not be conflated with Experiment005 fit-only
solvers; missing methods remain explicitly not implemented. High-order
nonzero-mu regimes and S=1 require independent numerical auditing.
Never merge without explicit user authorization.

## Experiment006 hybrid scientific contract (latest)

Six hybrid sparse/iterative plus banded selected-inverse diagnostic
pipelines have been added to the Experiment006 runner. Compare their
full measured cost including every factorization, not just their trend
fit time. Check tests/test_experiment006_hybrid_criteria.py before
interpreting speed rankings. No unrecorded timing or numerical results.


## Experiment007 — observed-difference mean frontier

Experiment007 independently measures mu='data'=mean(D_d y), never
manually assigned an arbitrary mu. It keeps mu=0 as a control,
records synthetic latent-trend mean(D_d tau_true) only as an oracle
diagnostic, and does not use this oracle for fitting. The d<=4
versus d>=5 switch was a small-n guard, not an optimal policy.
Review experiment007/README.md and tests before changing any
backend policy. Separate fit-only results from whole-criterion
CV/GCV/BIC/AICc/MLE costs; no invalid QA cell may be ranked.


## Experiment008 complete-criterion timing factorial

The user requested computation-time research ONLY, not RMSE:
n=64/128/256/512/1024/16384/131072, all d=1..6, mu zero
versus actual observed-difference mean mu='data', fixed nonzero
reference as a control, two amplitudes, CV/GCV/BIC/AICc/MLE,
four S grids M=100/1000/10000/100000 INCLUDING exact S=1,
all four one/multiple S x one/multiple series workloads,
direct_s versus pretranslated mapped_lambda, and naive explicit
dense inverse versus actual complete-criterion solvers/hybrids.

Research source and metadata:
paper/benchmarks/experiment008/{README.md,run_batches.py}.
Windows runner action: .github/workflows/experiment008-full-factorial.yml
and large-series action .github/workflows/experiment008-large-series.yml.
Use existing nonadmin conda env 'trendestimation' (no installations).
The compressed full Cartesian manifest is a PLAN, not fabricated
measurements. Actual time rows, failures and ineligibilities must
be kept distinct and pushed to results/experiment008-* branches.

Experiment008 opts into conditional plug-in mu='data' criteria for
computation timing. It is NOT fully refitted LOOCV or a new statistical
definition. The old main API behavior remains unchanged without the
explicit conditional_data_mu=True keyword in run_slice.
Never claim naive inverse at n=131072 is a feasible comparison:
one dense float64 n-by-n matrix is 128 GiB, before factorization.
Do not merge until actual results, numerical checks and CI are verified.


## Experiment009 n,d solver cost-crossover theory

Research branch research/experiment009-cost-crossover-surface;
PR #99. Source, frozen exact Windows empirical data, tests and
mathematical theory: paper/benchmarks/experiment009/. Theory is a
FAMILY of n,d boundaries indexed by candidate count M, series
count R and criterion C. Never identify a universal d cutoff.
Do NOT train a full-criterion cost model with fit-only times:
complete spectral fitted trends cost O(n^2) PER candidate, while
scalar global spectral scores can be O(n) per candidate after
setup; ordinary CV can require O(n^2). Experiment007 Cholesky
does NOT factor-cache across series; Experiment008 does when
budget permits. Experiment008 n<=512 cold setup includes a
COMMON dense spectral S->lambda mapper for both backends.
All reported predictions require machine-specific calibration,
numerical validity and dense-memory gating. Holdout results are
single-class and cannot certify the switch. Do NOT change
production default or merge without authorization.


## Final Computational Statistics engineering evidence (2026-11-03)

The Springer manuscript entrypoint is paper/main.tex, NOT the SNCS
or Elsevier CAS companion. It includes the 48 measured n64/d1/BIC
rows from two independent GitHub result-branch commits, with source
data and QA at paper/benchmarks/experiment010/publication_evidence/.
SVD/naive ran in an 8-worker pool; the CHOLMOD hybrid backfill used
one process. Do not interpret their elapsed seconds as a controlled
relative-performance ranking. CHOLMOD hybrid includes separate banded
selected-inverse diagnostics, not just a sparse factorization.
For controlled runtimes, rerun all three on the same machine in one
batch with Workers=1. Setting Workers=8 on just one method-case
launches only one subprocess. Never silently rewrite archived
source data, inflate selected-score parity into high-precision
accuracy certification, or mix with the historical full-factorial
Windows datasets.

## Mainline CHOLMOD 0.5 compatibility (2026-11-03)

Read notes/scikit_sparse_v05_windows.md when touching sparse Cholesky.
The user verified real CHOLMOD fit parity on Windows (maximum difference
1.2948756650255078e-13 at n64/d2/lambda2/mu0.15) and passed 110
targeted tests. Modern scikit-sparse requires cho_factor(csc_array(A))
followed by .solve(rhs); keep old Factor.solve_A() compatibility.
Never substitute SuperLU silently; keep large-run score/timing claims
separate from single-fit validation.


## Paper B theoretical CSDA manuscript (November 2026)

The active dedicated branch is paper/csda-computational-theory.
Read paper/csda-computational-costs/THEORY_HANDOFF.md before editing.
Paper B is mathematical computational complexity, NOT an end-to-end
Windows timing-paper claim. Current main.tex includes foundations,
algorithms, structured_criteria, amortized_frontier and
theory_discussion only. All prior empirical sections, historical CSVs,
AwesomeFigures and result branches are retained but excluded from the
theory article. The analytical identity
logdet(C_lambda)=logdet(A_lambda)-(n-d)log(lambda)-logdet(D_d D_d.T)
and its quadratic objective equality are verified on deterministic
small cases by paper/csda-computational-costs/verify_theory.py.
A new .github/workflows/csda-computational-theory.yml compiles the
exact Elsevier CAS class, without rerunning computational benchmarks.
Do not introduce a runtime ranking from mixed-concurrency evidence.
The new matched one-worker Experiment010 n64/d1/BIC run is archived
in the user's results/...20261103T222938857Z-shard0-offset20 branch;
use it for the SEPARATE Springer implementation paper. Keep theory
claims qualified against Weinert 2007, Biessy 2026 and
Erisman--Tinney 1975; do not claim algorithmic novelty for their work.
Do not merge a Paper B PR without explicit authorization.

## Historical Experiment010 runner handoff (not the active Experiment011 schedule)

## Experiment010 — multi-backend feasible runtime frontier (draft research plan)

Read paper/benchmarks/experiment010/README.md before new computational
benchmark work. Compare all ten complete-criterion Experiment006/008
pipelines, separately identifying composite guarded policy versus actual
solver, across mu=0, observed-difference mu='data', and fixed nonzero
mu=c. Use *identical S candidate grids*, including analytic S=1, for
both direct-S and once-pretranslated lambda policies. Include every
mapping, factorization, diagnostic and cache cost. Fit-only timing is
not an honest complete criterion comparison. Rank only memory-feasible,
installed, numerically certified pipelines; record failures and retry
an independently validated next-best method. Validate machine-specific
theoretical cost rankings on held-out empirically measured boundary cases.
This is a design protocol, NOT an implemented dispatcher or completed
Experiment010 benchmark. Do not change the library's default policy.


### Experiment010 mathematical scoring audit after first Windows run

First university VM run #41586066141 succeeded (smoke and pilot), yielding
420 + 720 measured status=ok timing rows. The pilot's 104 selected-score
disagreements included 100 for n64,d5,mu='data',MLE and 4 for n64,d6,
mu=0.15,CV. Read notes/experiment010_mle_normalization_audit.md BEFORE
ranking MLE methods. The old banded/hybrid/naive experimental MLE finite
lambda scores omitted logdet(D_d D_d.T), unlike spectral MLE and the exact
S=1 endpoint. Corrected on PR #100 using an O(d) analytic log-gamma
formula; keep original immutable result branches as PRE-correction evidence.
Use fresh measurements/tests and high-precision accuracy certificates
before claiming reliable winners or updating the CSDA manuscript.


## Experiment010 full-grid execution (2026-11-03)

Current independent branch research/experiment010-comprehensive-grid
is based on draft PR #100; it does NOT change PR #100 and must NOT be
merged without authorization. Read paper/benchmarks/experiment010/
COMPREHENSIVE_GRID.md. The 403200-cell feasibility DESIGN is archived
at results/experiment010-41647428485-a1-comprehensive-plan.
The first bounded actual measurement action #41647428485 runs
shards 0..3 of 16, each with at most 40 method-case attempts;
completion and results must be verified separately.
Preserve correct source SHA, complete raw timing and failure
logs, machine fingerprint and independent numerical certificates.
Resource-ineligible-all-workloads is an explicit status, never
a measured zero-second winner. A complete manifest does not
mean that the full feasible experiment has run.
The user declined further cost-prediction and fallback-regret
research for the current manuscript. Scope = accuracy and
measured time of ten existing complete-criterion pipelines.


## Experiment010 uncapped manual VM protocol (2026-11-03)

The user requested reruns WITHOUT artificial per-method runtime
timeouts or estimated-work exclusions. Source branch:
research/experiment010-uncapped-checkpointed (draft PR #103
stacked on PR #101). Read
paper/benchmarks/experiment010/UNCAPPED_LOCAL.md for the exact
PowerShell worktree/conda commands and immutable result-archive
script. The `--no-time-limit` option disables both per-method
and whole-batch time thresholds and uses unlimited estimated-work
budget. It does NOT bypass 2 GiB default dense-memory safety,
any numerical criteria, or actual OS/VM interruption. A small
`--max-method-attempts` is a checkpoint size, NOT a timeout.
Preserve real per-row times, numerical failures, and stderr logs,
including incomplete interrupted attempts. Never claim that
local runs have executed unless the corresponding results branches
exist and have been inspected.


## Experiment010 VM parallel local work (2026-11-03)

The user's 32-logical-processor Windows VM was bottlenecked by
sequential method subprocesses. The independent branch
research/experiment010-parallel-local (draft PR #104 stacked on
#103) adds `paper/benchmarks/experiment010/run_parallel.py` and
`-Workers 8` in `run_uncapped_local.ps1`. Follow
`paper/benchmarks/experiment010/PARALLEL_LOCAL.md` precisely.
Each method runs in its own process at one BLAS thread. The main
process is the sole atomic method-ledger writer and records all
numerical failures, timeout absence, resource exclusions, and
separate logs; final raw outputs are committed and pushed to a
unique branch. Eight workers is a conservative start; 32 logical
processors does not imply 32 safe concurrent processes. The default
RAM reservation is 2 GiB x 8 workers = 16 GiB; this is a scheduling
budget, not actual operating-system memory enforcement. Parallel
elapsed times involve CPU/resource contention and must not be
pooled as isolated serial latencies. Do not overwrite running
serial shard0 offset10 outputs or run duplicate case IDs.
Do not merge this stacked draft PR without authorization.


## Experiment010: Windows locked-CSV checkpoint and parallel safety

The manually completed shard0 offset10 batch archived all 10
method subprocess outputs despite final `PermissionError
[WinError 5]` replacing `method_attempts.tmp` to CSV. Archive:
results/experiment010-uncapped-PCAG103A-08-20261103T155726693Z-shard0-offset10.
It lacks batch_summary.json; both archived ledgers show all ten
completed subprocesses, with 0 valid rows for optional CHOLMOD.
The next correct shard0 cursor is **20**; never rerun offset10.
Source branch research/experiment010-parallel-local now retries
transient Windows locked-ledger replacement with backoff, preserves
unique recovery CSV if replacement remains denied, and adds
regression tests simulating this error. The parallel batch summary
identifies the effective ledger path. Read PARALLEL_LOCAL.md before
running. Keep source and archives distinct; do not merge.


## Experiment010 focused three-method large campaign (2026-11-03)

The user explicitly requests `naive_inverse`, `spectral_svd`,
`sparse_cholesky_banded_trace` ONLY for the upcoming large numerical
experiment. Read `paper/benchmarks/experiment010/FOCUSED_THREE.md`.
The 8-worker uncapped parallel n64/d1/BIC/high-amplitude/
mu=data/M100000 result batch at shard0 offset20 finished and is
archived at
results/experiment010-uncapped-PCAG103A-08-20261103T165925192Z-shard0-offset20.
It measured 144 valid score-parity-only rows; eight setup failure
rows belong to optional CHOLMOD (sparse Cholesky has no valid
numeric timing). Workload wall time was 1109.3s, with strong
parallel resource contention. No independent 85-digit accuracy
certificate is established. Next original ten-method shard0
cursor is **30**; do not repeat offsets 20–29.

The new independent research/experiment010-focused-three branch
keeps all ten methods and historical results intact but selects
only the requested three at launch. Nonselected full-design
positions get explicit `method_not_selected` ledger/manifest status.
Missing CHOLMOD is preflight `dependency_unavailable`, not a
zero-second success. The original ten-method shard cursor is
unchanged for conflict-free resumption. Dense naive/SVD also remain
RAM-infeasible at very large n. DO NOT merge other agent branches
or claim a genuine three-method comparison where one is missing.


## Experiment010 scikit-sparse 0.5 compatibility (2026-11-03)

The Windows Conda optional `scikit-sparse` install now imports,
but a user-supplied legacy `cholesky(A)(b)` smoke command fails
with `TypeError: 'tuple' object is not callable` due to
scikit-sparse 0.5's revised API. Correct public call:
`cho_factor(csc_array(A)).solve(b)`. Branch
research/experiment010-cholmod-v05-compat (stacked on #105)
explicitly uses SciPy CSC arrays for modern CHOLMOD while
preserving old 0.4 `Factor.solve_A`; a functional tiny PLS parity
preflight prevents unverified long benchmark attempts. Read
paper/benchmarks/experiment010/FOCUSED_THREE.md.
Do not claim the actual Windows installed build passed the solver
tests until its real VM output is archived. Never rerun previously
archived naive/SVD results just because optional CHOLMOD was installed.
