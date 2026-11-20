# MASTER CONTINUATION HANDOFF — TrendEstimation Paper C (verified 2026-11-18)

> **Live reconciliation (2026-11-20):** Read [CONTINUATION_STATUS_2026-11-20.md](CONTINUATION_STATUS_2026-11-20.md) immediately after this historical handoff. Current `main` has the newer 15-page Paper C draft, compiled on Windows #44485951302 with 51 references; the 12-page AwesomeFigures atlas is unchanged. A separately compiled 17-page revision exists only in open PR #152, which GitHub reported as conflicted at the November 20 inspection. This addendum preserves all November 18 experiment/build history without silently replacing past scientific results or claiming the PR is merged.


**Maintenance addendum (2026-11-18):** The stale workflow branch restrictions and pre-atlas publication SHA-256 inventory have been corrected in a scoped maintenance PR. Both PC08 workflows are **manual only** and accept `main` or scoped Paper C branches; the atlas never publishes generated PDFs/figures directly onto `main`. The verified final 14-page and 12-page PDF hashes are recorded in the active 16-file `publication_sha256.txt`, while the former pilot manifest is preserved under `publication_sha256_legacy_pre_atlas.txt`. The check procedure is `python paper/ngsim-jerk-case-study/check_publication_hashes.py --check`. Full record: [PUBLICATION_MAINTENANCE_2026-11-18.md](PUBLICATION_MAINTENANCE_2026-11-18.md). Experiments004–008 remain untouched. The author's latest explicit standing authorization permits merging scoped, validated maintenance PRs, overriding older no-merge restrictions; journal submission remains prohibited without separate approval.


> **For the next AI research agent:** Read this document in full, then inspect the **live repository and all named files** before editing. This is a continuity record, not permission to rerun studies, merge old PRs, change scientific results, or submit to a journal. The original agent's context became long; the work itself is preserved in Git.

## 0. Immediate instructions / immutable decisions

Repository: https://github.com/heri-espino/trendestimation

Current canonical starting branch: **`main`** (verified through GitHub on 2026-11-18). This **supersedes old November 9–14 notes** saying Paper C PR #133 is still open or that Paper C is only on its review branch.

Canonical Paper C editable source:
- `paper/ngsim-jerk-case-study/main.tex` — two-column Elsevier CAS *research draft*, not an actual submission.
- `paper/ngsim-jerk-case-study/sections/{introduction,methods,synthetic_case,precision_calibration,real_case,discussion}.tex`
- `paper/ngsim-jerk-case-study/references.bib`
- Main compiled PDF: `paper/ngsim-jerk-case-study/main.pdf` on `main`.
- Supplementary TeX/PDF: `paper/ngsim-jerk-case-study/atlas_supplement.tex` and `atlas_supplement.pdf`.
- Figure gallery: `paper/ngsim-jerk-case-study/FIGURE_ATLAS.md`.

**Article identity:** Scientifically and physically motivated study of established third-order penalized least-squares (PLS) trend estimation for vehicle *finite-difference jerk*, with a nonzero reference third-difference mean, normalized smoothness index S, actual competing smoothers (hard truncated SVD, GCV natural cubic smoothing splines, Savitzky–Golay), two known-truth/calibration simulation studies, and 200 recorded FHWA NGSIM episodes. **NOT** a numerical timing/Cholesky-vs-SVD-backend article. No claim of newly invented PLS/WH filtering or universal forecasting superiority.

**Explicit preservation:** Experiments004–008 are completed and frozen. Do not rerun, regenerate clean trajectories, retune original estimators, redownload raw NGSIM, rewrite historic rows, or overwrite `results/*` archive branches. Only do a *new*, separately named, author-approved experiment if a genuinely unanswered scientific question requires it. Re-rendering figures/compiling LaTeX is acceptable if source integrity is checked.

**Collaboration rules:** Work from current `main` on a *new scoped branch*, document changes and submit a PR for review. Preserve all science/code/figures/PDFs and existing branches. Do not merge changes or submit to a journal without the user's explicit authorization. Do not merge old PR #131 or #132 just because GitHub still reports them open: the approved Paper C branch already reached main through #133.

## 1. Current verified repository and PR state — do not use stale November 9 status

