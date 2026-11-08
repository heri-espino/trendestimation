# Paper C — experiment003: GCV-selected cubic smoothing spline

**Status:** Predeclared, bounded extension of experiments 001–002, designed for execution on PCAG103A-08. Results must be archived and verified before the status is upgraded to completed.

## Motivation

Experiment002 compared the d=3 PLS forecasts against cubic smoothing splines with a **fixed noise-scale heuristic**. A stronger statistical comparator is a smoothing spline whose penalty is independently selected by **generalized cross-validation (GCV)** from the historical 80-point training window. SciPy provides this using make_smoothing_spline(x, y, lam=None). Official reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.make_smoothing_spline.html .

## Fixed protocol

- Reuse exactly the five original NGSIM track segments, fifteen overlapping origins, and three chronological horizons from experiments001/002. They come from only **two distinct vehicle IDs**.
- Fit a **natural cubic smoothing spline** with training-only GCV-selected smoothing parameter. Never tune from a withheld position.
- Four forecast continuations are predeclared for the same fitted spline: quadratic endpoint Taylor, cubic endpoint Taylor, local-25 quadratic from historical spline-smoothed positions, and the library BSpline native extrapolation.
- Evaluate future recorded **position RMSE and MAE** in meters, not actual jerk RMSE. Save all 180 individual errors and 12 aggregate cells, plus GCV-matched earlier PLS and spline results in the report.
- No additional information inputs (e.g. velocity measurements), no hyperparameter tuning on the evaluation windows, and no attempts to make comparable curves look equally smooth through post-hoc adjustment.

## Reproduce

From repository root with SciPy and the current library installed:

    python -m pytest tests/test_paper_c_experiment003.py -q
    python paper/ngsim-jerk-case-study/experiments/experiment003/run.py --output-dir paper/ngsim-jerk-case-study/experiments/experiment003/runs/manual

The PC08 workflow archives the full data, version lock, source commit SHA and report in an immutable results-only branch. On successful completion, mirror the exact result files into this experiment's results directory in its research PR, leaving the runner archive intact.

## Expected interpretation

This makes the spline comparison substantially fairer than claiming superiority over one arbitrary smoothing strength; however, **same GCV criterion does not make different penalty orders equivalent**, and different continuation rules may dominate at different horizons. Natural cubic spline boundary conditions can induce undesired extrapolation behavior. The pilot remains too small for population inference. Never claim the first historical use of d=3 PLS, a measured true jerk benefit, or a universally better forecast rule without further evidence.

## Experiment numbering note

The earlier manuscript plan used the name “experiment003” for a *conditional, future* adaptive-reference study without an implementation. This source-controlled experiment003 is now specifically **the GCV smoothing-spline comparator**. Future adaptive-reference or large independent-vehicle research must use the next free sequential ID. Preserve old plans as historical context rather than inventing completed observations.
