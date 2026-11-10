> **November 9, 2026 paper-version history:** Before creating or compiling a new paper revision, read [PAPER_HISTORY.md](PAPER_HISTORY.md). It records the A+B consolidated theoretical draft and separate Springer/NGSIM compilations, exact source commits, PDF SHA-256 values, build logs, and retained predecessors. Source and archive branches are deliberately separate; do not overwrite prior results or merge unreviewed research PRs. Historical A/B separation below predates the later author consolidation decision.

# Paper work — mandatory manuscript/experiment routing

**Paper C extrapolation handoff (2026-11-05):** In addition to the
literature index below, read
[EXTRAPOLATION_RESEARCH_HANDOFF](ngsim-jerk-case-study/notes/EXTRAPOLATION_RESEARCH_HANDOFF.md),
[EXTRAPOLATION_DECOMPOSITION](ngsim-jerk-case-study/notes/EXTRAPOLATION_DECOMPOSITION.md),
[MU_POLICY_CATALOG](ngsim-jerk-case-study/notes/MU_POLICY_CATALOG.md),
and [EXTRAPOLATION_ABLATION_PLAN](ngsim-jerk-case-study/notes/EXTRAPOLATION_ABLATION_PLAN.md).
The user's new hypothesis is **d=3 PLS with nonzero reference
jerk plus local-polynomial extrapolation**, not a new PLS model.
Biessy 2025/2026 already performs WH extrapolation.
An exact fixed-S 2x2 decomposition is provided for testing
fit versus continuation contributions. No new empirical data, mu policies, forecast results or manuscript
edits are implied by these notes; a deterministic algebra regression
is provided in `ngsim-jerk-case-study/tests/`.
Any new scientific results belong in **Paper C** and a
separate reproducible experiment, not Springer Experiment011.


**Paper C primary literature notes (2026-11-05):** Before editing the NGSIM
manuscript, read [NGSIM annotated notes](ngsim-jerk-case-study/notes/README.md),
[the literature comparison](ngsim-jerk-case-study/notes/LITERATURE_REVIEW.md),
[the mathematical notes](ngsim-jerk-case-study/notes/MATHEMATICAL_NOTES.md)
and [prior novelty audit](ngsim-jerk-case-study/NOVELTY_AUDIT.md).
The examined primary sources include Fan (2024), Marczak–Buisson (2012),
Cao (2021), Zhu (2024), and Tang's arXiv source archive. No new empirical
evaluation or manuscript submission follows from the review.
**Do not describe estimated jerk as true physical jerk, the plug-in
mean as robust, or unconstrained PLS as guaranteeing kinematic limits.**


