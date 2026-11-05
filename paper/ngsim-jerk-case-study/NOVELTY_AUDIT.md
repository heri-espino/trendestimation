# Prior-art and novelty audit: nonzero-reference jerk smoothing of NGSIM trajectories

**Date:** 2026-11-04. **Status:** Targeted public-literature search and mathematical analysis; not a systematic review or a certified claim of world priority. **Manuscript:** `paper/ngsim-jerk-case-study/main.tex`. The source manuscript and archived data have not been changed in this branch.

## Question

Has quadratic penalized least-squares (PLS) smoothing with *third differences centered on a nonzero mean* already been applied explicitly to estimate vehicle jerk from recorded longitudinal trajectories, especially NGSIM? A narrower question is whether using the *training-data-estimated* third-difference mean and normalized smoothness selection is a useful, documented contribution.

## Search protocol

Searched public publisher/paper indices with combinations of: `vehicle`, `NGSIM`, `trajectory smoothing`, `jerk`, `third difference`, `Whittaker`, `Henderson`, `penalized least squares`, `nonzero mean`, `reference jerk`, `trend filter`, `quadratic programming`, `spline`. Read accessible publisher abstracts/full-page descriptions and compare their stated methods with our exact optimization problem. The existing 40-file literature extraction index covers the statistical PLS history but does **not** fully cover transportation trajectory reconstruction. Both corpora and external results should be revisited before submission.

**Result:** No exact match for the *combined* NGSIM + Guerrero-style $d=3$ PLS + nonzero/plug-in third-difference mean + normalized smoothness comparison was identified in this targeted search. This absence of a located match is **not proof** that the implementation is first in the literature. Several substantially overlapping contributions were identified.

## Closest prior art: MUST read and cite as appropriate

| Study | Bibliographic source | What is established | What remains different from our exact model |
| --- | --- | --- | --- |
| Guerrero (2007), *Time series smoothing by penalized least squares* | https://doi.org/10.1016/j.spl.2007.03.006 | Classical quadratic PLS with an arbitrary difference order $d$ and potentially nonzero mean/reference $\mu$; for $\lambda\to\infty$ the trend can have degree $d$. | It does not specifically report NGSIM vehicle jerk; the **nonzero $\mu$ model itself is not new**. |
| Fan, Jin & Yin (2024), *Two-Step Quadratic Programming for Physically Meaningful Smoothing of Longitudinal Vehicle Trajectories*, *Transportation Science* 58(6):1371–1388 | https://doi.org/10.1287/trsc.2024.0524 | Direct NGSIM longitudinal trajectory smoothing with third-order derivative constraints, discrepancy and roughness quadratic programs, minimum-jerk physical motivation, and comparison with manually re-extracted trajectories. | Two-stage physically constrained quadratic programming, not identified in the accessible publisher abstract as the specific $\|D_3\tau-\mu\mathbf1\|^2$ penalty. **Strongest direct competitor**; read its full text before claiming specificity. |
| Marczak & Buisson (2012), *New Filtering Method for Trajectory Measurement Errors and Its Comparison with Existing Methods*, *Transportation Research Record* | https://doi.org/10.3141/2315-04 | NGSIM trajectory filtering with splines; uses jerk distributions and high-jerk percentages to assess smoothing. | Not established from the accessible abstract to use a nonzero third-difference reference mean. |
| Punzo et al. (2011), *On the assessment of vehicle trajectory data accuracy and application to the NGSIM program data*, *Transportation Research Part C* | https://www.sciencedirect.com/science/article/pii/S0968090X10001701 | Systematic analysis of NGSIM measurement errors using jerk, trajectory consistency, spectral measurements. | Primarily data-quality assessment rather than the precise third-difference centered PLS selector. |
| Cao et al. (2021), *V-Spline: An Adaptive Smoothing Spline for Trajectory Reconstruction*, *Sensors* 21(9):3215 | https://doi.org/10.3390/s21093215 | Penalized vehicle-trajectory reconstruction combining position and velocity, acceleration penalty and CV-based tuning. | Distinct spline basis/penalty and derivative targets; shows that penalization/CV for vehicle smoothing is established. |
| Zhu et al. (2024), *A generic optimization-based enhancement method for trajectory data: Two plus one*, *Accident Analysis & Prevention* 200:107532 | https://doi.org/10.1016/j.aap.2024.107532 | Bilevel vehicle-trajectory processing using $\ell_2$ and $\ell_1$ trend filters, with jerk indicators and downstream trajectory prediction. | Does not establish the particular Guerrero nonzero-mean $d=3$ fit in the accessible summary, but **trend filtering plus jerk in transportation is not new**. |
| Tang, Yoon & Barfoot (2019), *A White-Noise-On-Jerk Motion Prior for Continuous-Time Trajectory Estimation on SE(3)* | https://arxiv.org/abs/1809.06518 | Gaussian-process motion prior based on jerk with a constant-acceleration prior mean in pose-trajectory estimation. | Different GP/SE(3) setting. Reinforces that physically motivated jerk priors in trajectory reconstruction predate our manuscript. |