Live GitHub metadata checked 2026-11-18:
- **PR #133** https://github.com/heri-espino/trendestimation/pull/133 — **MERGED into main**, merge SHA `06ab103d69e45ef2a32d9675bed7c82d48e4afb6` (2026-11-14). Former review branch: `paper/paper-c-scientific-editorial-review`. Its historical PR body includes older paragraphs claiming “still draft”; trust the actual merged flag.
- **PR #136** https://github.com/heri-espino/trendestimation/pull/136 — **MERGED into the #133 review branch**, merge SHA `ba066a703ca7ae5963dada68628e50676c300e25` (2026-11-14). Head: `feature/paper-c-awesomefigures-atlas`. That artwork then reached `main` via #133.
- **PR #131** https://github.com/heri-espino/trendestimation/pull/131 — still shown **open** in GitHub; historically supplied the genuine Experiment008 hard-truncated-SVD smoother and first method-first 11-page article. Do not discard that baseline, but do not re-merge its older stacked history.
- **PR #132** https://github.com/heri-espino/trendestimation/pull/132 — still shown **open**, a competing editorial rewrite with fewer TSVD comparisons; reference for organization only, not canonical.
- Final live publication navigator: `paper/LATEST_PAPERS.md` on **main**. Separate concurrent work: Springer computational/selection paper `paper/main.tex`, CSDA theory `paper/csda-unified-theory/main.tex`. Do not edit or merge other paper workstreams during Paper C handoff tasks.

**One crucial inconsistency:** `paper/ngsim-jerk-case-study/notes/SCIENCE_EDITORIAL_REVIEW.md` describes the November 14 visual merge first and still contains later-in-document *historical* claims that #133 was unmerged. Those are snapshots, not current state. This file supersedes those claims only with respect to integration status; mathematical and original-run details in that review remain useful.

## 2. Exact latest integrated scientific artifacts — AwesomeFigures completed

**Final successful Windows runner:** https://github.com/heri-espino/trendestimation/actions/runs/43631207424

- Main Elsevier CAS scientific manuscript: **14 pages**, SHA-256 `a61b70f081c48f3b98711e6d18fbd64f9f97a20772732093a08ec7c5ff56f22d`.
- AwesomeFigures illustrated supplemental atlas: **12 pages**, SHA-256 `1f11e85758ea82130359e76f1c463a944d27765d5fb6a9e8f45bb12e38a9345b`.
- Final **immutable** results-only build: `results/paper-c-awesomefigures-pc08-43631207424-a1`, within `paper/ngsim-jerk-case-study/visuals/runs/awesomefigures-43631207424-a1/`. Contains frozen input identities/hashes, ten additional exported triplets, eight restyled prior graphics, both PDFs, every page preview, environment snapshot, logs, figure/source and PDF-content audits.
- Earlier first atlas run (still archived): https://github.com/heri-espino/trendestimation/actions/runs/43630573121; earlier PDF SHA hashes differ because it precedes the final integrated build. Use **#43631207424** for final exact provenance.
- All plotted observations are frozen archival results. The atlas did NOT introduce new statistical experiments or new model searches.

### AwesomeFigures technology

Pinned `AwesomeFigures==0.1.0` from the paper dependencies; actual API calls are `set_style`, `color_palette`, `plot_scheme`, and `save_figure` (Okabe–Ito style). Do not substitute manual Matplotlib color palettes then claim AwesomeFigures integration.

Canonical files:
- `paper/ngsim-jerk-case-study/visuals/render_awesomefigures_atlas.py`
- `paper/ngsim-jerk-case-study/visuals/render_visual_suite.py`
- `paper/ngsim-jerk-case-study/visuals/render_method_comparison.py`
- `paper/ngsim-jerk-case-study/visuals/audit_awesomefigures_atlas.py`
- `paper/ngsim-jerk-case-study/generated/awesomefigures_atlas_manifest.json` (input/output SHA-256)
- `paper/ngsim-jerk-case-study/visuals/README.md`
- `paper/ngsim-jerk-case-study/FIGURE_ATLAS.md`
- Workflow `.github/workflows/paper-c-awesomefigures-atlas-pc08.yml`.

**Workflow caveat:** The last checked workflow triggers/branch guard name only `feature/paper-c-awesomefigures-atlas` and `paper/paper-c-scientific-editorial-review`, even though Paper C now lives in **main**. A successor who wants a new build from `main` must inspect the latest workflow YAML and safely adapt the allowlist for a NEW scoped branch or use an approved manuscript-only workflow; never assume dispatch on main succeeds or blindly republish into an unrelated branch. The workflow uses self-hosted `PCAG103A-08` (Windows X64), Conda `trendestimation`, protected source-SHA publishing, detached frozen-data worktrees, and append-only results archives. Never overwrite existing build directories.

