# Ahnert and Abel (2007) — local versus global numerical differentiation

**Reference:** Karsten Ahnert and Markus Abel, “Numerical differentiation of experimental data: local versus global methods,” *Computer Physics Communications* **177**(10):764–774 (2007), [DOI 10.1016/j.cpc.2007.03.009](https://doi.org/10.1016/j.cpc.2007.03.009). [arXiv preprint](https://arxiv.org/abs/physics/0510176).

**Source audit:** Publisher abstract and available extended article previews inspected 2026-11-08. The author's full original publisher PDF was *not* independently read in this pass; summaries below are scoped to the accessible material.

## Why this belongs in Paper C

The paper directly treats numerical derivatives of noisy experimental measurements, motivating a useful **physicists' benchmark taxonomy**:

- **Local methods:** finite differences and Savitzky–Golay filters. Convenient, but derivatives of noise can be unstable and local shape changes can produce variation.
- **Global methods:** smoothing splines and spectral smoothing. Represent a differentiable global fit with explicit smoothness regularization.
- **Evaluation principle:** derivative-error variance should be measured against known derivative truth **where available**, alongside the smoothness of the derivative estimate; residual fit alone is not sufficient.

The authors compare methods on artificial signals (including a sine signal and a Lorenz-system example) where derivative error is assessable, plus acoustic experimental data. Their results are **not claims about the NGSIM vehicles in our paper**, and do not establish which PLS forecast continuation is better.

## Method mapping into the existing repository

| Benchmark family | Our implemented comparison | Interpretation |
| --- | --- | --- |
| Third-difference PLS | Experiments001–003 use the unchanged TrendSmoother fit, with last3 and local25 forecast continuations | Our model's third differences approximate jerk; reference mean may be nonzero |
| Cubic smoothing splines | Experiment002 fixed training-only scale; Experiment003 GCV-selected natural cubic smoothing spline | Global penalty on integrated squared acceleration, not identical to third-difference PLS |
| Savitzky–Golay | Experiment002 21-point degree-3 filter plus Taylor continuation | Local regression differentiated at training cutoff |
| Local polynomial | Experiment002 degree-2 and degree-3 regressions on last 25 raw positions | Constant acceleration / constant jerk continuation policies |
| Spectral smoothing | Not implemented as independent estimator in these experiments | SVD is currently **only** a computational backend for existing PLS, not a competing forecasting method. Genuine SSA requires an explicit trajectory Hankel embedding, rank/window selection, and post-estimation continuation. |

**Important:** The in-sample GCV spline at a comparable criterion is not guaranteed to target the same effective degrees of freedom, physical derivative smoothness, or forecast objective as the finite-difference penalty. Extrapolation has its own boundary uncertainty. These comparisons are necessary but not a complete state-of-the-art survey.

## What the new results do and do not tell us

The GCV spline paired with a degree-2 Taylor forecast is RMSE **0.123310, 0.295081, 0.808529 m** at the 0.5/1/2-second horizons; PLS with d=3, zero reference and the last-three-point recurrence is **0.074519, 0.295769, 1.299841 m**. Thus PLS is favorable for the shortest horizon but does not dominate the spline. These are measured future **position** errors over only **two unique vehicle IDs** and no independently measured jerk. We still require synthetic truth for jerk-error inference.

## Handoff and citation scope

Cite this article to explain why spline and Savitzky–Golay are appropriate derivative-estimation baselines used in physical measurement analysis, **not** to assert a previous use of Guerrero nonzero-reference d=3 trend forecasting. Any later PCA/SVD or Kalman comparison requires explicit model definition and train-only calibration; do not add a numerical benchmark merely by naming a decomposition.
