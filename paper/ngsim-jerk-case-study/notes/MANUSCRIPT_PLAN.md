# Paper C — manuscript annotations and next experiments

**Purpose:** Working notes and an action-oriented outline for the **existing** NGSIM paper; **not** a rewrite of the current LaTeX, an experiment report, or a submission decision.

## 1. Key message to test

**Candidate contribution:** A comparison of zero-jerk and training-derived, potentially nonzero reference-jerk shrinkage within finite-difference PLS, evaluated on observed vehicle trajectories using a common bounded smoothness coordinate and independent checks of derivative behavior.

Avoid “first to estimate jerk,” “first PLS for vehicles,” “first nonzero mean smoother,” “proved superior,” “physically feasible” and “ground-truth jerk reconstruction.” No available evidence supports those broad claims.

## 2. Suggested manuscript structure

1. **Introduction:** Why NGSIM positions imply noisy higher derivatives; scope of our estimator and its *nonzero jerk reference*. Cite Guerrero (PLS) and the close traffic predecessors.
2. **Related work (new subsection):** Arrange the literature by objective: classical filtering / I-splines (Marczak), Hermite velocity splines (Cao), GP motion prior (Tang), $\ell_2$–$\ell_1$ trend filters (Zhu), hard-constrained two-step QP (Fan). Explain *both* overlap and differences, without asserting unverified first use.
3. **Methods:** Define discrete differences and $\Delta t$ physical units, exact $\mu=0$ versus $\widehat\mu$ policies, normalized $S$, conditional CV caveat, and explicit polynomial *forecast extrapolator*. Add the mean-telescoping identity.
4. **Results:** Keep the archived five-segment pilot as an **exploratory case**, with actual holdout position RMSE and method baselines. Distinguish the jerk plot from a measured jerk signal.
5. **Discussion:** Whether nonzero reference helps when jerk is sustained; sensitivity to first/last three position samples, loss of abrupt maneuvers, unconstrained physical derivatives and five-vehicle evidence limit.
6. **Conclusion:** Concise scope of the *tested application*, not a universal method ranking.

## 3. Recommended brief introduction paragraph (draft, subject to coauthor review)

> Classical finite-difference penalized least squares permits both zero and nonzero reference means of the penalized differences (Guerrero, 2007), while the associated degree of smoothing can be expressed through a trace-based index (Guerrero, 2008). In transportation research, derivative-aware filtering of NGSIM positions has been evaluated with I-splines and jerk diagnostics (Marczak and Buisson, 2012); more recent approaches include velocity-informed V-splines (Cao et al., 2021), jerk-driven continuous-time motion priors (Tang et al.), combined quadratic and absolute trend filtering (Zhu et al., 2024), and two-stage physically constrained quadratic programming (Fan et al., 2024). We study the specific effect of centering a third-difference PLS penalty on zero versus a training-derived reference jerk, and assess its historical trend estimates and separately extrapolated future positions. The model is an application of established regularization rather than a new smoothing family.

## 4. Most useful experiments, in reproducible sequence

### Proposed experiment001 — known-truth jerk and endpoint sensitivity (**not run**)

**Question:** Does $\widehat\mu$ reduce true jerk estimation error, and when is it unstable?

- Generate physically interpretable time series: constant velocity, constant acceleration, sustained nonzero jerk, piecewise jerk, abrupt braking and smooth acceleration changes.
- Fix time grids and declare independent or AR-correlated position noise plus optional endpoint outliers, with seeds stored in a machine-readable configuration.
- Compare $d=3$ PLS with $\mu=0$, raw training $\widehat\mu$, robustified reference estimates and known-reference oracle *only in simulation*. Match $S$ grids and search budgets.
- Report **jerk RMSE**, in-sample position RMSE, physical-bound violations, event retention, forecast RMSE for each fixed extrapolation rule and sensitivity to endpoint perturbations.
- Save one record per seed, scenario, method and horizon, plus numerical validity flags, dependencies and plots; do not overwrite the existing five-vehicle pilot.
- Next gate: determine whether a nonzero-reference benefit survives after holding the extrapolator fixed.

### Proposed experiment002 — independent vehicle-level evaluation (**not run**)

**Question:** Is any gain stable across drivers/vehicles/maneuvers, not just overlapping windows?

- Expand to predeclared train/test vehicles and possibly highD or CitySim after reviewing their licensing and data definitions.
- Freeze hyperparameters and estimator policies before evaluating previously unseen vehicles; do not make 15 overlapping origins count as independent replicates.
- Compare with position-only spline, Savitzky–Golay, Kalman/GP WNOJ and a documented implementation of Fan et al. where valid; include equal-data and extra-velocity-input scenarios distinctly.
- Report per-vehicle paired improvements and cluster/bootstrap uncertainty, plus relative change from a held-out predeclared benchmark.
- Preserve full data provenance, consent/license attribution, hashes, source code, CSVs and plots in a new results branch.

### Proposed experiment003 — physically constrained or adaptive reference (**not run**)

Assess a locally varying or state-space jerk reference or derivative-bound-constrained PLS **only after** experiment001/002 diagnose a failure mode. Such a change is a **new model**, not merely changing the interpretation of the published fixed-$\mu$ estimator. Compare against physical plausibility and avoid creating a second novelty claim before numerical evidence.

## 5. Immediate editorial tasks (no new computation required)

- Insert verified citation records into the paper's BibTeX, then cite them from a short related-work section.
- Figure captions: keep “estimated jerk proxy” and sampled-position/units; label all empirical RMSE as **future position** or **historical position**.
- Explain the final-degree difference between $\mu=0$ quadratic and $\mu\ne0$ cubic limiting trends.
- State explicitly that a reference-level penalty is **soft**, unlike Fan/Zhu kinematic bounds.
- Check all publisher-specific citations against the final article before submission.
- Preserve the current TeX, generated tables, figures, source downloads, experiment notes and journal templates.

## 6. Publication decision gate

Do not submit solely because the five-vehicle pilot shows lower short-horizon position RMSE for plug-in $\mu$. Require an independent vehicle sample, a direct strong comparator and a well-defined outcome for *jerk* or explain why the target is instead *position forecasting*. Get both authors' approval of novel claims and overlap with other TrendEstimation papers.
