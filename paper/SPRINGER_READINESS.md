**LATEST Springer KKT numerical-methodology revision (2026-11-10; supersedes older PDF links below):** The canonical Springer `paper/main.tex` in draft [PR #126](https://github.com/heri-espino/trendestimation/pull/126) now rigorously derives the unconstrained first-order optimality equation from PLS, explains source-actual banded factorization -> solve -> residual check -> selected inverse/criterion pipeline, compares the implementation's scaled optimality residual to conventional normwise linear-system backward error, justifies residual-based acceptance with verified references (Boyd--Vandenberghe 2004; Higham 2002; Golub--Van Loan 2013; Stellato et al. 2020), and keeps the 1e-7 tolerance explicitly implementation-specific. A new vector figure, from the unchanged frozen tensor, shows exactly 9096 rejected banded method-level rows (CV 3384, GCV 4160, MLE 1552; median 1.4078566e-7) without inventing accepted-residual values. Algebraic regression suite **10/10 passed**. The **NEW 19-page Springer PDF** was freshly compiled on the correct PC08 Windows runner in successful [Actions 42769877846](https://github.com/heri-espino/trendestimation/actions/runs/42769877846), source SHA `15349249c1f5bcf518a5e4fd0eabbdc9c79cb28e`, PDF SHA-256 `69e5dc84936e1c7a6db4690373cc982baa1e26d5afc614f8006dfa2525751c29`, 808912 bytes, archived under [artifacts/springer-empirical-pc08-42769877846](https://github.com/heri-espino/trendestimation/tree/artifacts/springer-empirical-pc08-42769877846). No TeX errors, unresolved references or overfull boxes; all 19 pages extracted/rendered and visually inspected. Exact source-backed figures/QA: [kkt001/FINAL_VERIFICATION.md](benchmarks/experiment011/pc08_empirical/kkt001/FINAL_VERIFICATION.md). No benchmark rerun, source tolerance change, raw data modification, merge, or journal submission. Draft PR #126 remains unmerged, stacked on #124; author declarations still require confirmation.

**CURRENT Springer manuscript (Nov 9, 2026; supersedes older PDF links):** The requested complete figure/table redesign has been integrated in canonical `paper/main.tex`: eight revised vector figures (stacked method-color reliability and cost allocations; matched violin/box/seed distributions; paired full-grid numerical completion; high-order failure mechanisms; single-versus-grid crossover; memory-policy scaling) and three new scientific tables (geometric means and independent-seed CIs plus median/IQR; comment-classified KKT/inversion failures; nine-grid completion counts). All derive from the frozen, hashed Experiment011 tensor; **no new benchmark**. [Successful visual generation #42719614790](https://github.com/heri-espino/trendestimation/actions/runs/42719614790) published archive branch `results/experiment011-visualization001-42719614790`. [Successful final PDF build #42720035896](https://github.com/heri-espino/trendestimation/actions/runs/42720035896) is archived at `artifacts/springer-empirical-pc08-42720035896/paper/builds/pc08/springer-empirical-42720035896/springer.pdf`, source SHA `632a32300435348c3af1c351273d760f8da66f7a`, PDF SHA-256 `d2a91de05c4399560efab435804ade3373900d2f39c18be18374452054b84044`, 702329 bytes, 16 pages. 7 numerical ingestion tests passed, no LaTeX errors/undefined refs/overfull boxes, and all 16 pages rendered and inspected. Details: [visualization001/FINAL_VERIFICATION.md](benchmarks/experiment011/pc08_empirical/visualization001/FINAL_VERIFICATION.md). The journal's conditional recommendation of spectral SVD for repeated, memory-feasible complete-criterion searches is unchanged; retained KKT and mapping caveats. Unverified authorship declarations require confirmation. Draft PR #126 remains **open/unmerged** and stacked on unmerged handoff PR #124. Do not merge or submit without authorization.

**LATEST Springer journal-language revision (2026-11-09; supersedes all earlier PDF pointers):** The manuscript in [draft PR #126](https://github.com/heri-espino/trendestimation/pull/126) has been academically rewritten to recommend spectral SVD as the **conditional preferred default for repeated, complete-criterion PLS smoothing-parameter selection**, subject to numerical validation and dense memory feasibility. The title/abstract/introduction/theory/computational design/results/reliability/discussion/conclusions and all captions are formalized; public-facing figure 2 and Table 1 use mathematical configurations rather than internal case names; the memory figure's internal study labels are removed. Original data and original detailed failure masks remain unchanged. Source-linked journal-facing figure/table: [publication001](benchmarks/experiment011/pc08_empirical/publication001/README.md) and [journal editorial verification](benchmarks/experiment011/pc08_empirical/publication001/EDITORIAL_VERIFICATION.md). Successful publication figure PC08 run [42654092416](https://github.com/heri-espino/trendestimation/actions/runs/42654092416); successful corrected robustness plot PC08 run [42654215335](https://github.com/heri-espino/trendestimation/actions/runs/42654215335). **NEW journal revision compiled on PC08 run [42654369909](https://github.com/heri-espino/trendestimation/actions/runs/42654369909)**, exact source commit \`0579c831df81b821f1920358092c9b522511fbe1\`, 16 pages, 514672 bytes, SHA-256 \`462a4cfb82e4bb290d85e38034f1485ce0983460645d3f8729d2008cbae48745\`. The rebuilt PDF and build proof are permanently archived at [artifacts/springer-empirical-pc08-42654369909](https://github.com/heri-espino/trendestimation/tree/artifacts/springer-empirical-pc08-42654369909), path \`paper/builds/pc08/springer-empirical-42654369909/springer.pdf\`. Existing seven unit tests pass, final LaTeX pass has no undefined citations/references, errors or overfull boxes, and all 16 pages were downloaded, extracted, rendered and visually checked; text has no "pilot", "smoke", Experiment011 or GitHub Actions mentions. This version removed an **unverified proposed coauthor attribution** pending actual author agreement; no claim about coauthor exclusion is made. Verify actual author roster, corresponding email, funding/conflicts and original raw-data access before submitting. The draft PR remains unmerged and no numerical experiment was rerun.

**LATEST Springer empirical robustness/PDF certification (2026-11-09; supersedes older 11-page PDF records below):** In draft [PR #126](https://github.com/heri-espino/trendestimation/pull/126), the canonical Springer \`paper/main.tex\` now contains the explicitly requested Cholesky KKT/grid reliability, matched single-vs-grid speedups and memory-policy discussion, illustrated by four additional vector figures (Figs. 5–8). The frozen Experiment011 source shows 9096 banded post-solve KKT rejection rows; nine 97-seed families succeeded for single-candidate both methods and on full grid for SVD, but banded full grid failed; 6336 inversion-error rows involve both methods. All counts are correlated timing/status rows, not independent failure events or high-precision certificates. The source-code 2 GiB cap with 40n² SVD allowance versus 16n(d+1) for two band buffers is explicitly *not observed RAM*. Figures/CSV/JSON generator and outputs are archived on [results/experiment011-robustness001-pc08-42642807292](https://github.com/heri-espino/trendestimation/tree/results/experiment011-robustness001-pc08-42642807292), with successful [PC08 run 42642807292](https://github.com/heri-espino/trendestimation/actions/runs/42642807292). The **NEW 15-page compiled PDF** is on [artifacts/springer-empirical-pc08-42643291205](https://github.com/heri-espino/trendestimation/tree/artifacts/springer-empirical-pc08-42643291205), [successful PC08 build 42643291205](https://github.com/heri-espino/trendestimation/actions/runs/42643291205), SHA-256 aad05992ae19f4d5db9c7c2ec1e1a4fcc67bb086c3465a645b472b70a4a859a8, 529793 bytes. Seven tests passed, final TeX pass was free of undefined references/citations and overfull boxes, and all 15 pages and new figures were downloaded/rendered/visually reviewed. Read [robustness001/RESULTS.md](benchmarks/experiment011/pc08_empirical/robustness001/RESULTS.md) and [robustness001/FINAL_VERIFICATION.md](benchmarks/experiment011/pc08_empirical/robustness001/FINAL_VERIFICATION.md). Raw files untouched; no new campaign, merge, journal submission or author-approval claim.

**Experiment011 robustness001 augmentation (2026-11-09; latest):** User requested explicit Cholesky failure locations and diagrams. Read [robustness results](benchmarks/experiment011/pc08_empirical/robustness001/RESULTS.md) and source [render.py](benchmarks/experiment011/pc08_empirical/robustness001/render.py). Frozen, unchanged Experiment011 tensor shows **9096 banded post-solve KKT rejection timing rows** (the implementation threshold is 1e-7), **2112 banded and 4224 spectral inversion-error rows** and 970 work-budget skip rows (776 naive/194 spectral; *not* recorded OOM). Nine case families, each with 97 seed indices, have 100% single-candidate status completion for both backends, but 0% full-grid Cholesky completion versus 100% SVD full-grid completion. Large n=1024/2048/4096,d=4 shared smoothness-inversion failures preclude any universal SVD-success claim. The spectral evaluator does **not** apply the identical banded KKT test: acceptance success is not a comparable high-precision accuracy certificate. SVD 5×float64-dense-matrix memory allowance 40n² bytes versus approximately 16n(d+1) for two banded arrays, under the explicit 2GiB dense-memory policy; this figure is a *code-policy model*, not observed RAM. New Figs. 5–8 and derived CSV/JSON ledgers generated and archived on [results/experiment011-robustness001-pc08-42642807292](https://github.com/heri-espino/trendestimation/tree/results/experiment011-robustness001-pc08-42642807292) with [PC08 Action #42642807292](https://github.com/heri-espino/trendestimation/actions/runs/42642807292). The same draft manuscript PR [#126](https://github.com/heri-espino/trendestimation/pull/126) is open and unmerged, stacked on PR #124. Figures and prose are included in the canonical sn-jnl manuscript; a **new PDF compile is requested**, and the older PDF from #42638070663 remains historical. Do not merge, alter tolerances, or rerun large experiments.

**Open draft manuscript PR #126 (do not merge):** https://github.com/heri-espino/trendestimation/pull/126 . It is stacked on the still-open PR #124 handoff branch; retarget after integration/review, do not merge or submit without approval. The newly built PDF source revision and verified artifact remain unchanged by these documentation-only updates.

**Final Springer build certification (2026-11-09):** The rewritten empirical paper compiled successfully on PCAG103A-08 in [Actions #42638070663](https://github.com/heri-espino/trendestimation/actions/runs/42638070663), using source revision 41e876224db79b79684df7bd9bbcf3a9fa6acb8c. The **new 11-page PDF** (409,890 bytes, SHA-256 7027b90867aad9bbeb431e9a4c6cb23ec79c26092686c4ea89e3dce9f27fee44) and final TeX logs/proofs are permanently on [artifacts/springer-empirical-pc08-42638070663](https://github.com/heri-espino/trendestimation/tree/artifacts/springer-empirical-pc08-42638070663). Seven regression tests passed. The PDF was downloaded, SHA-256 verified, rendered as all 11 pages and visually inspected (including table, all figures, references). Final TeX pass has no unresolved refs/citations or overfull boxes. See [FINAL_VERIFICATION.md](benchmarks/experiment011/pc08_empirical/FINAL_VERIFICATION.md) and [repaired derived evidence](https://github.com/heri-espino/trendestimation/tree/results/experiment011-springer-derived-42636962129). The manuscript remains **unmerged and unsubmitted** pending author/coauthor approval.

**Empirical completion and numerical audit (2026-11-09; supersedes older pending statements):** The accepted Experiment011 report records **2813/2813 distinct case-seed jobs**, but **57 processes failed**. Original and same-disk backup report SHA-256 agree (c5d4898c83c731ada23a10957f80adc43616200206dc76573f365d38ba37f723). Six checkpoint stages contribute **2272 + 11 + 55 + 0 + 0 + 475** canonical records. Manifest-driven audit found **92,679 rows, 76,220 complete status-admissible timing rows, 16,459 exclusions** (11,208 numerical failures; 4224 mapping; 970 budgets; 57 missing-input jobs with 60 individual files missing). The matched $n=256,d=3$, data-derived-mean CV case changes banded/SVD ratio **0.698 (0.671–0.724)** at a single candidate to **4.846 (4.567–5.125)** for 100 candidates, using 97 seed clusters. High-order full grids are often numerically incomplete and cannot win timing comparisons. Execution phases 24/1/12 stay distinct; these are not isolated latencies or precision certification. Preflight [42633415411](https://github.com/heri-espino/trendestimation/actions/runs/42633415411), repaired analysis [42636962129](https://github.com/heri-espino/trendestimation/actions/runs/42636962129) and [archive recovery 42637443986](https://github.com/heri-espino/trendestimation/actions/runs/42637443986) are complete. The approved repaired evidence is archived at [results/experiment011-springer-derived-42636962129](https://github.com/heri-espino/trendestimation/tree/results/experiment011-springer-derived-42636962129); an older empty Fig. 2 from analysis 42634293076 is superseded. Analysis code, vector figures, PNGs, tables, 700-replicate seed bootstrap, and claim-to-data ledger are preserved. Seven source-level tests passed on PC08. The canonical paper/main.tex has been rewritten with Springer sn-jnl and a new PDF compilation is pending final inspection on the scoped manuscript branch. All declarations and submission remain unapproved; no merge.

# Springer Computational Statistics — readiness and decision ledger

**Experiment011 completion update (2026-11-09):** The author reports **2813/2813 case-seed jobs recorded, remaining 0**, on the Windows VM. Read the [completed-campaign handoff](benchmarks/experiment011/handoff/COMPLETION_HANDOFF.md) and [Springer analysis prompt](benchmarks/experiment011/handoff/SPRINGER_ANALYSIS_AGENT_PROMPT.md) before following older pending-run instructions. Final raw data acquisition, verified backup and numerical/timing analysis remain pending; GitHub still has only the inspected 2338-job checkpoint. Preserve local raw files and use the documented no-automatic-publication backup procedure. These observations include 24/1/12-worker phases and must not be pooled as isolated-latency measurements.

**Editorial proposal (2026-11-04):** [Draft PR #112](https://github.com/heri-espino/trendestimation/pull/112) tightens the archived-timing claims in `paper/main.tex` and documents manuscript-level source and mathematical checks in [EDITORIAL_LITERATURE_AUDIT.md](EDITORIAL_LITERATURE_AUDIT.md). It adds **no new Windows Experiment011 measurements**, runtime rankings or publication authorization. The 29-case study and its evidence gates below are unchanged.

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


**Owner of this ledger:** independent review agent (see `SPRINGER_AGENT_BRIEF.md`). This is the authoritative checklist; keep it updated with exact commit hashes, source branches and measurable findings. Do not infer a result from the existence of a manifest or a successful smoke test.


**Preserved historical full-factorial index (not the active Experiment011 run schedule).** The archived coverage
extends beyond the currently approved 29-case staged study: seven n values through
131072, d=1..6, zero/fixed-nonzero/observed-difference means,
low/high magnitudes, five criteria, all ten full-criterion
pipelines, both direct and mapped smoothness coordinate policies,
four one/grid × one/multiple-series workloads, and M in
{100,1000,10000,100000} on grid workloads. Deduplicating
single-S work gives **252,000 planned cells**, not yet measured.
`paper/benchmarks/experiment011/full_plan.py` generates
an auditable compressed index with resource skip statuses
by invoking the existing Experiment008 plan; it never runs
the full experiment. The active 29 cases remain the targeted
study, and Experiment008/009/010 real prior records
must be reconciled before computing a new result.
The end goal is paired runtime per backend versus
naive inversion (where feasible) with repeated block-level
mean/median, dispersion and theory comparison; **no RMSE**.


## Historical editorial state at initial setup (2026-11-03)

This table preserves the original 21-case setup evidence; current 29-case
status and the pending Windows run are in SESSION_HANDOFF.md and the latest
focused-design entry below. Historical counts are not current plan totals.

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


**Tensor analysis implementation now available.**
`paper/benchmarks/experiment011/analyze.py` reads preserved
actual `runs/<tag>/<case>/blockNNN` folders and generates
a sparse long-form timing tensor, baseline-paired naive speedups,
per-cell independent-block means and bootstrap intervals
(with >=3 distinct seed blocks), plus source/host/BLAS-qualified
Big-O class descriptions. It never fills infeasible cells with
invented times and never computes RMSE. CI runs this analyzer
on a small hosted smoke before the Windows campaign.
The full 252,000-row resource-status plan and the measured
long-form table are **separate** data structures.


## Specific scientific questions for Springer

1. **CV versus GCV:** Does the complete leverage/residual requirement alter SVD-versus-banded-Cholesky crossover, controlling n,d,M,R,mu and hardware? Theoretical expectation is conditional; actual crossover is a measured result only after pilot data.
2. **Candidate-density amortization:** When does one retained SVD plus repeated scalar scores overcome the lower per-candidate banded operation count? Report setup separately from full cold/warm grid time; include endpoint S=1 as the exact limit.
3. **Caching and repeated series:** For repeated series with the same n,d,S, does factor/trace reuse change complete-criterion selection times? The existing evaluator caches factors under a memory budget; compare its two policies and four workloads without asserting it always retains all M factors.
4. **Numerical admissibility:** At high d and mu=data, do finite precision, memory limits, or criterion undefinedness remove a nominally fast pipeline? Compare high-precision or independent reference where feasible.
5. **CHOLMOD vs canonical banded Cholesky:** The implemented `sparse_cholesky_banded_trace` is a hybrid requiring another diagnostic factorization. Report its `fit + diagnostic` cost, not a pure CHOLMOD speed.

## Original staged design (historical; current 29-case extension below)

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

## Historical initial preparation verification (21-case version)

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

## Complete-factorial manifest and measured-tensor parser verified

- Full requested factorial (not measured): [GitHub Actions #41780451438](https://github.com/heri-espino/trendestimation/actions/runs/41780451438) completed successfully after adding `full_plan.py` and `analyze.py`.
- Verified compressed full-factorial plan `paper/benchmarks/experiment011/plans/full_factorial_plan.csv.gz`: exactly **252,000** planned method/workload/coordinate cells, with 138,960 preflight eligible, 92,640 work-budget exceeded, 16,800 dense-memory infeasible and 3,600 naive-runtime infeasible at the currently chosen budgets (2 GiB, 5e8 nominal work, six planned repeats). These are **preflight classifications**, not observations or failure rates.
- Hosted smoke analysis `paper/benchmarks/experiment011/analysis/gha_41780451438/`: 24/24 actual successful numerical timing rows, 24 aggregate cells and **16 genuinely paired naive-baseline ratios**; one independent block, so **zero confidence intervals** and no crossover inferred. Source executable SHA `cad1b3bf7c37a013ccd8593a02a1d4d9f60ff989d8185bdbc479017087d35f89`, hosted GitHub Linux runner (not PCAG103A-08).
- Unit tests verify the exact factorial axes, float64 parity, invalid/skip statuses, paired naive ratios, no confidence interval with one block, and duplicate-seed prevention.
- **Still missing for the active study:** matched Windows observations for the approved selected Experiment011 cases, independent blocks for CV/GCV comparisons, high-order numerical checks, empirical scaling figures, and journal author review. The historical factorial is not a pending execution requirement.

## Current focused design and multiprocessing verification (November 4, 2026)

**Author approval supersedes the earlier full-factorial execution target.**
Experiment011 now has 29 active cases (2 smoke, 15 pilot, 12 confirm).
The only changes to the initial 21 cases are eight targeted CV/GCV
comparisons at d=4 for n=256,1024,2048,4096. The 1024-point
confirmation uses an explicit 750-million-unit per-case work cap
for both SVD and banded Cholesky on the full M=100,R=3 grid.
For n=2048 and 4096, banded-only time is retained and labeled
`single_backend_timing_only_no_parity_reference`—never a
cross-method numerical certificate. The older Experiment008
252,000-cell index remains archived, not a requested execution set.

The *optional* separate `campaign.py parallel-series` mode
supports independent small series only (n<=256, M<=1000),
R<=32 and up to 32 Windows spawn workers, one BLAS thread each.
It writes `runs_parallel/`, not the serial `runs/` tensor.
Each process has private mapper/factors; report its
per-method/repeat wall time as **parallel throughput**,
never mix it with serial shared-cache latency.

**Verified hosted smoke:** [Actions #41796045403](https://github.com/heri-espino/trendestimation/actions/runs/41796045403) passed tests, generated the
checksum-versioned 29-case plan, and recorded **36/36 successful
per-series rows, 24 float64 paired comparisons, zero issues**
using 2 worker processes. This is Linux hosted QA, not measured
32-worker Windows performance. Windows d=4 measurements and
large-n confirmations are not yet executed.
