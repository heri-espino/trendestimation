# Paper C live continuation reconciliation — 2026-11-20

**Purpose:** A dated, docs-only continuation of [the comprehensive 2026-11-18 handoff](NEXT_AGENT_COMPREHENSIVE_HANDOFF_2026-11-18.md). This records newer *verified live GitHub state* without modifying, replacing, or rerunning any scientific experiment. For experimental methods and original archive provenance, read the comprehensive handoff first.

## Live integration and current publication

At this inspection, `main` was `29c7d71f6ae83241c1b650e19d3dc9ae3c58cf48`. Its [push CI run #44492112137](https://github.com/heri-espino/trendestimation/actions/runs/44492112137) passed Python 3.10, Python 3.12, and documentation jobs. The most recent main commit was an unrelated **Springer** Experiment013 protocol integration; it was not new Paper C data.

**Paper C on main is now the 15-page manuscript, not the 14-page manuscript described in the November 18 handoff.** [PR #150](https://github.com/heri-espino/trendestimation/pull/150) merged the primary-source-verified state-of-the-art revision on 2026-11-19. Its guarded [PCAG103A-08 build #44485951302](https://github.com/heri-espino/trendestimation/actions/runs/44485951302) records:
- Canonical `paper/ngsim-jerk-case-study/main.pdf`: **15 pages**, SHA-256 `b0a6ed86acbfda78f3ed9dfa7e56384140ec65526cabfa42d1bfd30f60a4922d`, 51 BibTeX entries, all 15 pages visually inspected *by the producing agent according to its archived audit*.
- Canonical `atlas_supplement.pdf`: **12 pages**, SHA-256 `1f11e85758ea82130359e76f1c463a944d27765d5fb6a9e8f45bb12e38a9345b`, unchanged from the November 14 final integrated AwesomeFigures atlas.
- Immutable 15-page PDF, source and page-preview archive: [`results/paper-c-pdf-pc08-44485951302-a1`](https://github.com/heri-espino/trendestimation/tree/results/paper-c-pdf-pc08-44485951302-a1/paper/builds/pc08-paper-c-44485951302-a1).
- Immutable older 14-page atlas-era build: [`results/paper-c-awesomefigures-pc08-43631207424-a1`](https://github.com/heri-espino/trendestimation/tree/results/paper-c-awesomefigures-pc08-43631207424-a1/paper/ngsim-jerk-case-study/visuals/runs/awesomefigures-43631207424-a1). Both historical versions must be retained.

The 2026-11-19 revision added nine verified literature entries (42 to 51) and strengthened the distinction between NGSIM positional reconstruction, constrained vehicle dynamics, independently sensed driver-intended jerk, correlated-error smoothing, classic REML, and modern interpolation/neural reconstruction. See [the source-to-claim review](SOA_JERK_PRIMARY_SOURCE_REVIEW_2026-11-19.md). Manuscript entrypoint: `main.tex` and its six `sections/*.tex`; illustration inventory: `FIGURE_ATLAS.md` and `visuals/README.md`.

## Concurrent PR — not integrated into main

**[PR #152](https://github.com/heri-espino/trendestimation/pull/152), `paper/paper-c-normalized-smoothness-precision`, remained open** at this inspection (head `ae0f946666e2e09e03fff7c3784d866035556a09`). Its CI [#44490928506](https://github.com/heri-espino/trendestimation/actions/runs/44490928506) passed, **but GitHub reports `mergeable_state=dirty`, `mergeable=false`** against the then-current main. **Do not merge while conflicted; respect the owning agent and re-verify against the latest main before any integration.**

This PR proposes and already built a *separate, not-yet-canonical* **17-page** manuscript ([PC08 #44490200179](https://github.com/heri-espino/trendestimation/actions/runs/44490200179), SHA-256 `409096cb0a9d75195c60da263070a27ec109db779b8f3d007a84ae77ca0357c3`) with original-source normalization/relative-precision clarification. The [branch's mathematical audit](https://github.com/heri-espino/trendestimation/blob/paper/paper-c-normalized-smoothness-precision/paper/ngsim-jerk-case-study/notes/NORMALIZED_SMOOTHNESS_RELATIVE_PRECISION_PRIMARY_SOURCE_2026-11-19.md) distinguishes the historical **n-normalized** Guerrero index `S_G` (limiting value `1-d/n`) from Paper C's existing **(n-d)-normalized** `S` (limiting value `1`), with `S = n S_G/(n-d)`, and distinguishes relative precision from absolute sensor precision. This revision **must not be represented as merged or incorporated into the 15-page main PDF**.

## Frozen experimental scope and inferential units

| Paper C experiment | True sampling target and preserved run |
| --- | --- |
| 004 | 200 real camera-recorded FHWA NGSIM episodes, 100 per site, 113 distinct site/ID pairs across only five coarse recording blocks. No independent physical jerk. [PC08 #42538556206](https://github.com/heri-espino/trendestimation/actions/runs/42538556206). |
| 005 | 1,296 independent synthetic confirmation trajectories (plus separate 96-trial pilot), with prescribed clean positions and *known finite-difference* jerk. [Cloud #42547883064](https://github.com/heri-espino/trendestimation/actions/runs/42547883064); also independently executed on Windows [#42547250403](https://github.com/heri-espino/trendestimation/actions/runs/42547250403) using the same specified seed streams. |
| 006 | New reference-mean/REML fits reusing **exactly the same** 1,296 synthetic and 200 real episodes; no new independent sampling units. [PC08 #42639588117](https://github.com/heri-espino/trendestimation/actions/runs/42639588117). |
| 007 | 1,944 paired noise/jerk calibration *conditions* from **72 independent stochastic parent draws**, with 27 treatments per parent, and four selection methods. The Linux/Windows executions use the same seeds, not additional independent parents. [PC08 #42660204414](https://github.com/heri-espino/trendestimation/actions/runs/42660204414). |
| 008 | Five historical physical smoothers on those same Experiment005/006 and Experiment004/006 cases; genuine hard TSVD versus soft PLS, not solver-speed comparison. [PC08 #42717662044](https://github.com/heri-espino/trendestimation/actions/runs/42717662044). |

**Nonnegotiable statistical distinctions:** `D_3=(-1,3,-3,1)`, `\Delta t=0.1 s`; `\mu` is meters per discrete third difference and `\mu/(\Delta t)^3` is the reference discrete-jerk proxy (m/s³). The fixed-reference estimator solves `(I+\lambda D_3^T D_3)\widehat\tau=y+\lambda\mu D_3^T 1`. The existing rank-normalized index `S(\lambda)=\sum_{j=1}^{n-3}\lambda\delta_j/(1+\lambda\delta_j)/(n-3)` gives fixed-\mu effective degrees of freedom `n-(n-3)S`. Data-selected reference or penalty changes complete-estimator complexity. The Gaussian covariance-noise interpretation is model-conditional, not an absolute position-sensor precision claim.

**Key archived findings remain unchanged:** synthetic known-discrete-jerk RMSE (m/s³): PLS 2.441257, nominal-EDF-matched TSVD 2.941621, conditional-GCV TSVD 250.718104; paired design-conditional TSVD-minus-PLS RMSE difference 0.500364, 95% bootstrap interval [0.322681, 0.713368]. Correctly specified Gaussian calibration: joint-REML selected-S Spearman about 0.9654, MAE 0.01148; correlated errors degrade calibration. Real one-second *cumulative-window recorded-position* RMSE: PLS 0.514386, nominally matched TSVD 0.511776, GCV spline with the common last-three-point rule 0.494562; **separate** spline + quadratic Taylor end-to-end benchmark **0.348043 m**. The spline advantage must remain visible and must not be attributed solely to the smoother when the continuation rule differs.

Ten AwesomeFigures atlas groups (each PDF/SVG/PNG) and eight restyled preexisting groups are complete; all have frozen-input hashes. `visuals/render_awesomefigures_atlas.py` calls `AwesomeFigures==0.1.0` native APIs. Do not fabricate new observations, reselect old TSVD ranks, rerun Experiments004–008, or republish frozen archives as new experiments.

## Safe continuation and validation

Canonical workflow files `.github/workflows/paper-c-manuscript-pc08.yml` and `paper-c-awesomefigures-atlas-pc08.yml` are **manual-dispatch only**, guarded by the intended Windows runner and exact source SHA. On `main` the atlas must archive only to a uniquely named results ref. Source branch publishing is limited to scoped Paper C branches and an unchanged branch head. The active `publication_sha256.txt` tracks exactly 16 canonical files; `publication_sha256_legacy_pre_atlas.txt` remains historical.

Read `AGENTS.md`, `paper/AGENTS.md`, the original comprehensive handoff, the current six manuscript sections, Experiment004–008 README/ledgers and visual manifests before editing. Fast safe checks on a full checkout (do **not** run the expensive science):

```sh
python paper/ngsim-jerk-case-study/check_publication_hashes.py --check
python -m pytest tests/test_paper_c_publication_maintenance.py tests/test_paper_c_experiment007.py tests/test_paper_c_experiment008.py tests/test_paper_c_plug_in_edf.py tests/test_paper_c_frozen_svd_audit.py -q
```

For a substantive update, create a fresh scoped branch from live main, preserve raw inputs and unfavorable results, run the appropriate targeted tests plus green Python 3.10/3.12/docs CI, do a guarded manual Windows source-matched PDF build with individual-page visual checks and immutable archive, update the publication hashes only after actual compiled-file changes, open a PR, resolve conflicts and required checks, then merge under the author's **standing routine-merge authorization** and verify post-merge CI. Never journal-submit without separate explicit permission. Authorship/affiliation/order and declarations remain provisional.

**Audit provenance:** GitHub live refs and original repository source, notes, tests, workflows, run ledgers, publication SHA ledger and PR metadata were inspected. The agent **did not directly render the binary PDFs in this session**; page-count/visual status is sourced from the cited audited Windows builds. This docs-only reconciliation executed no experiment, figure renderer, compilation or manuscript submission.
