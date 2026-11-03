# AGENTS.md — trendestimation research repository

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
