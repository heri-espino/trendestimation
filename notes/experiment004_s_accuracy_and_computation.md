# Experiment004 — Statistical accuracy, numerical reliability, and amortized S-domain computation

> **2026-10-28 scope revision (author-approved):** Exclude **d=0 entirely** from Experiment004. All design, pilot, validation, results, tables and subsequent full factorial run use **d=1,2,3,4,5,6** only. The historical d=0 discussions below document earlier planning and are not active requirements. The initial RMSE pilot is permitted now; large full-factorial runner jobs remain gated on validity review.


**Status (2026-10-28): design-only research protocol; no new timing or RMSE results.**
**Target context:** possible *Computational Statistics & Data Analysis* manuscript.
**Manuscript status:** do not rewrite or reformat the paper merely because this protocol exists.
**Ownership:** isolated research branch/PR; do not merge without review.

## 1. Research questions

1. At a shared set of normalized smoothness targets, how do **CV, GCV, AICc, BIC and Gaussian profiled marginal likelihood** differ in selected smoothness and *true latent-trend recovery error*?
2. How does this depend on difference order **d = 0,1,2,3,4,5,6**, series length, trend shape, seasonality, noise scale and serial correlation?
3. What are the **cold**, **prepared**, and **reuse-amortized** costs for SVD, symmetric diagonalization, banded Cholesky, general banded methods and specialized competitors?
4. How do **native S inversion per evaluation**, **once-mapped and cached S**, and an **independently chosen log-penalty grid** differ in cost, selected score, failures and evaluation count?
5. At what n/d/S values do eigenvalue mapping, finite-penalty factorization, trace/leverage and score calculations become numerically unreliable?

Do **not** claim S produces a statistically different estimator or necessarily a faster algorithm. For the same d, mu, criterion and exactly matched candidates, S and lambda are bijective coordinates: selected curves and true RMSE must agree up to numerical error.

## 2. Existing experiments — reuse rather than rerun blindly

