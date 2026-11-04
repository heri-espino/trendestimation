# Publication map — source of truth for all TrendEstimation agents

**Status:** research drafts and separate submissions; no journal acceptance or submission is implied. Updated 2026-11-03. Read this before creating an experiment, editing a manuscript, or merging a paper PR.


**Full timing design clarification:** The author requests the *entire*
original 252,000-cell Experiment008 factorial as the target tensor
(n=7 sizes, d=1..6, mean=0/data/0.15, low/high amplitudes,
5 criteria, 10 complete pipelines, 2 direct/mapped coordinate
modes, and 2 single-S workloads plus 2 grid workloads at
M=100/1000/10000/100000). The one-S cells occur only once per
base configuration, not four times. Experiment011's 21 cases
are a **pilot subset**, not the definitive tensor. Its
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
