**Paper C verified 2026-11-10:** Draft [PR #133](https://github.com/heri-espino/trendestimation/pull/133) has a compiled 12-page method-first physical jerk manuscript, source-derived plots and a frozen-data paired audit. [PC08 run #42767882100](https://github.com/heri-espino/trendestimation/actions/runs/42767882100) passed (PDF SHA-256 `5b6c5305c928e42f4a8b0665f5b2eb0a3a31f9238f86cf427cc3b6defb9ace3f`). Read [full reproducibility handoff](SCIENCE_EDITORIAL_REVIEW.md) for conditional plug-in TSVD-GCV, nominal EDF (not exact full EDF), 145 high-rank failures, 54-cell paired RMSE bootstrap [0.3227, 0.7134] m/s³, and cumulative horizon RMSE definitions. Original Experiments004–008 not rerun; PRs unmerged; no submission.

**Paper C scientific-editorial continuation (2026-11-09):** Review branch `paper/paper-c-scientific-editorial-review` is derived from the unchanged open PR #131, not PR #132. Read [scientific editorial audit](SCIENCE_EDITORIAL_REVIEW.md) for method-dependent reference-jerk comparability, conditional plug-in TSVD-GCV/EDF caveats, the exact archival near-interpolation error decomposition, and improved known-jerk-before-calibration reading order. **No Experiment004--008 rerun, no merge and no submission.** Publication PDF/build status must be checked against this branch's latest Actions run; the earlier PR #131 11-page PDF remains a valid historical build, not evidence that these new edits have compiled.

# Paper C method-first editorial handoff — verified 2026-11-09

**Canonical manuscript:** `paper/ngsim-jerk-case-study/main.tex` (Elsevier CAS). **Compiled scientific PDF:** [paper/ngsim-jerk-case-study/main.pdf](../main.pdf). **Working review:** [PR #131](https://github.com/heri-espino/trendestimation/pull/131), branch `paper/paper-c-methods-simulation-real-svd`, stacked on `paper/paper-c-visual-suite-exp007`; **open and unmerged**.

**User's editorial decision:** This paper is a **statistical/physical third-order penalized least-squares trend-estimation case study**. It must lead with Guerrero-style PLS and the normalized smoothness index S, then include **known-jerk simulation** and **real FHWA NGSIM case studies**, comparing conventional jerk methods. Do not present it as a Cholesky/SVD/other backend-speed paper. The original numerical paths/timings/criterion heatmap still exist in Git and belong in the separate Springer or reproducibility studies, not in the manuscript's core claims.

## What is in the paper now

1. **Theory/method:** `sections/methods.tex`: d=3 PLS objective, reference third difference mu, `S(lambda)`, exact fixed-mu effective df, and Gaussian variance-ratio interpretation; explicit distinction between Gaussian profile ML and mean-adjusted REML.
2. **SVD physical baseline:** `sections/methods.tex`, `experiments/experiment008/run.py`: **truncated SVD of D3** is a different smoothing estimator with a *hard* singular-filter cutoff; PLS is a *soft* filter. Either GCV-select the cutoff rank or match PLS effective df; both use the same training historical global cubic OLS reference. Full untruncated SVD just calculates the same PLS estimator and is not a statistical baseline.
3. **Noise calibration simulation:** `sections/precision_calibration.tex`, Experiment007; 1,944 crossed observation/noise/jerk-structure conditions but only 72 independent random parent draws. Model-correct joint REML selected-S versus known covariance noise fraction Spearman 0.9654 and MAE 0.0115, with serious AR(1)-noise model misspecification. Not absolute sensor precision.
4. **Known-physical-jerk simulation:** `sections/synthetic_case.tex`, Experiment005/006/008 same 1,296 archival confirmatory true clean trajectories (no regeneration). New PLS, TSVD, SG, GCV spline comparison on identical first-80 historical observations and identical discrete jerk target. PLS profile ML + global cubic OLS mu 2.4413 m/s³; matched-complexity TSVD 2.9416; GCV TSVD 250.718; SG 36.829; natural cubic GCV spline 60.913. One-second clean-position forecast with same 25-point continuation: PLS 0.4353m, matched TSVD 0.4502m, spline 0.4614m, SG 0.4825m, GCV TSVD 0.4889m.
5. **Real recorded-position case:** `sections/real_case.tex`, 200 preselected real NGSIM episodes (100 I-80 + 100 US-101, five coarse recording-time groups), 80 historical positions, h=5/10/20 future recorded positions. Common three-point one-second forecast: matched TSVD 0.5118m, PLS 0.5144m, TSVD GCV 0.5337m, SG 0.8188m, GCV spline with the *common* three-point continuation 0.4946m. **GCV cubic spline with its own quadratic Taylor continuation 0.3480m** remains best in this real pooled sample. Real jerk truth **not observed**. The 15-origin original pilot sample (two distinct vehicle IDs) remains illustrative only.
6. **Conclusions:** `sections/discussion.tex` explicitly states different physical targets, conditional S interpretation, no universal forecast advantage, and no false invention of PLS, SVD regularization or the smoothness index.

## Compiled PDF and figure provenance

[Successful PCAG103A-08 manuscript workflow #42719535746](https://github.com/heri-espino/trendestimation/actions/runs/42719535746) compiled an **11-page, 734,107-byte** CAS PDF, SHA-256:

`e28a43bc93ef49111d0d9a539fb1f7d675ea0a5f57e384f3d1ec391c410b0629`.

Both the prior six-multipanel scientific figure integrity audit and the new method-first manuscript/SVD audit **passed** (including text/figures and removal of backend-timing tables). The new image groups are **two vector PDF/SVG/PNG sets**:

- `figures/exp008_known_jerk_benchmarks.{pdf,svg,png}` — exact 1,296-case physical jerk and synthetic clean forecasting outcomes, log-scaled jerk axis.
- `figures/exp008_real_forecast_benchmarks.{pdf,svg,png}` — exact 200-episode recorded-future position RMSE at 0.5/1/2 seconds for five common-rule filters plus the spline-Taylor end-to-end comparator.

The six earlier Experiment006/007 source-derived plots (three exports each) and three original experimental PGF/SVG/PDF plots still appear in the compiled journal paper. The full original five figures, including the solver/backend diagram, remain **intact in the repository** even where intentionally not included in the manuscript.

**Persistent full audited VM build directory**:

`C:\Users\175199\Documents\TrendEstimation-PaperC\manuscript-methods\run-42719535746-a1`.

**Independent permanent Git file inventory/build:** [results/paper-c-methods-pdf-pc08-42719535746-a1](https://github.com/heri-espino/trendestimation/tree/results/paper-c-methods-pdf-pc08-42719535746-a1), containing 19 generated files (1,070,716 bytes excluding file_inventory.json), including compiled PDF, new vector figures, exact file SHA-256 and separate successful audits, package snapshot and compilation logs. The source-figure manifest is `generated/exp008_methods_figure_manifest.json`. The older six-figure source manifest is `generated/visual_suite_manifest.json`. `visuals/render_method_comparison.py` regenerates the two new groups from frozen successful experiment CSVs; `visuals/audit_methods_pdf.py` validates their exact hashes and the compiled paper.

## Source data and results preservation

- Experiment008 actual physical-baseline [successful Windows run #42717662044](https://github.com/heri-espino/trendestimation/actions/runs/42717662044). **Full persistent VM** `C:\Users\175199\Documents\TrendEstimation-PaperC\experiment008\run-42717662044-a1`. [Results-only branch](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp008-pc08-42717662044-a1): 16 files, 7,230,292 bytes excluding inventory, 6,480 synthetic + 1,000 real fitted rows, 38,880 + 6,000 future-error records, summaries and logs. Science code `experiments/experiment008/run.py` and `tests/test_paper_c_experiment008.py`, test suite passed on the runner.
- Experiments005–007 original independent, archived first-party synthetic data and results are **unchanged**. Experiment007 [full ledger](../experiments/experiment007/RUN_LEDGER.md) and Experiment006 [ledger](../experiments/experiment006/RUN_LEDGER.md) provide the original fixed scientific selection and calibration protocols.
- Experiment004 original downloaded FHWA NGSIM raw source pages remain on PC08 under `C:\Users\175199\Documents\TrendEstimation-PaperC\experiment004\run-42538556206-a1\data`. Exact selected-position SHA-256: `e6b594edd0cde7165302c4c7b65720645ec940122af23152db24f7eb1230598e`. The original raw pages remain on the VM, not silently fabricated or republished in the small Git figure archive.

## Important next steps

All future edits should maintain the user's decision: **statistical third-difference PLS first**, interpretable S, proper synthetic-known-truth and real-recorded outcome separation. Prior experiments remain immutable; new explorations get sequential experiment IDs. Human editorial review of layout and coauthor names is still required before submission; automated PDF text/figure checks are not a substitute for page-by-page visual review. Do not merge PR #131 or other stacked branches without explicit authorization.