- `notes/experiment002_full_s_factorial.md` and `paper/benchmarks/full_s_backend_criteria.py`: 7 backends x 5 criteria x d=0..5 x fixed mu=0/0.15; complete 17-point S grid with analytic 0 and 1 endpoints; numerical failures and criterion nonapplicability recorded.
- `paper/benchmarks/results/full_s_search_modes/` and `paper/sections/windows_full_s_results.tex`: **80,640 archived Windows records** for multiple search modes, repetitions and R=1/3/8. Do not overwrite or retrospectively relabel these results.
- `notes/experiment003_windows_findings_20261028.md` on branch `analysis/experiment003-windows-results-20261028` (PR #82, not necessarily merged): n=256..2048, d=2, M=21, R=4, banded eigenvalues-only and cached banded Cholesky vs full SVD, plus amortization as R grows. Source files on `experiment003/windows-local`. Do not silently combine these with old benchmark environments or claim that a *sum of timed phases* is independently timed end-to-end wall clock.
- `notes/criterion_coordinate_factorial.md`: matched grids vs independently spaced grids and existing derivative-CV searches.

Experiment004 should import, reference and analyze existing archives **before** deciding which cells need new computation.

## 3. Statistical specification

For equally spaced y in R^n, 0 <= d < n,

    tau_hat(lambda, mu) = argmin_tau ||y-tau||^2
                                + lambda ||D_d tau - mu * 1||^2
    Q_d = D_d.T @ D_d
    H_lambda = (I + lambda Q_d)^(-1)
    p_mu[t] = mu * binom(t,d),  t=0,...,n-1
    tau_hat = p_mu + H_lambda @ (y-p_mu)

D_0 = I, p_mu = mu * 1. The d=0 case is not a high-order-difference special case; it has a scalar-shrinkage structure.

The **normalized** index, distinct from the original Guerrero n-denominator index, is

    S_d(lambda) = (n-tr(H_lambda))/(n-d)
                = mean_j lambda*delta_j/(1+lambda*delta_j),
    S_d(0)=0, S_d(infinity)=1,

where delta_j are the n-d *positive* eigenvalues of Q_d, provided numerical rank is resolved.

**Two mean policies, explicitly separated:**

- `mu_fixed_zero`: fixed numeric mu=0, classical conditional criteria valid under their own assumptions.
- `mu_observed_difference`: mu_hat = mean(D_d @ y), computed per series. This is **not** mean(y), except for d=0; for d=1 it is mean first differences, for d=2 mean second differences. Existing classical scoring API rejects `mu="data"`; evaluating classical CV/GCV/AICc/BIC after freezing mu_hat into a number defines a **conditional plug-in heuristic**, **not** exact data-adaptive CV or an automatically valid EDF/AICc calculation. Label these cells `plug_in_conditional`. The existing MLE allows the plug-in but is **not joint MLE**.

An optional *separate* methodological subexperiment may derive and implement valid re-fitted-mu LOOCV, adjust the effective smoother/EDF under estimated mu and optimize mu jointly under the likelihood. It must not be silently assumed equivalent to conditional formulas.

**d=0 identifiability warning:** for any fixed mu and 0 < S <= 1,
tau_hat = (1-S)y + S mu*1, residual = S(y-mu) and H=(1-S)I.
Hence the *conditional* LOOCV and GCV scores are both mean((y-mu)^2), independent of interior S. At S=0 the usual 0/0 formulas are undefined. Therefore a d=0 CV/GCV `argmin S` is not uniquely identifiable; report ties or flat-score diagnostics rather than a spurious stable optimum. The implemented marginal MLE explicitly excludes d=0.

## 4. Requested S grid, including limits and tail stress

The **primary dense selection grid** is

    [0, 0.01, 0.02, ..., 0.99,
     0.995, 0.999, 0.9995, 0.9999, 0.99999,
     0.999999, 1-1e-8, 1-1e-10, 1-1e-12, 1]

Sort and deduplicate using exactly stored float64 decimal inputs; preserve their original decimal representation in metadata. That is 100 ordinary values + 9 listed finite tail values + 1 = **110 candidate S targets**. (Double-check through code before emitting results.)

Separate stress grid near 0: [1e-12, 1e-10, 1e-8, 1e-6, 1e-4, 1e-3, 0.005], merged with the primary grid only when explicitly requested. Never silently trim a difficult candidate to make a backend faster.

- S=0 -> lambda=0, tau_hat=y. CV and GCV are undefined at this interpolation endpoint; AICc/BIC and MLE follow their explicitly documented conventions.
- S=1 -> lambda=infinity, solved as an **analytic limit**, not a huge finite factorization. For d>=1, project y-p_mu onto degree-(d-1) polynomial nullspace and add p_mu; for d=0 the result is mu*1. Score limits must be criterion-specific.
- Extremely close finite S values may map to unrepresentable lambda or ill-conditioned A. Record `mapping_unrepresentable`, `conditioning_failure`, `score_undefined`, `factorization_failed`, or `ok` distinctly.

The S index is defined by the problem's difference matrix and n/d; the same S=0.8 across *different d* does **not** imply equal underlying trend geometry.

## 5. Two separate experimental layers

### A. Statistical accuracy against known truth

Fixed, public synthetic truth tau0 on normalized time t in [0,1].
Use several scientifically distinct functions:
1. smooth nonlinear (sine + low-order polynomial);
2. piecewise linear with a kink/change in slope;
3. smooth trend plus seasonal component (carefully designate which part is tau0 and which is nuisance);
4. polynomial or slowly varying monotone trend;
5. a stochastic smooth-trend process, with a saved generating seed.

Observed y = tau0 + epsilon. Error families include iid Gaussian and correlated AR(1) errors; for each shape examine at least two noise scales.
Use n in {64,128,256} for primary accuracy and enough **independent** random seeds (proposed >=100). Increase seeds adaptively based on uncertainty and runtime.
Pair every criterion/d/mu comparison on identical generated y and tau0. Do not pool technical timing repeats as independent simulated series.

For each selected S and fitted trend, archive:
- **latent trend RMSE** = sqrt(mean((tau_hat - tau0)^2));
- optional MAE, bias and boundary versus interior RMSE;
- selected S, lambda, criterion score, effective degrees of freedom;
- oracle S minimizing latent-trend RMSE **on the same candidate grid** for that d and mu policy;
- excess RMSE or risk over the grid oracle (state whether averaging RMSE or squared error);
- failure / no-unique-minimum / non-applicable / score undefined;
- true-generating parameters and explicit definition of latent truth.

Do not use RMSE(y, tau_hat) as a recovery-accuracy metric: the interpolating S=0 fit would trivially win. True-trend recovery is **not** forecasting performance; rolling-origin forecast RMSE would require a distinct horizon-specific evaluation.

### B. End-to-end and component runtime

Prioritize realistic n in {128,256,512,1024,2048}; reserve n>2048 for methods whose memory and complexity make the task feasible. For high d, record numerical stability rather than assuming all cells can be computed.

Vary R in {1,4,16,64} independent observed series reusing a fixed (n,d,S-grid). Compare:
1. **cold** construction, mapping and scoring on each series;
2. **prepared backend** reuse of structure but no mapped S cache;
3. **cached S map**: compute all candidate lambda once per (n,d,grid), then reuse across mu, criteria and series;
4. **cached factorizations** for the same mapped lambda grid in addition to the cached map;
5. **per-search native S** inversion, for a fair same-grid control;
6. **log-lambda** candidate grid, SAME mapped penalties, for an exact statistical-equivalence control; and independently spaced log-lambda grid ONLY for different candidate-distribution experiments.

Do not double-count shared mapping cost for each criterion, mean or solver when it is physically constructed once. Also provide **standalone** cost of one S-based search where the map cannot yet be amortized.

Record actual **monolithic end-to-end wall-clock measurements** as primary results. Component timers (matrix assembly, spectral preparation, band eigenvalues, inverse roots, factorization, scoring, reconstruction, candidate selection) are secondary diagnostics. Do not call sums of separately measured median phase times actual end-to-end wall-clock.

Backends:
- full SVD of D;
- symmetric eigendecomposition of Q (with rank/conditioning QA);
- dense Cholesky (small n only);
- general banded solve;
- genuine banded Cholesky;
- **structured trace / selected-inverse approach** for GCV, comparable to Weinert (2007), if faithfully implemented and independently validated;
- a DCT-based special-purpose comparison inspired by Garcia (2010) only under **mathematically identical** difference operators and boundary conditions. Garcia's original DCT smoother uses a different boundary operator from ordinary forward D_d, so never treat its output as an exact baseline for our estimator without showing equivalence.

Score-specific costs differ: CV requires leverage diagonals, GCV/AICc/BIC need EDF and RSS, and MLE needs a valid marginal likelihood quadratic + determinant. Do not make MLE pay for unnecessary CV quantities or make banded methods solve dense identity matrices without disclosing their non-specialized baseline status.

Compare **shared S candidate grid vs repeated mapping** separately from **continuous numerical optimization**. The latter needs matched tolerances, function-evaluation budgets, multistart diagnostics, and a dense validated grid as a reference, not claims that a local Brent optimizer proves global optimality.

## 6. Priority staging / computational budget

**Stage 0 — reference and QA:** No new timed work. Parse the archived 80,640-cell Experiment002 results and Experiment003, inventory exact coverage, freeze matching source SHA/config/protocol, check the user-provided PDFs including Weinert (2007), Cortes-Toto et al. (2017), Biessy (2026) and Garcia (2010 + 2012 corrigendum).

**Stage 1 — smoke/correctness:** n=32/64, d=0..6, a few representative S targets including S=0/1 and 1-1e-8, fixed mu plus observed-difference plug-in, all five criteria where applicable. Check analytic limits, scores, fitted curves, S inversion, tie behavior, and failures; do not publish these as timing benchmarks.

**Stage 2 — accuracy pilot:** n={64,128}, 20 independent seeds, 2 trend shapes, iid/correlated noise, 5 criteria, 7 orders, two mean policies, full 110-point grid, trusted spectral reconstruction. Determine RMSE uncertainty and reasonable full-simulation budget.

**Stage 3 — performance pilot:** n={128,512}, d={0,2,4,6}, R={1,4,16}, selected backends; both cold and complete mapped/reused workflows, whole-call timers; begin specialized trace competitor. This helps identify meaningful break-even regions.

**Stage 4 — publication run:** after reviewing pilot validity, extend seeds (~100 or more), n and R; randomize timings in paired blocks, log one BLAS thread and optional additional threading regime; measure independent host sessions. Run only validated combinations, logging numerical failures and excluded cells explicitly.

**Stage 5 — plots and synthesis:** archive all raw CSV/Parquet, environment.json, config.json, selected parameter/error tables, QA failures, per-stage stopwatch data, figure sources, PDF/SVG (AwesomeFigures), SHA256 manifest and dated interpretation. Do not overwrite existing runs. Use a separate results branch or run-specific directory and open a reviewable PR, never silently merge.

### Minimum QA

- At matched candidate penalties, all numerical backends must agree on tau, criterion score and EDF (where defined) to tolerance justified for n/d/S, not a universal fixed epsilon.
- Selected S and latent-trend RMSE must match between mathematically identical native and premapped searches.
- A backend is not a valid whole-grid speed winner when it fails one or more required candidates.
- d=0 CV/GCV tie detection and d=0 MLE N/A are mandatory regression tests.
- Extreme high-order near-one condition numbers and underflow/overflow are reported, not concealed.
- Cache keys use n, d, exact grid, dtype and operator/boundary convention; the mapping does **not** depend on y or mu when those conventions are fixed.
- Isolate experimental measurement overhead and hardware drift; randomize order, keep paired seeds, report numbers of independent simulated datasets and technical repeats separately.
- Log any use of `mu="data"` and conditional-versus-reestimated mean assumptions without presenting pseudo-LOOCV as exact.

## 7. Publication positioning and readings

This experiment aims to establish **statistical and numerical tradeoffs under a unified smoothness-indexed interface**, not the invention of CV, GCV, finite-difference PLS, Cholesky, or the smoothing index.

- Weinert, H. L. (2007). *Efficient computation for Whittaker–Henderson smoothing*. CSDA 52, 959–974. https://doi.org/10.1016/j.csda.2006.11.038 — specialized structured algorithms and GCV trace computation; essential fair baseline. Note his fidelity/roughness weighting uses an inverse penalty convention relative to ours.
- Cortés-Toto, D., Guerrero, V. M. & Reyes, H. J. (2017). *Trend smoothness achieved by penalized least squares with the smoothing parameter chosen by optimality criteria*. Communications in Statistics — Simulation and Computation 46, 1492–1507. https://doi.org/10.1080/03610918.2015.1005236 — fixed-mu classical selection comparisons and original Guerrero index, with different normalization from our S.
- Biessy, G. (2026). *Whittaker–Henderson smoothing revisited: A modern statistical framework for practical use*. ASTIN Bulletin. https://doi.org/10.1017/asb.2025.10061 — likelihood, penalized statistical interpretation, banded/reduced-rank algorithms; its likelihood choices must not be conflated with our profiled Gaussian criterion.
- Garcia, D. (2010). *Robust smoothing of gridded data in one and higher dimensions with missing values*. CSDA 54, 1167–1178. https://doi.org/10.1016/j.csda.2009.09.020 — DCT-based GCV and comparative algorithm engineering; DIFFERENT boundary conditions. Its 2012 corrigendum, https://doi.org/10.1016/j.csda.2011.12.001, corrects a singularity/positive-definiteness argument. Do not repeat the original paper's blanket O(n^3) statement for properly implemented fixed-bandwidth Cholesky.

## 8. Decision gate before the CSDA rewrite

Complete Stage 0 and Stage 1, determine whether the original 80,640-cell archive already addresses each proposed comparison, and only then run new calibrated simulation/timing workloads. After valid results, select a manuscript claim; do not draft claims based on hoped-for speedups or hoped-for RMSE improvements.