### Figure inventory — ten new groups, each PDF/SVG/PNG (30 new assets)

1. `atlas_known_jerk_regimes`: synthetic historical known-jerk RMSE for six prespecified motion regimes (216 trajectories per regime).
2. `atlas_tsvd_rank_pathology`: conditional position-GCV near-interpolation ranks and share of squared jerk error.
3. `atlas_paired_jerk_losses`: case-paired PLS versus nominal-EDF-matched TSVD errors.
4. `atlas_method_tradeoff`: known historical jerk reconstruction versus clean future position forecasting; different targets.
5. `atlas_ngsim_by_site`: US-101 versus I-80, common continuation, cumulative forecast RMSE.
6. `atlas_ngsim_paired_delta`: paired NGSIM episode-level forecast MSE differences; descriptive only.
7. `atlas_spectral_calibration_grid`: selected S against theoretical fraction for four tuning policies, correctly specified Gaussian setting.
8. `atlas_misspecification_matrix`: calibration errors for correlation/outlier/jerk-model violations.
9. `atlas_noise_jerk_interventions`: independently change observation-noise and genuine jerk-innovation variation.
10. `atlas_reference_policy`: impact of training-derived reference mean and smoothing selector.

**Three new interpretive figures** are placed into the primary manuscript: jerk-regime RMSE, TSVD-GCV rank pathology, real NGSIM site heterogeneity. All ten appear in the supplemental 12-page atlas. **Eight previously existing** Experiment006/007/008 scientific figure groups were restyled, not deleted. A legend collision in the jerk-regime graphic was fixed and visually inspected. Gallery provides exact file links and explanatory scientific caveats.

## 3. Statistical and physical foundation

Let observations `y ∈ R^n` be noisy longitudinal vehicle positions (meters), latent clean positions `τ`, sample step `Δt=0.1 s`, `D=D_3∈R^(n−3)×n` with stencil `(−1,3,−3,1)`, `Q=DᵀD`, and `m=n−3`.

Guerrero-style established reference-mean PLS:
```math
τ_hat(λ,μ) = argmin_τ [ ||y−τ||_2² + λ ||Dτ−μ 1||_2² ]
           = (I+λDᵀD)^{-1}(y+λ μ Dᵀ1).
```
`μ` has units of **meters per discrete third difference**. The associated jerk reference is `μ/(Δt)^3` in m/s³. The finite-difference jerk proxy is `Dτ/(Δt)^3`; it is not a directly observed continuous jerk derivative in NGSIM. `ker D` is three-dimensional (quadratic sequences). For large λ, the fitted trend approaches the quadratic/cubic reference constrained by μ; it does *not* assert real vehicles have constant jerk.

For positive eigenvalues `δ_j` of `DDᵀ`:
```math
S(λ) = (1/m) Σ_j λδ_j/(1+λδ_j),       0 ≤ S ≤ 1,
df_fixed_mu(λ) = n − m S(λ) = tr((I+λQ)^{-1}).
```
These degrees of freedom are **conditional on μ fixed**, NOT the complete selected estimator's effective complexity if μ is fitted from y.

For a historical cubic-OLS `μ_hat=aᵀy`, choose `q_1` with `Dq_1=1`; fixed tuning gives the plug-in PLS map `A_PLS=H+(I−H)q_1 aᵀ`, `H=(I+λQ)^{-1}`, with trace `tr(H)+aᵀ(I−H)q_1`. For hard TSVD projector `P_r`, `A_TSVD=P_r+(I−P_r)q_1 aᵀ`, trace `3+r+aᵀ(I−P_r)q_1`. The Experiment008 matched rank matches **nominal fixed-reference EDF**, not the complete plug-in traces, and neither trace includes the additional effect of data-selected λ/r.

