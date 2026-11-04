# Springer Computational Statistics — readiness and decision ledger

**Owner of this ledger:** independent review agent (see `SPRINGER_AGENT_BRIEF.md`). This is the authoritative checklist; keep it updated with exact commit hashes, source branches and measurable findings. Do not infer a result from the existence of a manifest or a successful smoke test.

## Editorial state at setup (2026-11-03)

| Gate | Status | Evidence / gap |
|---|---|---|
| Springer template and historical draft | **compiled** | `paper/main.tex`, 36-page main-branch PDF built by GitHub Actions; its existing narrative is broader than the newly agreed implementation focus |
| Four-paper publication boundaries | **documented** | `paper/PUBLICATION_MAP.md`; theoretical CSDA B is **open PR #109**, not merged |
| Original older factorial | **archived / partial** | Experiments006–010 retained; do not relabel unexecuted factorial as completed |
| Experiment010 measured n64/d1/BIC three-way **mixed concurrency** | **verified limited** | `paper/benchmarks/experiment010/publication_evidence/` contains 48 rows, but different simultaneous worker counts. Springer main-branch table is descriptive only |
| Experiment010 measured n64/d1/BIC **matched serial comparison** | **archived / limited** | `results/experiment010-uncapped-PCAG103A-08-20261103T222938857Z-shard0-offset20`, 48 rows, 1 worker and 1 BLAS thread. Two repeats; no general scaling inference |
| Experiment011 deterministic experiment plan | **generated and committed** | 21 cases; plan records 187 eligible and 5 budget-exceeded method/scenario preflights. These are planning statuses, not measured times |
| Experiment011 CI smoke | **passed, hosted (not Windows)** | [Actions #41767817861](https://github.com/heri-espino/trendestimation/actions/runs/41767817861): 24/24 rows `ok`, 16 paired float64 checks, zero issues; raw CSV, plan, QA and environment committed to this branch |
| Experiment011 Windows multi-criterion pilot | **not measured** | requires VM; use `runs/<machine-id>/` plus permanent results branch |
| Experiment011 cross-machine or multithread throughput | **not measured** | optional separate study, never blend with isolated-latency data |
| Numerical checks beyond float64 parity | **not complete** | CSDA A has high-precision references; specific high-order experiment011 cases require independent forward-error audit before any winner claims |
| Statistical analysis of crossover and uncertainty | **not measured** | need >= several independent, rotated, paired blocks per cell; bootstrap over independent blocks, exclude invalid |
| Updated Springer results tables/figures | **pending validated data** | use AwesomeFigures with Springer `sn-jnl` font/width, archive vector sources |
| Coauthor, correspondence, disclosures, novelty and submission approval | **not confirmed** | do not invent, submit or assert accepted |

## Specific scientific questions for Springer

1. **CV versus GCV:** Does the complete leverage/residual requirement alter SVD-versus-banded-Cholesky crossover, controlling n,d,M,R,mu and hardware? Theoretical expectation is conditional; actual crossover is a measured result only after pilot data.
2. **Candidate-density amortization:** When does one retained SVD plus repeated scalar scores overcome the lower per-candidate banded operation count? Report setup separately from full cold/warm grid time; include endpoint S=1 as the exact limit.
3. **Caching and repeated series:** For repeated series with the same n,d,S, does factor/trace reuse change complete-criterion selection times? The existing evaluator caches factors under a memory budget; compare its two policies and four workloads without asserting it always retains all M factors.
4. **Numerical admissibility:** At high d and mu=data, do finite precision, memory limits, or criterion undefinedness remove a nominally fast pipeline? Compare high-precision or independent reference where feasible.
5. **CHOLMOD vs canonical banded Cholesky:** The implemented `sparse_cholesky_banded_trace` is a hybrid requiring another diagnostic factorization. Report its `fit + diagnostic` cost, not a pure CHOLMOD speed.

## Predeclared staged design

**Stage 0 (safe smoke):** n64, d1, GCV, M100, numeric mu0; one block/one repeat, 3 core methods; no large experiment claims.

**Stage 1 (VM pilot):** n in {64,128,256}, d in {1,3}, M in {100,1000}, C in {CV,GCV,AICc,ML}, R in {1,3}, numeric mu0 plus a separately named conditional mu=data validation; limited selected cases rather than entire Cartesian product. Three blocks, two repeats per block and rotated method orders are target defaults, **not already-run observations**. Include both direct-S and mapped-lambda policies in every case.

**Stage 2 (after calibrated pilot):** selected n/d/criterion scaling for M up to 10000 and optionally 100000 where each backend's explicit memory/work preflight is feasible. Include n=512/1024 banded-vs-spectral cases only when measured pilot suggests practical; do not force dense at n=131072.

**Stage 3 (optional):** eight-worker throughput of many independent validated method–case workloads; schedule as a separate benchmark and report aggregate throughput and worker pressure. This is not the same as comparing isolated per-backend latency.

## Required outputs for every run

- `raw_times.csv`, `summary.csv`, `paired_speedups.csv`, `environment.json` from existing Experiment006 evaluator.
- `experiment011_case.json` with case specification, selected methods, block, actual process source SHA, original source hashes and stage.
- `experiment011_qa.json` with all statuses, finite-value coverage, same-pair selected-S discrepancies and score parity where meaningful; DO NOT promote a cell with warning/invalid.
- SHA-256 files/checksums and a machine run README documenting invocation and any contention.
- Git commit and push to an independent `results/experiment011-<machine-id>` branch. Link the actual branch/commit here.

## Review-before-submission checklist

[ ] Every methods table identifies **complete statistical criteria** versus fit-only timings.
[ ] Every speedup is derived from identical source cases, same CPU conditions, same M, same candidate values, and same number of series.
[ ] Show setup, mapping, candidate scoring, cold/warm totals, memory/skip diagnostics, and a clear comparison of CV with GCV.
[ ] Plot measured scaling with credible intervals only at valid paired independent repeats; label dates, hardware and BLAS versions.
[ ] Distinguish simulated input used for numerical performance from NGSIM observed data used for a different question.
[ ] Discuss BIC divergence at interpolation boundary and conditional plug-in mean, without describing restricted BIC as a repaired theorem.
[ ] Identify previously known results by Guerrero, Cortés-Toto, Weinert and Biessy; cite CSDA theory companion as a working manuscript only when appropriate.
[ ] All figures and PDFs are committed and pass reproducible PDF compilation.
[ ] All coauthors have approved manuscript, affiliation, contact information, funding/ethics statements and journal-specific policies.

**Do not merge** any Springer or Experiment011 PR until the review gates are explicitly met and the user authorizes it.

## Latest reproducible preparation verification

- **CI:** hosted GitHub Actions workflow #41767817861 finished `success`.
- **Immutable run:** `paper/benchmarks/experiment011/runs/gha_41767817861/smoke_gcv_n64_d1_m100/block000/`.
- **Source revision measured by that hosted run:** `c52291e77b6375c77e4aecfef55e2dd53362b0b7`.
- **Actual validation:** all 24 smoke records `ok`; 16 matched method comparisons of selected `S` and GCV score, no issues; float64 parity **only**, not an independent precision certificate.
- **Planned eligibility:** 21 case definitions; 187 eligible and five budget-exceeded method/scenario preflights from the inherited Experiment006 resource gate. These have **not** been measured.
- **Not done:** any Windows Experiment011 paired multi-criterion run; any multi-core throughput study; actual CV/GCV crossover, independent high-order precision certification, submission/revision of the main Springer manuscript.

**Next author action:** review the new preparation PR and use the Windows PowerShell commands in `paper/benchmarks/experiment011/README.md` to run selected pilot cases on a separate results branch. After validating their QA, update this ledger, run only confirmatory cases supported by the observed pilot, and prepare measured tables/figures.

## Coordination record — existing agents notified through PR conversations

- **Springer preparation:** [PR #110](https://github.com/heri-espino/trendestimation/pull/110), branch `paper/springer-implementation-experiment011`; not merged.
- **CSDA B:** a non-invasive coordination comment was posted to [open PR #109](https://github.com/heri-espino/trendestimation/pull/109) (comment ID `6621889147`) explaining that theoretical novelty remains in CSDA B and measured implementations belong to Springer. No code changes to that branch.
- **Existing Experiment010 runner:** a coordination comment was posted to [open PR #105](https://github.com/heri-espino/trendestimation/pull/105) (comment ID `6621890104`) preserving the nested PR stack, result archives and concurrency rules.
- **CI:** [hosted smoke #41767817861](https://github.com/heri-espino/trendestimation/actions/runs/41767817861) passed and committed its raw rows and source/QA manifest on this branch. Hosted Linux measurements are not a substitute for the planned Windows multi-criterion pilot.

Agents do not automatically execute work merely because these comments or files exist. Future agent sessions must explicitly read this ledger and claim nonoverlapping branches/file ownership before proceeding.
