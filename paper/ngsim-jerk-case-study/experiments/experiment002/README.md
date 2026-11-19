# Paper C — experiment002: fixed spline, Savitzky–Golay, and local-polynomial baselines

**Status:** Predeclared bounded computation using the original NGSIM pilot. The runner output is preserved under a separate results-only branch when available. This experiment is a **small illustrative comparison**, not population-level proof about jerk reconstruction or method novelty.

## Why these methods

In response to the author, the first external comparison emphasizes trajectory methods that are common in experimental measurement and derivative estimation:

1. **Cubic smoothing spline:** degree-3 UnivariateSpline, with a fixed **training-only** roughness estimate. Continue with a degree-2 Taylor expansion, degree-3 Taylor expansion, or a local-25 quadratic fit to spline-smoothed positions.
2. **Savitzky–Golay:** degree-3 polynomial, 21-point filter with the SciPy boundary rule; use the training endpoint position and derivatives to continue with quadratic or cubic Taylor expansion.
3. **Local polynomial:** fit degree 2 or 3 to the last 25 raw training positions and extrapolate.

**PCA is not itself a univariate jerk estimator**, and **SVD is a factorization/solver** rather than a separately specified trend model. Singular-spectrum analysis (SSA, low-rank Hankel SVD) might be meaningful as a later comparison if its window, rank, and selection rule are predeclared, but no PCA/SVD benchmark is claimed to have been run.

## Fully specified training-only choices

- Source: preserved NGSIM US-101 observations, 5 tracks, **2 distinct vehicle IDs**, 3 overlapping origins per track.
- Historical training window n=80 and exactly the same future horizons (0.5, 1, 2 seconds) as the prior PLS pilot.
- Cubic smoothing spline weight target: \(s=n\sigma_{\mathrm{pilot}}^2\), where

  \[
  \sigma_{\mathrm{pilot}}=\operatorname{clip}\left(
  \frac{1.4826\,\operatorname{median}|D_3y-\operatorname{median}(D_3y)|}{\sqrt{20}},
  0.01,0.75
  \right).
  \]

  This is a **heuristic** designed to avoid selecting smoothing on withheld trajectories. It does not identify true NGSIM observation noise and should be sensitivity-tested later.
- SG window=21, degree=3, derivatives via savgol_filter and delta=0.1 seconds, computed strictly on training data.
- All predictions evaluate the identical observed future time stamps. Each method has one forecast per track/origin/horizon, for 315 rows and 21 summaries.
- Archive original PLS-GCV results from [experiment001](../experiment001/README.md) **unchanged** for the side-by-side results Markdown. We do not adjust PLS smoothing decisions or report these extra baselines as PLS improvements.

## Reproduce on PCAG103A-08

The workflow at [paper-c-recurrence-splines-pc08.yml](../../../../.github/workflows/paper-c-recurrence-splines-pc08.yml) is bounded to this experiment branch and checks the runner is PCAG103A-08, uses the existing Conda environment, makes **no installations**, and keeps BLAS single-threaded. It checks both experiments for numerical validity, runs this comparator, uploads the full output, and permanently preserves a results-only branch.

From the repository root with an already prepared environment:

    python -m pytest -q tests/test_paper_c_experiment001.py tests/test_paper_c_experiment002.py
    python paper/ngsim-jerk-case-study/experiments/experiment001/run.py --verify
    python paper/ngsim-jerk-case-study/experiments/experiment002/run.py --output-dir paper/ngsim-jerk-case-study/experiments/experiment002/runs/local-manual

The output directory will contain (1) one row per method/origin/horizon in forecast_rows.json, (2) summaries in forecast_summary.json, (3) the full RESULTS.md table, and (4) run_manifest.json including dataset SHA and environment versions. No archived prior Paper C observations, paper figures or manuscript PDFs are overwritten.

## Limitations and next experiments

The user asked whether the entire d=3, nonzero-mu PLS forecasting combination could be historically novel. This experiment cannot establish bibliographic priority; it tests practical predictive accuracy for the specific software workflow. Nor can 15 overlapping windows from two vehicle IDs establish significant mean improvements in the vehicle population.

**Next:** evaluate many genuinely distinct vehicles (independent splits); include synthetic trajectories with known jerk for jerk-estimation error; evaluate alternative mu estimators and longer-horizon sensitivity. If SSA or a Kalman jerk-state smoother is added, document its observation model, tuning policy and any additional inputs. Do not use this pilot to tune competing methods and then call the same pilot an independent test.
