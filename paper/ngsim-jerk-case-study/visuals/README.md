# AwesomeFigures Paper C atlas (November 2026)

The canonical manuscript now includes three source-derived physical diagnostics; a separate [supplement](../atlas_supplement.tex) contains ten new panels. See the [figure gallery](../FIGURE_ATLAS.md) for all ten image previews. All results originate from the previously completed immutable Experiment006/007/008 branches. None of Experiments004--008 were rerun.

| New figure | Result portrayed | Design limitation |
| --- | --- | --- |
| atlas_known_jerk_regimes | Historical discrete-jerk RMSE by six physical regimes | 1,296 synthetic trajectories; 216 per regime |
| atlas_tsvd_rank_pathology | Conditional GCV TSVD rank counts and error concentration | 145 cases with rank 75/76; 78.9% of squared jerk error |
| atlas_paired_jerk_losses | Paired PLS versus nominal-EDF-matched TSVD loss | 1,296 paired synthetic cases, not observed real jerk |
| atlas_method_tradeoff | Jerk reconstruction versus clean 1-second window forecasting | Different physical outcomes and same local25 continuation |
| atlas_ngsim_by_site | US-101 versus I-80 recorded-position windows | 100 selected episodes per site, not independent drivers |
| atlas_ngsim_paired_delta | Paired site/episode forecast MSE differences | Reused vehicle/time blocks; descriptive only |
| atlas_spectral_calibration_grid | Selected S versus covariance-theoretic noise fraction | Nine model-correct Gaussian cells, 24 parents per cell |
| atlas_misspecification_matrix | Four tuning policies across nine error/jerk structures | Model misspecification and paired parent draws |
| atlas_noise_jerk_interventions | Separate measured-noise and genuine jerk-volatility interventions | Archived parent-bootstrap uncertainty |
| atlas_reference_policy | Third-difference mean and likelihood choices | Existing Experiment006 known-jerk summaries |

The script [render_awesomefigures_atlas.py](render_awesomefigures_atlas.py) directly calls the pinned AwesomeFigures APIs set_style, color_palette, plot_scheme and save_figure to export vector PDF, editable SVG and PNG. The same APIs now style the existing six Experiment006/007 figures and two Experiment008 comparator figures. This does not claim exact LaTeX preamble-matched fonts; it produces genuine AwesomeFigures plots with documented provenance.

## Exact reproduction and preservation

Read root AGENTS.md, paper/SESSION_HANDOFF.md and [scientific editorial review](../notes/SCIENCE_EDITORIAL_REVIEW.md). Use the dedicated [PCAG103A-08 workflow](../../../.github/workflows/paper-c-awesomefigures-atlas-pc08.yml), which mounts the original three results-only branches as detached read-only worktrees. It verifies 1,296 synthetic paired fits, 200 real forecast episodes, all 72-parent calibration summaries and the known original jerk RMSEs. It never downloads NGSIM data or refits smoothing parameters.

The generated/awesomefigures_atlas_manifest.json stores the SHA-256 of every input and all 30 new output assets. The companion [audit](audit_awesomefigures_atlas.py) verifies the source-derived outputs and the main/supplement compiled PDF content. The complete VM build, 26-plus page previews, compilation logs and environment snapshots are retained on a unique append-only results-only Git branch, never solely on the runner.

Scientific interpretation constraints: S measures relative spectral observation noise only conditional on the covariance model. The Experiment007 1,944 factorial cells derive from only 72 independent parent draws. Real NGSIM has no independent clean jerk truth; its episodes share vehicles and recording-time blocks. The adverse 0.348 m spline-Taylor first-second position result remains in the canonical manuscript.

---
# Paper C reproducible visual suite

This directory generates six additional publication-grade figures for the canonical Elsevier CAS v2.4 manuscript. Figures derive from independently archived, completed Experiment006/007 scientific results; they do not alter the experiments, create hypothetical data, or retrain models. The existing five paper figures are preserved.

## Figure set

| Stem | Meaning | Source |
| --- | --- | --- |
| exp007_jerk_example | Predeclared synthetic clean/noisy position; raw and recovered physical third differences | Experiment007 trial confirm_000010, archived selected mu/lambda |
| exp007_spectral_interpretation | Spectral relative-noise weights, exact fixed-mean effective degrees of freedom | Analytic n=80, d=3 difference spectrum |
| exp007_calibration | Selected S versus true covariance noise fraction under IID and AR1 errors | Experiment007 confirm per_cell.csv |
| exp007_interventions | Separate manipulation of observation noise versus true jerk variability, with parent-bootstrap intervals | Experiment007 confirm effects_summary.csv |
| exp007_misspecification | Method-by-regime calibration error heatmaps | Experiment007 confirm calibration_summary.csv |
| exp006_reconstruction_forecasting | Known-jerk RMSE versus synthetic clean and NGSIM recorded forecast RMSE | Experiment006 confirm and real data summaries |

Each figure is exported as a vector PDF for TeX, an editable SVG and 240-dpi PNG preview, with white backgrounds and the repository's pinned AwesomeFigures elegant Okabe-Ito publication style. The rendering code is render_visual_suite.py. It stores input SHA-256 and per-figure output SHA-256 in generated/visual_suite_manifest.json.

## Exact scientific provenance

Experiment007: Windows runner successful [run #42660204414](https://github.com/heri-espino/trendestimation/actions/runs/42660204414), archived in [results/paper-c-exp007-pc08-42660204414-a1](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp007-pc08-42660204414-a1), data below paper/ngsim-jerk-case-study/experiments/experiment007/runs/pc08-42660204414-a1/confirm/.

Experiment006: Windows runner successful [run #42639588117](https://github.com/heri-espino/trendestimation/actions/runs/42639588117), archived in [results/paper-c-exp006-pc08-42639588117-a1](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp006-pc08-42639588117-a1), using confirm/ and real/ below paper/ngsim-jerk-case-study/experiments/experiment006/runs/pc08-42639588117-a1/.

Run [the standalone PC08 visual build workflow](https://github.com/heri-espino/trendestimation/blob/paper/paper-c-visual-suite-exp007/.github/workflows/paper-c-visual-rebuild-pc08.yml) to retrieve the two source archives in detached worktrees, rerender all graphics and compile the new PDF. No Monte Carlo or real NGSIM downloads are repeated.

## Interpretation safeguards

The Gaussian variance-ratio interpretation holds when the covariance model is correct; AR1 measurement errors cause clear miscalibration. The factor 1,944 describes paired factorial conditions, not independent drivers or independent Monte Carlo units; there are only 72 independent parent stochastic draws. The real 200-episode NGSIM study has no observed true jerk. The identified GCV smoothing-spline forecasting advantage and unfavorable cases are retained in the visual comparisons. Each figure is captioned with its source, target, units and limits.

The design remains a scientific paper, not a presentation: no decorative imagery, unstated image assumptions, hidden noise correlations or unverifiable chart values. The full source code, figures, compiled PDF, journal build logs and file hashes are kept in the repository or in the immutable VM/Git results archive.
