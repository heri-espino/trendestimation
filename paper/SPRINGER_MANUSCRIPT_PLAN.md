# Springer Computational Statistics — planned implementation article

**Canonical LaTeX:** `paper/main.tex` using the repository's official Springer `sn-jnl` class. This document is an authoring plan, not a separate conflicting manuscript. Do not replace it with `paper/computational-statistics-submission/main.tex` (historical SN Computer Science), and do not swap in the Elsevier CAS style.

## Differentiated submission objective

**Provisional retitle after evidence review:** *Reproducible computational profiles of smoothness-indexed penalized least squares: complete criteria, caching and backend selection.*

Question: With exactly matched normalized smoothness candidates and numerical requirements, how does the **total work actually timed** depend on series size \(n\), difference order \(d\), candidates \(M\), repeated series \(R\), criterion \(\mathcal C\), reference-mean policy, backend and cache policy?

The paper's distinctive contribution must be a reproducible **implementation-and-measurement** study: reusable source, platform/BLAS controls, full-criterion scoring, failure/feasibility profile, and empirical choices. It must not claim the complexity theorems of CSDA Paper B as newly proved here, or forecast accuracy from the NGSIM paper as runtime evidence.

## Intended section-level restructuring of existing `paper/main.tex`

1. **Introduction and prior art:** brief model and normalized index (cite Guerrero 2007/2008, Cortés-Toto 2017, Weinert 2007, Biessy 2026). Explain why *complete criteria* and real execution time are different from one fitted trend. Contrast with CSDA Paper B (theory) and A (precision) without duplicate originality claims.
2. **Software contract and exact endpoints:** the common objective \(\|y-\tau\|^2+\lambda\|D_d\tau-\mu1\|^2\), shared grid including true \(S=1\), conditional \(\mu=\operatorname{mean}(D_dy)\), BIC boundary, and criteria CV/GCV/AICc/ML (with MLE offset caveat). Cite theorem source rather than republishing its full proof.
3. **Implemented complete pipelines:** naive dense inverse (reference), full spectral SVD, banded Cholesky plus exact selected inverse, and optionally separately labeled CHOLMOD+banded trace. Report real factor-cache and per-candidate diagnostics; do not conflate fit-only PCG/LU with full CV/ML.
4. **Experimental protocol:** cite `paper/benchmarks/experiment011/{cases.json,campaign.py,verify.py}`; n,d,M,R,C,means/scale; seeded paired blocks, rotated method order, BLAS threads, resource budgets, hardware, software; define full cold-attributed and warm time precisely and identify mapper setup.
5. **Validation / eligibility:** scores selected on identical \(S\) grids; numerical parity and independent high-precision checks; statuses `ok`, numerical failure, undefined criterion, ineligible memory/runtime, missing optional dependency. Denominator for win rates is all attempted or eligible cells as explicitly stated.
6. **Measured results:** only rows backed by a committed raw CSV and source SHA. At minimum show a paired **CV vs GCV** n/M crossover plot, cold/setup/warm breakdown, cross-series cache effect, and memory feasibility. Show confidence interval over independent measurement blocks only when appropriate.
7. **Limitations:** algorithmic complexity alone cannot establish milliseconds; sample machine/OS/concurrency matters, and the bootstrap intervals do not create independent hardware replications. `mu=data` conditional LOOCV is not refit CV; BIC near S=0 is ill-posed; S-grid inversion can dominate.
8. **Conclusions and reproduction:** bounded method-choice table specific to measured workload, and a deterministic reproduction command. Explain how to repeat the experiment without requiring the full 50,400-slot Experiment010 tensor.

Preserve all existing `paper/sections/*.tex` and figures until they are individually audited. The existing 36-page Springer PDF is an archived draft; do not delete or disguise the mixed-concurrency comparison included in main until a validated replacement is prepared.

## Figure and table schedule (all publication figures via AwesomeFigures)

| ID | Content | Source prerequisite | Current state |
|---|---|---|---|
| T1 | implementation inventory and full-criterion diagnostic accounting | Experiment006 source and verified method contracts | can draft, **not** a time ranking |
| T2 | full design, skipped/ineligible matrix, run machine and dependencies | Experiment011 plan + actual statuses | plan prepared; measured cells pending |
| T3 | paired \(n,d,M,R,C\) sample runtimes, cold/setup/map/score/warm | validated Experiment011 raw Windows blocks | pending |
| F1 | measured CV vs GCV complete-grid frontiers, confidence bands | validated independent blocks on the same machine | pending |
| F2 | per-candidate and full-grid amortization with setup split | validated matching n/d/C/M/R raw rows | pending |
| F3 | cost of direct-S inversion vs once-mapped lambda (same exact candidates) | both coordinate policies in Experiment011 | pending |
| F4 | memory/feasibility matrix and failed method status categories | full plan and actual outcome flags | pending |
| F5 | distinct throughput chart under 8-worker pool (optional) | separately run and identified multi-case throughput study | not measured |

The previously archived Experiment010 matched one-worker n64/d1/BIC case may provide a narrowly scoped introductory illustration; the main Springer's mixed-worker BIC table cannot be reused to claim matched speedups. The two-repeat matched pilot remains descriptive.

## Quantitative publication gates

- At least paired CV and GCV on identical n,d,method pools and work budgets, with three independent method-order-rotated blocks (two repeats each) on the Windows VM.
- Every actual time claim cites source revision, run machine, benchmark case, method, scenario and exact raw CSV; avoid silently borrowing timings from the CSDA manuscript.
- The actual `mean_total_s` and `median_total_cold_s` from inherited Experiment006 reflect its existing setup attribution rather than a truly isolated new OS process per repetition. If claiming true cold start is important, instrument a separately designed process-spawn experiment first.
- Report numerical accuracy independently from timing: float64 same selected criterion is a **parity check**, not a high-precision forward-error certificate.
- If too few valid paired cases exist, narrow the claims; do not extrapolate a universal crossover surface from a single machine and one BIC example.
- Compile via `.github/workflows/computational-statistics-paper.yml` only after changes to `paper/main.tex` have been reviewed, and modify the trigger to include the new publication evidence and analysis outputs.
- No unverified author email, funding, conflicts, or approval; no submission or merge without author authorization.

**Ownership and status:** see `paper/SPRINGER_AGENT_BRIEF.md` and `paper/SPRINGER_READINESS.md`.
