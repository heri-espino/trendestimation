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
