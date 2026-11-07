# Mathematical lineage: Guerrero (2007, 2008) and Cortés-Toto et al. (2017)

**Source status:** The original Guerrero (2007) PDF was independently inspected on 2026-11-07, including printed pp. 1228 and 1233; see [direct forecasting-source annotation](guerrero_2007_forecasting_primary_source.md). Guerrero (2008) and Cortés-Toto et al. (2017) continue to use the existing [extracted literature](https://github.com/heri-espino/Trend-Estimation/tree/main/literature/extracted) and references; exact OCR-transcribed formulas remain subject to publisher-PDF checks.

## Guerrero (2007): the established PLS estimator

**Reference:** Víctor M. Guerrero, “Time Series Smoothing by Penalized Least Squares,” *Statistics & Probability Letters* 77:1225–1234, [DOI 10.1016/j.spl.2007.03.006](https://doi.org/10.1016/j.spl.2007.03.006).

For observed $y\in\mathbb R^n$ and a $d$-th forward-difference matrix $D_d$,

$$
\widehat\tau_{\lambda,\mu}
=\operatorname*{arg\,min}_{\tau}
\left\{\|y-\tau\|_2^2+\lambda\|D_d\tau-\mu\mathbf1\|_2^2\right\}.
$$

The model explicitly accommodates **nonzero mean of the differences**. The particular solution $p_{\mu,t}=\mu\binom{t-1}{d}$ obeys $D_dp_\mu=\mu\mathbf1$; hence
$\widehat\tau=p_\mu+(I+\lambda D_d^\top D_d)^{-1}(y-p_\mu)$.
At $\lambda\to\infty$, the fit lies in the affine class $D_d\tau=\mu\mathbf1$, allowing degree-$d$ polynomials if $\mu\ne0$.

**Critical extrapolation evidence:** Remark (v), printed p. 1228, **explicitly derives h-step trend extrapolation for d=1 and d=2 with nonzero $\mu$**. Equation (17) estimates $\mu$ from observed differences, and Example 2 (printed p. 1233) forecasts Mexico's GDP using a nonzero estimated second-difference mean. This means **PLS trend estimation followed by forecasting, including data-estimated nonzero $\mu$, is prior art from 2007**. See the [source-level annotation and the distinct d=3 extrapolation recurrence](guerrero_2007_forecasting_primary_source.md).

**Implication:** Our $\mu\ne0$ objective and generic trend extrapolation are **established mathematics**, not a new penalty, optimizer or forecasting paradigm. What remains worth testing is the physical third-derivative interpretation, specific local-continuation rule, software implementation and held-out evidence.

## Guerrero (2008): user-controlled percentage smoothness

**Reference:** Víctor M. Guerrero, “Estimating Trends with Percentage of Smoothness Chosen by the User,” *International Statistical Review* 76:187–202, [DOI 10.1111/j.1751-5823.2008.00047.x](https://doi.org/10.1111/j.1751-5823.2008.00047.x).

Guerrero's trace-based percentage smoothness provides an interpretable alternative to a raw $\lambda$. Paper C uses an $n-d$ normalized bounded coordinate

$$
S_d(\lambda)=\frac1{n-d}\sum_{j=1}^{n-d}
\frac{\lambda\delta_j}{1+\lambda\delta_j},\qquad
\delta_j>0.
$$

This is a rescaled **conditional** trace measure and is independent of fixed $\mu$. The paper's normalized scaling must be distinguished from Guerrero's original convention (which can have a different endpoint normalization).

**Implication:** S is useful for comparing degrees of smoothing across orders, not a new form of regularization or a guarantee of identical physical behavior at common S.

## Cortés-Toto, Guerrero & Reyes (2017): criterion selection

**Reference:** Daniela Cortés-Toto, Víctor M. Guerrero, Hortensia J. Reyes, “Trend Smoothness Achieved by Penalized Least Squares with the Smoothing Parameter Chosen by Optimality Criteria,” *Communications in Statistics—Simulation and Computation* 46:1492–1507, [DOI 10.1080/03610918.2015.1005236](https://doi.org/10.1080/03610918.2015.1005236).

Compares ordinary cross-validation (CV), generalized CV (GCV), corrected Akaike information criterion (AICc) and a residual-based BIC for finite-difference trend smoothing. Their simulation studies the **attained smoothness**, not NGSIM jerk fidelity.

Our paper additionally uses profiled Gaussian marginal ML. Under the published residual-based BIC form, the log-RSS contribution can be pathological as $\lambda\downarrow0$, so the current study's imposed $S\ge0.10$ boundary is an exploratory restriction, **not a mathematical repair**.

**Conditionality:** If $\widehat\mu=\operatorname{mean}(D_dy)$ is computed from the entire training window, the usual fixed-$\mu$ leverage-based CV is not exactly equal to refitting the plug-in mean for every leave-one-out sample.

## Essential claim boundaries

- The PLS family, nonzero $\mu$, classical criteria and user-selected smoothness all have statistical precedents.
- Our proposed distinct contribution is **interpreting $\mu/(\Delta t)^3$ as a jerk-reference level in observed vehicle trajectories**, with a careful empirical comparison and validation of what that policy changes.
- Reproducing the PLS fit or the normalized index alone is not evidence that estimated physical jerk is accurate.
