**Paper C scientific-editorial continuation (2026-11-09):** Review branch `paper/paper-c-scientific-editorial-review` is derived from the unchanged open PR #131, not PR #132. Read [scientific editorial audit](ngsim-jerk-case-study/notes/SCIENCE_EDITORIAL_REVIEW.md) for method-dependent reference-jerk comparability, conditional plug-in TSVD-GCV/EDF caveats, the exact archival near-interpolation error decomposition, and improved known-jerk-before-calibration reading order. **No Experiment004--008 rerun, no merge and no submission.** Publication PDF/build status must be checked against this branch's latest Actions run; the earlier PR #131 11-page PDF remains a valid historical build, not evidence that these new edits have compiled.

# Publication map — source of truth for all TrendEstimation agents
**Paper C NEW editorial scope (2026-11-09):** Method-first d=3 PLS smoothing and physical jerk/noise calibration, synthetic/NGSIM comparisons; NOT computational solver timing. [Authoritative method-first paper handoff](ngsim-jerk-case-study/notes/METHOD_FIRST_EDITORIAL_HANDOFF.md), [PR #131](https://github.com/heri-espino/trendestimation/pull/131). Synthetic case (1296 known clean-jerk trajectories) now includes new hard truncated SVD estimator, matched EDF vs GCV rank, cubic spline GCV and SG. Joint S-calibration experiment on 1944 paired noise-dynamics conditions (72 independent simulated parent draws) stays in paper with explicit relative vs absolute precision caveat. Real NGSIM larger sample 200 recorded episodes, 5 coarse time blocks, no true jerk. Successful PC08 method-first [paper PDF build #42719535746](https://github.com/heri-espino/trendestimation/actions/runs/42719535746), 11 pages, source plot and audit passed, full VM hash manifests and figures permanently retained. Separate Springer computation paper remains dedicated to tensor timing/solver SVD, and separate CSDA theory paper remains untouched; numerical backend artifacts preserved but excluded from physical Paper C text. No merge or journal submission without authorization.

**Paper C Experiment007 (2026-11-09):** The author specifically requested [a paired model-based test of normalized S vs known observation noise and true jerk dynamics](ngsim-jerk-case-study/experiments/experiment007/RUN_LEDGER.md). Completed on PCAG103A-08 [run #42660204414](https://github.com/heri-espino/trendestimation/actions/runs/42660204414) plus independent Linux calculation. 1,944 factorial confirm conditions/72 independent parent draws, full third-difference clean/noisy positions, covariance-attribution true S, selected S and all 39 VM-file hashes archived. Main result: iid Gaussian joint-REML S tracks relative noise fraction well (Spearman .965, MAE .0115); noise and true jerk SD have expected opposite effects. **Sensor precision is not identifiable from S alone**; equal variance ratio despite 16-fold observation variance change gives same S. Under correlated observation errors, calibration degrades, so the interpretation requires noise-model diagnostics and restrictions. This is a targeted calibration contribution to existing third-order PLS theory, not a new estimator theorem or real sensor-accuracy claim. Neither Paper C manuscript nor Springer/CSDA papers changed. PR stacked on other unmerged Paper C branches; never merge without approval.

**Paper C latest (2026-11-09):** [Experiment006 documented results](ngsim-jerk-case-study/experiments/experiment006/RUN_LEDGER.md) add **joint unknown-reference REML** and forecast-oriented nested alpha shrinkage to the previous jerk/NGSIM studies. Verified PC08 workflow #42639588117 and the archived 47-file VM/Git result inventory. Reused identical Experiment005/004 source observations, 1296 analytic trials and 200 NGSIM episodes. True synthetic D3 jerk RMSE 2.441m/s³ for global OLS profile ML versus 3.295 for joint REML; the real camera target remains observed future position with the GCV spline better overall. **Joint continuous REML often selects lambda=0 on real data (161/200), whereas the corrected 15-value grid excludes zero.** Do not claim new empirical drivers/known physical jerk, superiority or completed manuscript submission. Keep all original files and other Springer/CSDA paper assignments intact. Source review in [open PR #127](https://github.com/heri-espino/trendestimation/pull/127).


**Paper C Experiment005 successfully simulated (2026-11-08):** [verified RUN_LEDGER.md](ngsim-jerk-case-study/experiments/experiment005/RUN_LEDGER.md) documents 96 pilot and 1,296 confirm independent known-jerk trials, complete cloud data/results in results/paper-c-exp005-cloud-42547883064-a1 and zero numerical failures. PLS Gaussian profile ML strongly outperformed GCV PLS and benchmark splines/SG for known discrete-jerk RMSE in the predeclared simulation mixture; GCV cubic spline remained the best overall for observed-position forecasts on Experiment004 real NGSIM. Both opposite-looking findings are preserved, not selectively reported. Windows PC08 workflow remains queued, the hosted data are not yet VM copies. Paper C results are segregated from Springer numerical optimization and CSDA papers, and only this paper may use this synthetic experiment. No paper submission or merge authorized.


**Paper C Experiment005 planned/executing (2026-11-08):**
The author newly authorized known-jerk simulations
after the 200-episode observational Experiment004.
[Fixed config](ngsim-jerk-case-study/experiments/experiment005/config.json)
and [full handoff](ngsim-jerk-case-study/experiments/experiment005/README.md)
cover 96 pilot and 1,296 confirm independent
analytic truth/noisy position trajectories. Compare
`d=3` PLS GCV/profile ML across zero, sample, OLS
and oracle `mu` plus last3/local25, against GCV splines
and SG, with known D3 jerk and clean future position
truth. The PC08 runner archives **all generated artifacts
and exact path/SHA index** without overwriting the
real-data study. This research is solely **Paper C**
and does not modify Springer or CSDA reports. No
results or claims are established before the runner's
actual completed manifest is verified.


**Paper C expanded experiment004 completed (2026-11-08):**
See [run ledger](ngsim-jerk-case-study/experiments/experiment004/RUN_LEDGER.md),
[PC08 completed job](https://github.com/heri-espino/trendestimation/actions/runs/42538556206)
and [stacked PR #122](https://github.com/heri-espino/trendestimation/pull/122).
The real-only US-101/I-80 comparison produced 200 episodes,
6,600 valid held-out recorded-position forecasts, 800
GCV/profiled-Gaussian-ML selections, and a compiled current
Paper C PDF on PC08. The canonical full original raw downloads
and results live in documented persistent VM storage; the
separate Git results branch records the full scored rows,
provenance and SHA inventory. A GCV spline has the lowest
pooled RMSE at 0.5, 1 and 2 s. There are only five recording
session proxy groups and no true physical jerk labels; do
not claim general inference, novelty, or first-use proof.
No Springer/CSDA manuscript was altered by this experiment.


**Paper C update (2026-11-08):** Author-led experiments
[001](ngsim-jerk-case-study/experiments/experiment001/README.md),
[002](ngsim-jerk-case-study/experiments/experiment002/README.md)
and [003](ngsim-jerk-case-study/experiments/experiment003/README.md)
now compare (d=3) three-point PLS continuation with local-25 and
predeclared splines, Savitzky--Golay and other conventional baselines.
All new results and source code are in [PR #121](https://github.com/heri-espino/trendestimation/pull/121),
with verified PC08 runs and successful revised CAS compilation.
This remains an **NGSIM real-position forecasting paper**, not
the separate numerical complexity, precision or Springer timing
papers. Five track segments represent **only two vehicle IDs**.
The GCV spline outperforms the PLS recurrence at 2,s, though PLS
is better at 0.5,s. Do not claim universal forecasting or jerk
accuracy. Next step: true-jerk simulation and independent vehicles.


**Paper C focus update (2026-11-05):** The proposed scientific
question is whether **d=3 third-difference PLS with a nonzero
training-derived reference jerk**, followed by an **explicitly
separate local polynomial continuation**, improves vehicle-position
forecasts and/or estimated jerk behavior. This is an **unproven
applied novelty/performance claim**, not a new PLS estimator or first
WH extrapolation. Biessy (2025/2026) previously developed WH
extrapolation. Read the [Paper C extrapolation handoff](ngsim-jerk-case-study/notes/EXTRAPOLATION_RESEARCH_HANDOFF.md)
and [planned experiment](ngsim-jerk-case-study/notes/EXTRAPOLATION_ABLATION_PLAN.md).
The existing five-track pilot remains descriptive; Paper C retains
exclusive ownership of any future physical forecasts. No shared
Springer/CSDA manuscript is changed by this documentation.


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


**Status:** research drafts and separate submissions; no journal acceptance or submission is implied. Updated 2026-11-03. Read this before creating an experiment, editing a manuscript, or merging a paper PR.


**Historical full timing design (retained, not scheduled):** The original
252,000-cell Experiment008 factorial remains a reference index
(n=7 sizes, d=1..6, mean=0/data/0.15, low/high amplitudes,
5 criteria, 10 complete pipelines, 2 direct/mapped coordinate
modes, and 2 single-S workloads plus 2 grid workloads at
M=100/1000/10000/100000). The one-S cells occur only once per
base configuration, not four times. Experiment011's **29 selected cases** are now the active author-approved
study; the original 252,000-cell full factorial must not be executed
on the basis of these instructions. Its
`full_plan.py` now reuses Experiment008's full-factorial
manifest logic and saves all cells/status flags without
running the expensive factorial. Full-grid CV may be
substantially more expensive than GCV; the final empirical
paper must measure supported cells on the Windows host
and preserve the infeasible mask as a scientific result.



## Four distinct scientific questions

| Track | Canonical source | Core contribution | Allowed evidence | Claims that belong elsewhere |
|---|---|---|---|---|
| CSDA A: spectral reliability | `paper/csda-spectral-smoothness/` | Numerical reliability, shift-free/spectral formulation, smoothness coordinate and high-precision accuracy | Analytical identities, 85-digit reference and independent numerical error tests | Broad machine-level runtime superiority; physical forecasts |
| CSDA B: theoretical computational costs | `paper/csda-computational-costs/` | Formal \(T_{\mathcal A}(n,d,M,R,\mathcal C;\epsilon,\theta)\), criterion-dependent amortized operation and memory bounds, selected inverse and crossover conditions | Proofs and unit-cost theory illustrations; a **small, clearly labeled** matched timing example; one contextual jerk illustration | Claims of universal fastest backend, exhaustive empirical crossover, method-independent stopwatch constants |
| Springer: measured software/implementation | `paper/main.tex` and `paper/sections/` | Empirically reproducible **complete criterion pipeline** performance, measured milliseconds/seconds, numerical validity, caching, concurrency/throughput, feasible algorithm-choice maps | Frozen raw Windows experiment results, independent checks, uncertainty across paired blocks, full environment; bounded theoretical explanations cited from CSDA B | Re-presenting CSDA B's proofs as a second novel theorem; using fit-only timings as complete CV runtime; unverified speedups |
| NGSIM: third-difference/jerk application | `paper/ngsim-jerk-case-study/` | Real FHWA US-101 trajectories, jerk proxy, training-only selection and separate polynomial continuation with actual chronological holdouts | Real attributed position data, d=3 and training-only mu='data', forecast error against recorded future, physical baselines | Claim that PLS intrinsically forecasts or raw third differences are ground-truth jerk; global hardware speed ranking |

**Other existing manuscript:** `paper/computational-statistics-submission/` is an independently preserved *SN Computer Science* submission draft, not the canonical Springer *Computational Statistics* entrypoint above. Do not silently swap journal templates (Springer `sn-jnl` versus Elsevier `cas-dc`) or confuse this historical draft with a new paper.

## Status and version boundaries

- Main branch currently contains the previously compiled Springer `paper/main.pdf` and `paper/computational-statistics-submission.zip` from paper PR #107. Its narrow three-method illustration `paper/benchmarks/experiment010/publication_evidence/` combines **8-worker SVD/naive** and **1-worker CHOLMOD** archival runs. It is real evidence, **not a controlled comparative timing result**.
- CSDA B revisions (compact tables, theoretical figures, one-worker 48-row pilot, NGSIM figure) are on **open PR #109**, branch `paper/csda-computational-theory`, not necessarily in main. Do not assume unpublished branch content is already merged.
- Experiment010 runner is on the open nested research PR stack **#100 → #101 → #103 → #104 → #105**. Other agents own those branches. The directly archived **matched** `n=64,d=1,BIC` single-worker 48-row run is on `results/experiment010-uncapped-PCAG103A-08-20261103T222938857Z-shard0-offset20`, source SHA `f16f2bab6cfa37c6423c7f2d4554208efa9f683a`. Only one configuration and two repeats; do not identify a universal optimal boundary.
- This Springer preparation lives on branch `paper/springer-implementation-experiment011`, with **Experiment011** as the new source-controlled *targeted* follow-up. It deliberately invokes the **already present** mainline Experiment006 full-criterion evaluator instead of copying or merging open Experiment010 runner branches. Any future adoption of those research APIs requires separate PR review.
- The NGSIM manuscript's original data/provenance, its five tracked vehicle segments, and its training/holdout pipeline remain unchanged. Reuse figures with attribution; do not relabel them Springer algorithm validation.

## Non-overlap policy for publication

A data set or formula can appear in multiple manuscripts when necessary, but the *question answered* and the *claims of novelty* cannot be duplicated. Explicitly cross-reference the other manuscripts and label reused material as prior or contextual. An 85-digit precision result belongs primarily to CSDA A; theoretical work bounds belong primarily to CSDA B; **measured** matched, end-to-end criterion timings belong primarily to Springer; physically evaluated third-difference extrapolation belongs primarily to NGSIM.

The Springer paper may briefly define normalized smoothness and cite Guerrero (2007/2008), Cortés-Toto et al. (2017), Weinert (2007), and Biessy (2026), but must not claim those existing algorithms are new. Main novelty must be tested **reproducible workflow, implementation tradeoffs and empirical criterion-specific decision boundaries**, if the data support that conclusion.

## Springer evidence acceptance gates

1. **Same statistical workload:** identical \((n,d,M,R,\mathcal C,\mu,\text{data},\text{seed})\), grid values and exact endpoint convention across backends. Conditional plug-in `mu=data` is not fully re-estimated LOOCV.
2. **Complete pipeline:** report preparation, S-to-lambda inversion, factorization, selected-inverse/EDF/leverage, score evaluation, total cold and warm times, and peak memory when available. Fit-only methods and hybrids must be named honestly.
3. **Numerical QA before winners:** record failed/undefined/timeout/memory-skipped and unavailable dependencies; compare selected smoothness across methods and score parity where scores share a common normalization. For Gaussian profiled ML the banded and spectral implementations can differ by a *lambda-independent offset*, so only minimizers or separately normalized scores should be compared.
4. **Controlled timing:** isolated one-worker and one BLAS thread for latency; randomized or rotated paired execution blocks and an idle machine. An 8-worker pool measures throughput of multiple independent tasks, not eight-way speedup of one Cholesky factorization.
5. **Independent repetitions:** report raw per-repeat observations and paired dispersion; bootstrap intervals only when there are enough independent blocks. Do not report confidence intervals based on overlapping rows or two repeats as though they were independent.
6. **Feasibility:** dense \(n=131072\) requires 128 GiB per float64 matrix before workspaces. Record resource guards, never time attempted OOM as a completed run.
7. **Archival:** commit runnable scripts, config plan, raw CSVs, status rows, environments, machine description, figures, QA and PDFs. Numerical results from an ephemeral VM must be pushed to a separate results branch; do not leave them only in chat or Actions artifacts.

## Agent ownership

Read `paper/SPRINGER_AGENT_BRIEF.md` for independent roles, non-overlap boundaries, checkpoints and handoff format. Experiment owner instructions live in `paper/benchmarks/experiment011/AGENTS.md`. All agents must inspect current branches/PRs and source before changing files, use their own branch, and **never merge without explicit user approval**.

The canonical decision log and status ledger is `paper/SPRINGER_READINESS.md`; future agents must update it when data or claims change. This avoids repeating a broad expensive factorial or treating a planned matrix as a completed study.