**SVD is a genuine estimator comparison, not a solver-speed comparison.** Let `D=U diag(σ_j)V_+ᵀ`, V0 span quadratic nullspace, and q satisfy `Dq=μ1`. PLS multiplies positive modes by `(1+λσ_j²)^{-1}` (soft spectral attenuation). Hard TSVD preserves only the r least-rough positive modes, using multipliers 1 for those modes and 0 for discarded modes, plus the same 3-dimensional nullspace. GCV chooses r by *conditional plug-in position GCV* with fitted μ held fixed in denominator; not exact full-data-dependent GCV. TSVD rank-matched is an ablation, not an independently tuned rank policy.

**Gaussian relative-noise interpretation** requires `y=τ+ε`, `Dτ=μ1+u`, independent `ε∼N(0,σ_ε² I)` and `u∼N(0,σ_u²I)`, with `λ=σ_ε²/σ_u²`; if `σ_j` is physical jerk innovation SD then `σ_u²=(Δt)^6 σ_j²`. Under those assumptions, `S(λ_true)` is the mean spectral fraction of the covariance of **observed third differences** caused by observation noise. For general correlated structures, a covariance-defined fraction is `tr((C_u+C_ε)^(-1) C_ε)/m`, where `C_ε=Cov(Dε)`; a scalar-λ fitted S can be miscalibrated. S is **NOT absolute sensor accuracy, an observed noise fraction of individual positions, or a probability an observation is corrupt**. Scaling noise and genuine jerk SD by the same factor leaves theoretical S unchanged while absolute measurement variance changes.

**Likelihoods:** fixed-μ profile Gaussian likelihood / library `mle` differs from unknown-μ joint REML. For `z=Dy, B=DDᵀ, Wλ=I+λB`, joint REML uses
```math
μ_hat(λ)=[1ᵀWλ^{-1}z]/[1ᵀWλ^{-1}1],
F_REML(λ)=log|Wλ|+log(1ᵀWλ^{-1}1)
 +(m−1)log{[(z−μ_hat1)ᵀWλ^{-1}(z−μ_hat1)]/(m−1)}.
```
Do not attribute Gaussian maximum likelihood itself as Guerrero's 2007 innovation. See `notes/GUERRERO_GAUSSIAN_REML_EQUIVALENCE.md` and original bibliography.

**Forecasting:** PLS is a smoother, not an intrinsic forecasting model. Two explicitly different continuation families occur: a same-algorithm last-three-point constant-third-difference recurrence (method-specific μ: PLS/TSVD historical cubic OLS, spline/SG zero), and separate quadratic-local (25 historical samples) or spline quadratic Taylor continuation. The latter is an end-to-end method + boundary-rule comparison; do not describe it as an isolated smoothing-filter effect.

Crucial scoring correction: horizon-H position RMSE is **cumulative over every frame h=1,...,H**, not at h=H only:
```math
RMSE_H = sqrt{ (1/(NH)) Σ_i Σ_{h=1}^H (xhat_{i,h}−x_{i,h})² }.
```

## 4. All completed Paper C experiments and numerical facts

| Experiment | Completed purpose and independence | Read first |
| --- | --- | --- |
| 001–003 | Historical exploratory/protocol steps; preserve artifacts and read their files, but do not present as a separate independent confirmatory study. | `experiments/experiment00X/` |
| **004** | Real FHWA NGSIM expanded evaluation: 200 selected quality-qualified episodes (100 US-101; 100 I-80), training length 80 at 10 Hz; five coarse recording blocks; no independent physical jerk truth. Windows Actions **#42538556206**. | `experiments/experiment004/README.md`, `RUN_LEDGER.md`, archive `results/paper-c-exp004-pc08-42538556206-a1` |
| **005** | 96 pilot + **1,296** independently generated known-truth synthetic trajectories, 80 historical and 20 clean withheld future positions; analytic jerk families, GCV and fixed-μ Gaussian likelihood, cubic reference and spline/SG controls. Cloud run **#42547883064**; frozen original PC08 source also used by Exp008. | `experiments/experiment005/README.md`, `RUN_LEDGER.md`, archive `results/paper-c-exp005-cloud-42547883064-a1` |
| **006** | Unknown-μ joint REML + continuous parameter selection, fitted to **the same 1,296 Exp005 synthetic trajectories** and the **same 200 Exp004 NGSIM episodes**, not new independent synthetic data. Windows **#42639588117**; cloud scientific replication **#42639588094**. | `experiments/experiment006/README.md`, `RUN_LEDGER.md`, archive `results/paper-c-exp006-pc08-42639588117-a1` |
| **007** | Independent known-noise/jerk calibration experiment: **1,944 factorial cases**, 72 independently drawn parents, 27 repeated treatment cells per parent; 4 selection methods, 7,776 valid decisions. Pilot 162. Windows **#42660204414**, independent Linux computation **#42660028292** with same seeds, *not independent statistical draws*. | `experiments/experiment007/README.md`, `RUN_LEDGER.md`, archive `results/paper-c-exp007-pc08-42660204414-a1` |
| **008** | Genuine five-smoother comparative benchmark on same **1,296** Exp005/006 synthetic cases and **200** Exp004/006 NGSIM cases. Historical 6,480 synthetic fitted rows, 38,880 synthetic future rows, 1,000 real fitted rows, 6,000 real forecast rows. Windows **#42717662044**. | `experiments/experiment008/README.md`, `run.py`, archive `results/paper-c-exp008-pc08-42717662044-a1` |

