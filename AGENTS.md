# AGENTS.md — trendestimation research repository

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
