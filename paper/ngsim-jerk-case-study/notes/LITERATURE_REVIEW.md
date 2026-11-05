# Literature review — nonzero-reference PLS and observed vehicle trajectories

**Paper C:** NGSIM US-101 jerk-oriented PLS application. **Reviewed 2026-11-05.** Research synthesis; no new manuscript result or verified claim of being the first.

## 1. Research question and vocabulary

Let $y_i$ denote recorded longitudinal position (meters), $\Delta t=0.1$ seconds, and $D_d$ a discrete forward-difference matrix of order $d$. **Jerk** is the third time derivative of position, $j(t)=x'''(t)$, approximated by $(D_3x)_i/(\Delta t)^3$. **PLS** is quadratic penalized least squares; **reference jerk** is the center toward which a third-difference penalty shrinks. **Physical feasibility** means satisfying explicitly stated kinematic bounds—not just reducing large derivatives.

The exact Paper C estimation problem is

$$
\widehat\tau_{\lambda,\mu}
=\operatorname*{arg\,min}_\tau
\{\|y-\tau\|_2^2+\lambda\|D_3\tau-\mu\mathbf1\|_2^2\}.
$$

Our principal distinction to investigate is the **role of nonzero $\mu$** in an already established smoother. It is **not** enough to say “jerk has not been smoothed before.”

## 2. What each research family contributes

| Research family | Representative study | Method / meaning of smoothness | Input and evidence | Direct distinction or danger |
| --- | --- | --- | --- | --- |
| Statistical PLS and interpretable smoothing | [Guerrero 2007/08; Cortés-Toto et al. 2017](papers/guerrero_cortes_2007_2017.md) | Square residual + squared deviations of $d$-th differences from $\mu$; degree-of-smoothing index; CV/GCV/AICc/BIC | General time series and simulations | **Nonzero $\mu$ already exists.** Our new claim must be applied, not foundational. |
| NGSIM derivative-aware filtering | [Marczak & Buisson 2012](papers/marczak_buisson_2012.md) | I-spline reconstruction and comparisons with Butterworth, sEMA, local regression and Kalman filters | NGSIM I-80; jerk-threshold and sign-reversal diagnostics | Jerk diagnostics and spline smoothing of NGSIM are **not new**; overtuning can delete stops. |
| Position/velocity spline reconstruction | [Cao et al. 2021](papers/cao_2021.md) | Cubic Hermite **V-spline**, $\int\lambda(t)\{f''(t)\}^2dt$, adaptive penalties and CV | Separate measured positions **and velocities**; simulations and tractor GPS | Acceleration regularization, irregular-time treatment and more input variables; not same centered jerk penalty. |
| Probabilistic jerk-driven motion prior | [Tang et al. 2019](papers/tang_2019.md) | Continuous-time Gaussian process on $SE(3)$ with white noise on jerk | Pose/velocity/acceleration, lidar odometry | Zero-mean jerk noise induces a **constant-acceleration mean**, not our nonzero reference jerk. |
| Physically constrained NGSIM smoothing | [Fan, Jin & Yin 2024](papers/fan_2024.md) | Two sequential QPs: discrepancy then roughness, hard derivative limits and prior position-error bounds | NGSIM + highD, third-order derivative constraints; existence/uniqueness results | **Closest predecessor.** Our unconstrained single PLS has different shrinkage and no hard feasibility guarantee. |
| Emergency-event-preserving trend filtering | [Zhu et al. 2024](papers/zhu_2024.md) | Two-stage $\ell_2$ position/velocity fusion followed by $\ell_1$ acceleration trend filtering with physical constraints | CitySim and downstream LSTM prediction assessment | Quadratic/absolute trend filters in traffic are existing prior art; assess whether our $\ell_2$ shrinkage erases maneuvers. |

## 3. Literature-derived conclusions

1. **Well established:** noisy vehicle-position data amplify errors in differentiated speed, acceleration and jerk; traffic researchers have long applied classical and optimization-based smoothing, including direct NGSIM experiments. Marczak and Buisson explicitly used jerk distributions and limits in 2012.
2. **Also established:** quadratic trajectory reconstruction and jerk-related third-order constraints; Fan et al. provide a particularly close 2024 comparator. A paper claiming “first use of jerk regularization” would be factually unsafe.
3. **Also established:** $\lambda\|D_d\tau-\mu\mathbf1\|^2$ with nonzero $\mu$; Guerrero developed this general framework. Cortés-Toto et al. studied its selection criteria. A new PLS model cannot be claimed solely because $\mu\ne0$.
4. **Potentially distinctive under current search:** a controlled-smoothness study of a **position-only** NGSIM third-difference PLS model with an explicitly compared **training-derived nonzero jerk reference** and strictly chronological position holdouts. None of the primary items read here explicitly reports that exact combination, but an exhaustive priority search has not been completed.
5. **Competing philosophy:** Fan seeks hard kinematic feasibility; Zhu preserves abrupt changes via an $\ell_1$ layer; Cao incorporates separate velocity and adaptive local roughness; Tang uses a continuous-time stochastic motion model. Paper C should articulate *why a global soft jerk reference is scientifically useful despite these alternatives*.

## 4. What current Paper C demonstrates—and does not

The repository holds five deterministically selected NGSIM **US-101** vehicle segments, 80-frame training windows, three chronological forecast origins per segment and 0.5, 1 and 2-second holdouts. For $d=3$ at the one-second horizon, the generated summary reports:
- **0.475 m** future-position RMSE for training-derived $\widehat\mu=\operatorname{mean}(D_3y)$;
- **0.583 m** for fixed $\mu=0$;
- **0.547 m** constant velocity, **0.543 m** Savitzky–Golay/velocity and **0.626 m** constant acceleration.

This is an approximately 18.5% difference between the two PLS policies **within this selected pilot**, not a population effect with independent uncertainty. The 15 origins overlap; the five selection criteria can yield nearly identical fits. The estimate is **position forecast error**, not ground-truth jerk error. Forecasts are produced by a separately appended local polynomial after fitting—not natively by PLS.

The normalized $S$ grid is identical across policies, so the empirical comparison is interpretable in terms of conditional degrees of smoothing, but $S$ does not make $d=2$ and $d=3$ curves geometrically identical.

## 5. Where the article can contribute

**Narrow empirical hypothesis:** A data-informed nonzero reference third difference improves trend and derivative reconstruction or short-horizon extrapolation when vehicles exhibit locally sustained nonzero jerk, relative to zero-jerk shrinkage.

**Counterhypothesis:** The training-derived mean is dominated by noisy endpoint second differences, while a globally constant jerk reference erases real changes in driving behavior; any observed position gain comes mainly from cubic extrapolation rather than improved jerk estimation.

**Required discriminating evidence:** known-jerk simulation, predeclared vehicle-level holdouts, common data and tuning budgets, separate estimates of true jerk and future position, and honest comparison with physically constrained and spline-based baselines. See [mathematical notes](MATHEMATICAL_NOTES.md) and [manuscript plan](MANUSCRIPT_PLAN.md).

## 6. Proposed related-work narrative

Vehicle trajectory filtering has progressed from local averaging and smooth regression to algorithms that explicitly consider higher derivatives, measurement error and feasible driving dynamics. Marczak and Buisson (2012) benchmarked I-spline and classical filters on NGSIM data using jerk-related diagnostics. Cao et al. (2021) incorporated measured velocity and adaptive acceleration penalties into a V-spline, while Tang et al. modeled a continuous-time jerk-driven Gaussian-process motion prior. More recently, Zhu et al. (2024) combined quadratic and absolute trend filtering with kinematic constraints to preserve abrupt changes, and Fan et al. (2024) established a two-stage, physically constrained quadratic-programming method for NGSIM longitudinal trajectories. The present work instead studies Guerrero-style finite-difference PLS with a reference mean of third differences. It contrasts zero and training-derived reference jerk within a shared smoothness index and evaluates separate extrapolation rules on chronologically held-out positions. This is a comparison and physical interpretation of an established estimator, not a claim that quadratic smoothing or jerk modeling is novel.

**Review boundary:** That paragraph is a recommended draft grounded in the examined sources. Confirm the publisher full text of Fan et al., coauthor preferences and numerical scope before inserting it into the LaTeX manuscript.