### Experiment008: synthetic **known finite discrete jerk** historical RMSE (m/s³)

| Method | RMSE |
| --- | ---: |
| PLS, cubic-OLS μ + continuous Gaussian profile likelihood | **2.441257** |
| Hard TSVD, nominally matched fixed-reference EDF | **2.941621** |
| Savitzky–Golay, window 21 / degree 3 | **36.829147** |
| Natural cubic smoothing spline, GCV | **60.913063** |
| Hard TSVD with conditional plug-in position GCV | **250.718104** |

An audit of archived per-case `synthetic/fitted_rows.csv` found **145 of 1,296** conditional-GCV TSVD ranks at **75 or 76** out of 77 positive modes, accounting for **78.9465% of total TSVD-GCV squared historical jerk error**. This near-interpolation derivative amplification does not mean all SVD estimators are poor. This statistic is from old rows, not a new model search.

A **54-cell stratified paired trajectory bootstrap** from those same frozen rows (24 trajectories/cell, seed 30133, 5,000 resamples) gives nominally matched TSVD-minus-PLS RMSE **0.500364 m/s³**, conditional 95% bootstrap interval **[0.322681, 0.713368] m/s³**. This is conditional on the fixed synthetic mixture, not real-world population uncertainty. See `visuals/audit_frozen_svd_comparison.py`, `tests/test_paper_c_frozen_svd_audit.py`, `tests/test_paper_c_plug_in_edf.py`, and `notes/SCIENCE_EDITORIAL_REVIEW.md`.

### Forecast comparisons: understand continuation and evaluation target

For **synthetic clean position**, first-second cumulative RMSE (meters), common last-25 quadratic continuation: PLS 0.435296; matched TSVD 0.450206; TSVD-GCV 0.488903; GCV spline 0.461424; SG 0.482451.

For **real recorded NGSIM position**, first-second cumulative RMSE (meters), common 3-point third-difference continuation: PLS **0.514386**; matched TSVD **0.511776**; TSVD-GCV **0.533672**; spline-GCV **0.494562**; SG **0.818773**. The separate GCV spline plus quadratic Taylor continuation achieved **0.348043 m**, a stronger pooled end-to-end 1-second result. **Keep these adverse PLS comparisons intact**; the paper cannot claim universal PLS superiority in forecasting.

NGSIM site and episodes are NOT random independent drivers: vehicle identifiers may repeat, recordings share 5 blocks, camera position is not independently verified latent true position, and no observed true physical jerk exists. Any site or episode bootstrap/heterogeneity figure should be described as exploratory/descriptive.

### Experiment007 calibration facts

Under correct independent Gaussian covariance assumptions, joint REML selected S had **Spearman ≈ 0.9654** with the theoretical spectral noise attribution and **MAE ≈ 0.01148**. Correlated AR(1) observation noise and endpoint outliers degrade calibration. Scaling both observation-error SD and physical jerk-innovation SD by four leaves S invariant, while observation variance increases 16×. There are **72** independent parents, NOT 1,944 independent Monte Carlo trajectories. The study tests interpretability, not absolute NGSIM sensor precision.

## 5. Manuscript story, editorial decisions, and prior corrections

Current main manuscript order:
1. Physical motivation and conservative prior-art attribution.
2. Established PLS objective, discrete jerk units, nonzero μ, normalized S, Gaussian conditional interpretation, likelihood variants; TSVD hard filter versus PLS soft filter, spline and SG.
3. Synthetic known-jerk evaluation, genuine baselines, paired uncertainty, rank-pathology.
4. Separate Experiment007 noise/smoothness calibration, with misspecification counterexamples.
5. Recorded real NGSIM historical/forecast application, site heterogeneity, **negative or mixed** PLS outcomes.
6. Limitations, extrapolation-versus-smoothing distinction, reproducibility, careful conclusion.