**Parallel editorial review (2026-11-04):** [draft PR #112](https://github.com/heri-espino/trendestimation/pull/112) contains targeted writing and mathematical corrections for the four publication tracks and a separate direct-weights draft. The [editorial literature audit](EDITORIAL_LITERATURE_AUDIT.md) records source support and unresolved checks. It does not supersede the Experiment011 case design or authorize merges/submissions. Preserve manuscript branches and experimental data.

**Integration status (2026-11-04):** the author authorized merging the open research PRs.
Read [cleanup audit](REPOSITORY_CLEANUP.md) and the current session handoff.
Use `origin/main` after integration; older “open/unmerged” statements below
are historical. Experiment011 remains 29 cases; Windows measurements are pending.


**Session continuation (2026-11-04): read [SESSION_HANDOFF.md](SESSION_HANDOFF.md) first.** It records the four-paper split, approved 29-case scope, current PRs, Windows missing-file diagnosis, exact results-worktree commands, and pending measurements. The next author action is the small 16-series/16-worker GCV pilot; the Windows campaign is not yet measured.

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


The preserved original Experiment008 full factorial has 252,000 planned method-workload-coordinate cells, from seven n values, six d values, three reference-mean policies, two data scales, five criteria, 10 implemented complete pipelines, two coordinate mapping policies, two single-S workloads and eight grid-workload variants. See `paper/benchmarks/experiment011/full_plan.py` (a non-executing Experiment008 planner wrapper). Experiment011 now has 29 active cases; the old full factorial is a background reference, not a mandate to run all cells. Never present the full eligibility manifest as real observations or imply that all infeasible dense large-n cells have been timed. Benchmark goal is computing time against the genuine naive inverse, not RMSE.



This file applies to all manuscript and benchmark artifacts below `paper/`. Read the root `README.md`, `AGENTS.md`, `AI_HANDOFF.md` and `paper/PUBLICATION_MAP.md` **before editing**. Preserve previously accepted experiments, raw data and all other agents' open PR branches.

## Authoritative manuscript routing

- **CSDA A (precision/spectral mathematics):** `paper/csda-spectral-smoothness/`. High-precision numerical validation, shift-free spectra and intrinsic estimator reliability.
- **CSDA B (cost theory):** `paper/csda-computational-costs/`; current authoring is on **PR #109**, which is not main. Mathematical operation-count and memory models, proof of selected-inverse sufficiency, conditional crossover, plus only bounded illustrative timings and jerk context. Do not duplicate the theoretical contribution in another journal.
- **Springer Computational Statistics (actual implementation and timing):** `paper/main.tex` and `paper/sections/`, using the official Springer `sn-jnl` class. Existing PDF is archived. This research follow-up is `paper/benchmarks/experiment011/`, with agent brief `paper/SPRINGER_AGENT_BRIEF.md` and readiness ledger `paper/SPRINGER_READINESS.md`. Source-controlled stage cases and numerical QA come **before** any new best-method assertion.
- **NGSIM physical application:** `paper/ngsim-jerk-case-study/`. Real FHWA vehicle-position data, d=3 third differences, training-only data mean, separate extrapolation and observed-future errors. No measured true jerk or native TrendSmoother forecasting claim.
- **Historical SN Computer Science draft:** `paper/computational-statistics-submission/`. This is **not** the canonical Springer Computational Statistics source `paper/main.tex`. Do not change its journal or formatting by mistake.

## General scientific standards

1. Preserve every original CSV, JSON, source program, TeX, figure, log and environment manifest. New outputs get new paths or branches, never overwrites.
2. Distinguish mathematical arithmetic counts from measured seconds and separate solver fit-only timings from *complete* CV/GCV/AICc/BIC/ML selection cost. CHOLMOD plus separately charged banded diagnostics is a hybrid, not pure CHOLMOD.
3. Compare matched statistical objectives, candidate S values, input seeds, n,d,R,M,mean policy, criterion, numerical validity and hardware. Do not mix one-worker latency and eight-worker throughput or call a resource skip a completed fast result.
4. `mu='data'` is a response-dependent plug-in of observed d-th differences. Fixed-mu leave-one-out CV is only conditional when that mean is estimated on full training observations. RSS-BIC has an ill-posed interpolation boundary. MLE score conventions may differ by a lambda-independent offset.
5. Use AwesomeFigures and the **actual journal's LaTeX style**; document fonts, output dimensions, and retain vector PDF/PGF where appropriate. Never fabricate computational or physical results for illustrations.
6. Independently validate numerical scores before attributing measured winner rankings. The Experiment010 matched 48-row BIC pilot has just two repeats and cannot certify an n/d/C surface.
7. Separate source branches, worktrees, tasks and PRs for concurrent agents. Do not merge a research or manuscript PR without explicit authorization.
8. At handoff, update `AGENTS.md`, `AI_HANDOFF.md`, the relevant experiment README and the Springer readiness ledger with exact completed work, what was not done, reproduction commands, PR/branch SHA and required next steps.

For the Springer campaign, only `campaign.py run --case ...` executes a declared case. The default plan/list commands never start an expensive full factorial. A confirmation-stage run requires `--allow-confirm`. The tiny GitHub Actions smoke is not the user's Windows VM runtime dataset. The source of truth for results is the committed, user-verified result branch and its raw rows.