### What the literature search does and does not establish

- **Established:** Third-order differentiation of positions as jerk; quadratic/spline smoothing of vehicle trajectories; NGSIM jerk diagnostics; third-order quadratic programs; CV for trajectory smoothers; Guerrero's PLS and nonzero $\mu$.
- **Not located in targeted search:** Exactly the combination of a Guerrero-style third-difference reference mean estimated from *training-only position data*, normalized smoothness selection, and a held-out NGSIM vehicle trajectory study.
- **Not defensible without additional evidence:** "We introduce jerk estimation", "the first use of PLS for jerk", "the first use of nonzero-reference regularization", or "we introduce a new smoothing estimator." The close 2024 Fan et al. study means any broad novelty statement is especially vulnerable.

## Exact mathematical interpretation

For observations $y\in\mathbb R^n$ at constant interval $\Delta t$, write

$$
\widehat\tau_{\lambda,\mu}
=\underset{\tau}{\arg\min}\;
\|y-\tau\|_2^2+\lambda\|D_3\tau-\mu\mathbf1\|_2^2,
\qquad
\widehat j_i=\frac{(D_3\widehat\tau)_i}{(\Delta t)^3}.
$$

Then

$$
\lambda\|D_3\tau-\mu\mathbf1\|_2^2
=\lambda(\Delta t)^6
\sum_i\left(j_i-\frac{\mu}{(\Delta t)^3}\right)^2.
$$

Thus $\mu/(\Delta t)^3$ is a **reference physical jerk**, not inherently a measurement of actual jerk. $\mu=0$ biases the penalty toward zero jerk, while fixed $\mu\ne0$ biases it toward a nonzero jerk level. At the limiting smoothness $S=1$, the fitted trajectory is quadratic for zero $\mu$ and generally cubic for nonzero $\mu$ (if the cubic coefficient is nonzero).

The nonzero-reference model is an *exact affine change of variables*, not a newly invented statistical smoother. Take $p_{\mu,i}=\mu\binom{i-1}{3}$ with $D_3p_\mu=\mu\mathbf1$ and let $H_\lambda=(I+\lambda D_3^\top D_3)^{-1}$. Then

$$
\widehat\tau_{\lambda,\mu}
=p_\mu+H_\lambda(y-p_\mu).
$$

It is equivalent to applying zero-mean Whittaker smoothing to the cubic-detrended observations and restoring the cubic. This is useful for interpretation, but limits any theoretical novelty claim.

### Critical sensitivity of the sample mean

The manuscript uses $\widehat\mu=\operatorname{mean}(D_3y_{\mathrm{train}})$, not a fixed independently specified prior. Because $D_3=\Delta\circ D_2$,

$$
\boxed{
\widehat\mu
=\frac{1}{n-3}\sum_{i=1}^{n-3}(D_3y)_i
=\frac{(D_2y)_{n-2}-(D_2y)_1}{n-3}.
}
$$

**Important:** The estimated mean of all third differences telescopes to the difference between the *endpoint second differences*. Consequently, the plug-in reference is sensitive to errors in the first and last few measured positions, even though it is written as an average over all third differences. At $n=80$ training positions and $\Delta t=0.1$ s, it is especially important to compare this estimator to robust estimates and physical priors.

As an illustrative *noise model*, for independent positional measurement errors with variance $\sigma^2$, the two disjoint endpoint second differences imply