Earlier fixes: correctly distinguish plug-in GCV from full-estimator exact GCV; conditional versus plug-in EDF; isolate genuine truncated SVD (not SVD used to invert PLS); replace misleading terminal-horizon descriptions by cumulative-window RMSE; preserve different boundary/μ rules and spline-Taylor superiority; repair LaTeX orphaned equation number, stock CAS footer (“Research draft — not submitted”), long DOI that protruded into opposite column, and final figure legend overlap. Author ORCID is already in `main.tex`. Authors shown (Heriberto Espino-Montelongo, Daniela Cortés-Toto) are **provisional** until coauthor approval. The Elsevier class is a format choice, **not confirmation of selected or submitted journal**.

Source-derived scientific priority: Whittaker (1923), Henderson, Guerrero (2007: nonzero reference and smoothness), Cortés-Toto et al. (2017), and Biessy (published online 2025, 2026 volume) predate our application. Do not call PLS, controlled smoothness or WH extrapolation novel. Source bibliography in `references.bib` and provenance/review references in `notes/LITERATURE_REVIEW.md`, `notes/METHOD_FIRST_EDITORIAL_HANDOFF.md`.

## 6. Chronology of paper, builds, visual integration and merges

- Early Paper C experiments (004–008) completed in independently archived runs. Original `main.tex` and historical plots preserved.
- Nov 9: PR #131 method-first physical/statistical rewrite with genuine hard-TSVD comparator. First 11-page compiled CAS manuscript in [#42719535746](https://github.com/heri-espino/trendestimation/actions/runs/42719535746).
- Nov 9–10: separate scientific-editorial continuation PR #133: corrected full plug-in hat-matrix mathematics, GCV and nominal rank-matching labels, added frozen-row audit and paired uncertainty, improved empirical narrative. Verified 12-page compiled draft in [#42769072781](https://github.com/heri-espino/trendestimation/actions/runs/42769072781).
- Nov 14: author requested **many more figures using genuine AwesomeFigures**, plus a supplemental gallery. Branch/PR #136 created. It generated ten additional figure groups in PDF/SVG/PNG and restyled eight prior groups; three new figures incorporated in main article, all ten in supplement. Corrected figure legend, audited outputs.
- Nov 14: **PR #136 merged into the Paper C review branch**, merge SHA `ba066a703ca7ae5963dada68628e50676c300e25`. First verified 14-page paper /12-page atlas in #43630573121; **final integrated runner #43631207424** success with a newly verified 14/12-page pair and hashes above.
- Nov 14: **PR #133 merged into `main`**, merge SHA `06ab103d69e45ef2a32d9675bed7c82d48e4afb6`. This was **after** the last messages saying #133 remained open. This distinction is essential.
- At verification on Nov 18: `paper/LATEST_PAPERS.md` on main indexes the latest three manuscripts; the Paper C files and AwesomeFigures gallery are present in `main`. No scientific experiments rerun or journal submission.

## 7. Safe immediate workflow for a new agent

