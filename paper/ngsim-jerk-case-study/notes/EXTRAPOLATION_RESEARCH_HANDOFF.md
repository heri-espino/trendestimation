# Paper C — extrapolation with third-difference PLS and nonzero reference jerk

**Updated:** 2026-11-05. **Status:** A research and agent handoff plus [one deterministic algebra regression test](../tests/test_reference_jerk_extrapolation.py); no new statistical experiments, forecast results, LaTeX manuscript claims, or submissions. The current five-vehicle evidence is unchanged.

## Question to test

> Does a position-only, smoothness-indexed PLS trend with \(d=3\) and a **training-estimated nonzero reference jerk** provide more accurate and more physically informative extrapolations than the same smoother centered at \(\mu=0\)?

The strongest possible paper is an **application- and forecasting-focused evaluation** of this question, not the first demonstration of PLS, nonzero \(\mu\), third-order smoothing, or extrapolation generally.

### Status of originality claims

| Claim | Current assessment | Basis |
| --- | --- | --- |
| First PLS model with \(\mu\ne0\) | **False** | Guerrero (2007) studies the general nonzero-mean finite-difference penalized estimator. |
| First use of PLS/Whittaker–Henderson for extrapolation | **False as a broad claim** | Biessy (published online 2025; 2026 volume) Section 7 explicitly develops Whittaker–Henderson extrapolation, including consistency constraints and uncertainty intervals. |
| First jerk-aware vehicle trajectory smoother | **False as a broad claim** | Marczak–Buisson (2012), Fan–Jin–Yin (2024), Zhu et al. (2024), and others use jerk-based diagnostics, constraints or filters. |
| First use of third differences with nonzero mean on NGSIM for independently appended local polynomial extrapolation | **Not established** | No exact match was identified in the earlier targeted search, which was neither exhaustive nor designed to prove worldwide priority. |
| A new *empirically validated benefit* from choosing \(\mu\) for jerk-oriented vehicle extrapolation | **Hypothesis to test** | Only 5 selected vehicle segments and 15 overlapping historical origins are currently archived; jerk ground truth is unavailable. |

**Additional decisive source check (2026-11-07):** [Guerrero (2007), original printed pp. 1228 and 1233](papers/guerrero_2007_forecasting_primary_source.md) **already derives and empirically uses PLS trend forecasting with estimated nonzero $\mu$ for $d=1,2$**. The 2020 Ramos-Ibarra–Silva environmental forecasting paper applies controlled smoothing with $d=2,\mu=0$. Our implementation's $d=3$, local-last-25-points rule and physical reference-jerk comparison are different, but **the act of forecasting from PLS is not new**. A distinct Python package feature combination needs a package-by-package comparison, not a claim that no other Python Whittaker smoother exists.