$$
\operatorname{Var}(\widehat\mu)
=\frac{12\sigma^2}{(n-3)^2}
\quad (n\ge6),
\qquad
\operatorname{Var}(\widehat j_{\mathrm{ref}})
=\frac{12\sigma^2}{(n-3)^2(\Delta t)^6}.
$$

These equalities do **not** assert that the NGSIM camera errors are independent. Real errors may be serially correlated and contaminated by systematic artifacts. The sample mean must not be described as a robust or physical truth estimator without evidence.

## What our archived pilot actually shows

The current `generated/empirical_summary.tex` and `generated/forecast_table.tex` record **one-second held-out position RMSE** at 15 overlapping origins in five vehicle segments:

- $d=3$, $\mu=0$: **0.583 m**;
- $d=3$, training-only $\widehat\mu=\operatorname{mean}(D_3y)$: **0.475 m**;
- constant-velocity extrapolation: **0.547 m**;
- Savitzky–Golay plus velocity extrapolation: **0.543 m**.

The five selection-criterion rows are nearly identical, so they are **not five independent replications**. These quantities assess **observed future position**, not an independently measured physical jerk signal. A difference in forecast RMSE can arise through the appended local polynomial extrapolator as well as through the historical smoothing; the current evidence does **not** show that physical jerk is estimated more accurately. It also cannot establish superiority across the vehicle population.

## Narrow novelty statement suitable for a future introduction

> We investigate the application of finite-difference penalized least squares with a nonzero reference mean of third differences to camera-derived longitudinal vehicle trajectories. In this formulation the penalty shrinks estimated jerk toward a reference level rather than necessarily toward zero. Building on the controlled-smoothness framework of Guerrero (2007, 2008), we compare zero and training-derived jerk-reference policies, examine their historical derivative estimates, and assess separately appended extrapolations on chronologically withheld vehicle positions. Unlike previous NGSIM quadratic-programming and spline reconstruction methods, our emphasis is the role of the reference difference mean within a common normalized-smoothness coordinate.

The contrast with prior studies must be checked in their **full methods**, particularly Fan et al. (2024); the wording above does not claim exclusive priority.

## Tests that could turn the observation into a defensible contribution

1. Expand from five segments to a larger sample of independent vehicles, periods, and datasets (e.g., highD/CitySim if licensing and harmonization permit).
2. Add **Fan et al. 2024** as a serious third-order trajectory-smoothing competitor, along with smoothing spline/V-spline, Kalman/GP jerk-prior and existing baseline methods. Validate consistent inputs and whether methods estimate positions or physical derivatives.
3. Predeclare the key ablation: $d=3$ with fixed $\mu=0$, plug-in raw $\widehat\mu$, robust/boundary-smoothed reference $\widehat\mu$, and oracle/reference-jerk values in *simulation*. Keep $S$ grids and extrapolation rules matched.
4. Use synthetic trajectories with *known jerk truth*: zero jerk, sustained nonzero jerk, piecewise jerk, acceleration changes, tracking errors, autocorrelated observation noise and outliers. Report **jerk RMSE**, historical position RMSE and future position RMSE separately.
5. Evaluate forecast improvements with per-vehicle/segment clustering or a paired block bootstrap; avoid treating overlapping origins as independent. Freeze policies before evaluating unseen vehicles.
6. Assess whether gain arises from improved historical trend fitting, from the cubic continuation term, or both. Compare extrapolators under matched fitted trajectories.
7. Document robustness to the endpoint telescoping identity and plot the distribution of $\widehat\mu/(\Delta t)^3$ in physical units.
8. Keep all code, configs, raw outcomes and figures in the repository as sequentially numbered experiments; do not overwrite the five-segment pilot.

## Handoff decision

**Assessment:** *Potentially distinctive applied formulation; universal first-use claim unverified.* Do not frame the main contribution as the first quadratic or third-difference approach to vehicle jerk. If robust vehicle-level evidence supports the nonzero-reference policy, a reasonable title direction is "Nonzero-Reference Jerk Regularization for Vehicle Trajectory Smoothing: A Smoothness-Indexed Penalized Least-Squares Study." Coauthors should approve literature scope, method comparisons and scientific claims before submission.

**No new empirical experiments or sources were downloaded/modified as part of this audit.**