1. Inspect live GitHub status and current `origin/main` before anything else. Read `README.md`, `AGENTS.md`, `AI_HANDOFF.md`, `paper/SESSION_HANDOFF.md`, `paper/PUBLICATION_MAP.md`, `paper/LATEST_PAPERS.md`, Paper C `README.md`, `notes/SCIENCE_EDITORIAL_REVIEW.md`, this handoff, full `main.tex` and all six sections, bibliography, figure gallery and scripts, tests/workflows, manifests and Experiment004–008 ledgers.
2. Identify the user's **new explicit goal**. If the goal is just continuing the paper, first read current 14-page PDF and 12-page atlas and compare visible graphics, scientific captions and citations. Do not start new experiments or design a new paper.
3. Check `main`, PR #133/#136 merge records, open historical PRs #131/#132 and other agents' branches. Use a **new feature branch** for any edits; no force-push or unrelated work.
4. For visualization changes, use pinned native AwesomeFigures renderer; mount `results/paper-c-exp006-pc08-42639588117-a1`, `results/paper-c-exp007-pc08-42660204414-a1`, `results/paper-c-exp008-pc08-42717662044-a1` read-only. Verify original SHA-256s/counts. Existing 10+8 figure groups and legends already completed.
5. For LaTeX-only edits, compile on PCAG103A-08 (or existing approved GitHub Actions workflow) without reconstructing experiment data. Adapt the workflow branch trigger safely since current visual workflow allowlist predates the `main` merge. Record exact source commit, PDF sha256, page counts, source data hashes, log and visual inspection results. Publish to scoped branch and separate immutable results-only ref.
6. Run tests/audits appropriate to changed files, inspect **every** final PDF page. Existing paper audits: `visuals/audit_awesomefigures_atlas.py`, original `visuals/audit_methods_pdf.py`; numerics `tests/test_paper_c_plug_in_edf.py`, `tests/test_paper_c_frozen_svd_audit.py`, and Experiment008 tests. Do not claim “fully verified” from a green LaTeX job alone.
7. Update agent notes and reproduction files for material changes, preserve all source/results/SVG/PDF/PNG and historic branch archives. Commit/push and open a PR; **do not merge or journal-submit without the user's explicit approval**. Before submission, obtain final journal target, coauthor approval/order/affiliation, funding/conflicts/data-availability declarations, rights verification and final references.

## 8. What remains open scientifically — not mandatory new work

The manuscript is a compiled, scientifically qualified **research draft**, not peer-reviewed or submitted. The main remaining gates are actual coauthor/editorial review and venue-specific formatting. Potential *new*, separately proposed work might include exact full-estimator TSVD GCV, alternative physically constrained estimators, larger site/block sampling, robust noise calibration, or a strictly prespecified new extrapolation ablation. Such work requires fresh labels, protocols and author authorization, and must not be retroactively substituted for Experiment008 or interpreted as already validated. The earlier `notes/EXTRAPOLATION_*.md` documents discuss hypotheses, **not** verified new experimental benefits.

**Nonnegotiable claims:** PLS is established; jerk here is a finite-difference target; S is relative/model-conditional; the Gaussian calibration does not measure absolute sensor precision; 1,944 calibration observations share 72 parents; 200 NGSIM episodes are clustered recorded-position samples with unknown clean jerk; real spline-plus-Taylor forecasting performs better in some comparisons; TSVD-GCV is conditional plug-in GCV; rank-matching is nominal conditional EDF; cumulative forecast RMSE is a window metric; AwesomeFigures atlas did not create new experiments.

## 9. Handoff source links (read live and reconcile with current Git)

- Repository: https://github.com/heri-espino/trendestimation
- Latest paper navigator: https://github.com/heri-espino/trendestimation/blob/main/paper/LATEST_PAPERS.md
- Paper PDF: https://github.com/heri-espino/trendestimation/blob/main/paper/ngsim-jerk-case-study/main.pdf
- Atlas PDF: https://github.com/heri-espino/trendestimation/blob/main/paper/ngsim-jerk-case-study/atlas_supplement.pdf
- Illustrated gallery: https://github.com/heri-espino/trendestimation/blob/main/paper/ngsim-jerk-case-study/FIGURE_ATLAS.md
- Canonical scientific review: https://github.com/heri-espino/trendestimation/blob/main/paper/ngsim-jerk-case-study/notes/SCIENCE_EDITORIAL_REVIEW.md
- Final windows atlas: https://github.com/heri-espino/trendestimation/actions/runs/43631207424
- Full immutable final build: https://github.com/heri-espino/trendestimation/tree/results/paper-c-awesomefigures-pc08-43631207424-a1/paper/ngsim-jerk-case-study/visuals/runs/awesomefigures-43631207424-a1
- PR #136 visual merge: https://github.com/heri-espino/trendestimation/pull/136
- PR #133 integration to main: https://github.com/heri-espino/trendestimation/pull/133
- Original genuine TSVD PR #131: https://github.com/heri-espino/trendestimation/pull/131
- Alternative editorial PR #132: https://github.com/heri-espino/trendestimation/pull/132

### End-of-handoff directive

**Continue from the current verified repository state. Do not restart the project.** Prioritize technical/scientific truth, high-quality graphics, complete reproducibility and integrity of published results. Conserve the author's time: read the work already done, identify only genuine remaining decisions, keep everything preserved, and obtain explicit permission before merging or submitting.