**Prior-art priority update (publisher verified on 2026-11-05):** Guillaume Biessy, *Whittaker–Henderson smoothing revisited: A modern statistical framework for practical use*, *ASTIN Bulletin*, 56(1):1–31 (January 2026), DOI [10.1017/asb.2025.10061](https://doi.org/10.1017/asb.2025.10061), online 3 September 2025. Its [Section 7](https://www.cambridge.org/core/journals/astin-bulletin-journal-of-the-iaa/article/whittakerhenderson-smoothing-revisited-a-modern-statistical-framework-for-practical-use/237E3C12164917F768932FDBC2079100) extends a weighted smoother onto unobserved positions with zero observation weights and consistency constraints. **This is distinct from our specific local-polynomial continuation**, but it prevents any blanket “first PLS extrapolation” statement. Read the full paper and supplement for method-level comparison before submission. This was an additional public-source check, not a newly replicated computation.

## What the present repository actually implements

Read [run_case.py](../run_case.py), particularly \`continuation\`, \`run_forecasts\`, and \`choose\`. The current experiment is **already implemented**, not only proposed:

- Observations: 5 FHWA NGSIM US-101 tracks, positions at 10 Hz; training window \(n=80\), 3 overlapping historical origins per track.
- Candidate orders \(d=1,2,3,4\), with a shared 16-point normalized smoothness grid \(S_d(\lambda)\).
- Two reference policies: \(\mu=0\) and \(\widehat\mu_d=\operatorname{mean}(D_dy_{\rm train})\), each *computed on training data only*. For \(d=3\), \(\mu/\Delta t^3\) has reference-jerk units.
- Five in-sample selectors: CV, GCV, AICc, restricted residual BIC, and profiled marginal ML. With data-derived \(\mu\), fixed-\(\mu\) CV is **conditional**, not fully refitted leave-one-out CV.
- **After fitting** the training trend, \`continuation(trend,order,mu,horizon)\` subtracts a particular degree-\(d\) solution \(\mu\binom{t}{d}\), fits a degree-\((d-1)\) polynomial to the final **25 fitted observations**, predicts future points, then adds back \(\mu\binom{t}{d}\) at future indices.
- Forecasts are evaluated at \(h=5,10,20\) frames against **withheld recorded position**, not latent jerk or noise-free position.

**Important:** The code's extrapolation mechanism is **ours as a separately appended heuristic**. The library's PLS fit does not itself produce forecasts. Do not claim an integrated predictive state-space model, calibrated intervals, or the existence of a unique extrapolation prescribed by the PLS objective.

### Current descriptive evidence (not rerun)

At \(d=3\), 1-second horizon, the archived summary reports an RMSE of **0.475 m** for training-derived \(\mu\) and **0.583 m** for \(\mu=0\); constant-velocity, Savitzky–Golay/velocity, and constant-acceleration baselines have RMSE **0.547 m**, **0.543 m**, and **0.626 m** respectively. These are historical **future-position** errors for a limited data sample. They are not jerk-estimation errors, independent repetitions of random vehicles, or a valid population-wide superiority claim.

## Mechanism: why nonzero \(\mu\) matters for continuation

For \(d=3\), \(D_3\tau\) estimates jerk multiplied by \((\Delta t)^3\). Thus \(\mu\ne0\) favors nonzero reference jerk. In the infinite-penalty limit:

- \(\mu=0\): the estimated historical trend is quadratic in time; continuation is constant-acceleration motion.
- fixed \(\mu\ne0\): the estimated trend is a degree-3 polynomial with constant nonzero reference jerk; continuation can express cubic displacement.

At finite \(\lambda\) the historical trend is not generally polynomial. The future curve is determined by the separately specified local fit, its window length, chosen \(S\), and the reference \(\mu\). This creates a critical **causal attribution problem**: a gain may result from better historical smoothing, from adding the cubic future term, from a changed selected \(S\), or from interactions among selection and extrapolator design. See [exact decomposition](EXTRAPOLATION_DECOMPOSITION.md).

## Competing explanation and testable predictions

**Thesis:** If the motion has approximately sustained nonzero jerk over the training/forecast boundary, a correctly estimated reference jerk reduces a constant-acceleration extrapolation bias.

**Antithesis:** If driver behavior changes abruptly, a constant jerk reference can extrapolate the wrong dynamic regime. If the reference is a raw mean of third differences, it is unusually sensitive to boundary tracking errors; apparent gains may come from extrapolation geometry rather than true jerk recovery.

**Synthesis:** Test a **factorial ablation** of smoothing reference versus continuation reference, with a fixed \(S\) grid, an independently designed vehicle-level evaluation, and simulations with known jerk. We should aim to characterize **when and why** the reference policy helps or harms.

### Operational priorities

1. **No new journal submission until attribution is resolved.** The key direct-competitor literature is [the annotated review](LITERATURE_REVIEW.md); Biessy is the newly verified direct PLS-extrapolation predecessor.
2. **First next study:** [experiment001 design](EXTRAPOLATION_ABLATION_PLAN.md) separates the fitted trend from cubic continuation; measure position and known-truth jerk separately.
3. **Next:** [\(\mu\) policy catalogue](MU_POLICY_CATALOG.md) compares raw mean, stable training-only regression estimates, robust fits and an oracle-only simulation control.
4. **Then:** independent-vehicle replication and serious prior baselines (Fan's constraints, appropriate spline, GP/Kalman motion prior), not another overlapping five-origin pilot.
5. Save **every** script, seed, configuration, raw result, figure, failure status and analysis to the repository under sequential \`experiment001\`, \`experiment002\` ... paths. Continue existing artifact numbering if new work is added; never overwrite the present case-study outputs.
6. A future agent must consult [AGENTS.md](../../AGENTS.md), [publication map](../../PUBLICATION_MAP.md), and current branch/PR ownership before editing shared files. This is **only** Paper C, not Springer Experiment011.

## Suggested defensible contribution statement (provisional)

> We study a third-difference penalized least-squares smoother with a training-derived reference jerk for longitudinal vehicle trajectories. We distinguish its effect on historical trend estimation from the effect of a separately specified cubic continuation, and test whether the choice of reference mean improves chronological position forecasts and simulated jerk recovery.

**What is not claimed:** first PLS forecasting; first jerk smoothing; globally optimal \(\mu\); hard physical feasibility; calibrated predictive uncertainty; or universal improvement. Confirm exact priority against the full related literature and obtain coauthor approval before adopting a novelty claim.
