# Paper C — candidate reference-mean policies for \(d=3\)

**Status:** Research options for future experiments, not existing public library features or proven accurate estimators. Keep all \(\mu\) computations strictly on the available **training window**. The current NGSIM code implements **only \(\mu=0\) and \(\mu=\operatorname{mean}(D_dy)\)**.

## Definitions and units

For equally spaced positions \(y_t\) in meters at \(\Delta t=0.1\) s, the third-difference PLS penalty shrinks \(D_3\tau\) toward the **scalar** \(\mu\). The physical reference jerk is

\[
j_{\rm ref}=\mu/(\Delta t)^3 \quad [\mathrm{m/s^3}].
\]

Even if \(\mu\) is estimated from data, \(\mu\) is **held fixed during a conditional PLS solve**. Estimating it jointly or allowing \(\mu_t\) to vary creates a different model/selection problem and needs separate validation.

## Policy registry (proposals, not results)

| Policy ID | Training-only definition | Statistical motivation | Principal risk | Status |
| --- | --- | --- | --- | --- |
| \`zero\` | \(\mu_0=0\) | Explicit constant-acceleration reference; necessary control | Bias under sustained nonzero jerk | **Implemented** |
| \`sample_mean\` | \(\widehat\mu_{\rm raw}=(n-3)^{-1}\mathbf1^\top D_3y\) | Guerrero-style plug-in; estimates average third difference | **Telescopes to endpoint second differences**; noisy or anomalous boundary positions | **Implemented** |
| \`cubic_ols_global\` | Fit \(y_i\approx a+b u_i+c u_i^2+e u_i^3\) by least squares on the training window; set \(\widehat\mu=6e(\Delta t)^3\) | Uses all training positions to estimate average sustained jerk | A globally constant jerk is wrong for piecewise maneuvers; residual outliers | Proposed |
| \`cubic_ols_tail\` | Same polynomial fit using a **predeclared** final \(k\) training positions | Targets the dynamics near the forecast origin | Larger variance for short \(k\); sensitive to near-end artifacts; degree-3 extrapolation instability | Proposed |
| \`cubic_robust_tail\` | Fit a degree-3 polynomial using a specified robust M-estimator (e.g., Huber loss) on last \(k\); \(\widehat\mu=6e(\Delta t)^3\) | Reduces sensitivity to gross position errors near the boundary | Threshold/scale choice, non-Gaussian bias; robustness is empirical, **not guaranteed** | Proposed |
| \`smoothed_endpoint\` | Apply a **training-only** prefilter to position, then \(\widehat\mu=(D_2\widetilde y_{\rm end}-D_2\widetilde y_{\rm start})/(n-3)\) | Controls boundary noise while retaining a mean-difference interpretation | A new pre-smoothing hyperparameter; possible nested tuning/leakage | Proposed |
| \`median_third_diff\` | \(\operatorname{median}(D_3y)\) (or predeclared trimmed mean) | A low-cost comparator resistant to isolated large derivative values | Adjacent third differences are correlated and error-amplified; can remove genuine short-lived jerk events | Proposed, not guaranteed robust for tracking artifacts |
| \`oracle_jerk\` | Known \(\mu=(\Delta t)^3 j_{\rm true}\) from a **synthetic data-generating model** | Separates estimation error from the value of a nonzero reference | **Never available in actual NGSIM**; must not enter real holdouts | Simulation-only control |
| \`dynamic_mu_t\` | Time-dependent reference \(m_i\) from a dynamic model or time-varying optimization | Allows driver regime transitions | **Different estimator family**, changes penalties, EDF and proofs; not part of existing paper | Future theory, not experiment001 default |

### Algebraic diagnostic for the current sample mean

Let \(n\ge6\) and \(D_d\) denote forward differences. Then

\[
\widehat\mu_{\rm raw}
=\frac{\sum_{i=1}^{n-3}(D_3y)_i}{n-3}
=\frac{(D_2y)_{n-2}-(D_2y)_1}{n-3}.
\]

Therefore this particular policy actually uses **only the first and last three positions** after cancellation. Its sensitivity is **not** equivalent to averaging \(n-3\) independent observations.

For i.i.d. additive position noise with variance \(\sigma^2\), a mathematical noise-model calculation gives \(\operatorname{Var}(\widehat\mu_{\rm raw})=12\sigma^2/(n-3)^2\) for \(n\ge6\). That formula is **not** an empirical NGSIM measurement-error estimate.

### Why an OLS cubic is different

With actual time \(u_i=(i-i_{\rm end})\Delta t\), fit \(y_i=a+bu_i+cu_i^2+eu_i^3+\epsilon_i\). For a true degree-3 polynomial trajectory, \(d^3x/dt^3=6e\); consequently the implied reference in **discrete position units** is \(\widehat\mu=6e(\Delta t)^3\).

Unlike \(\operatorname{mean}(D_3y)\), an OLS cubic generally uses interior positions as well as boundary positions. That changes the estimator's noise behavior and bias under noncubic dynamics. It is **not** a “fixed but user-chosen \(\mu\)”; its data dependence also affects effective degrees of freedom and selection scores.

### Recommended initial comparison

Use only a **small, prespecified set** to avoid overfitting the pilot: \`zero\`, \`sample_mean\`, \`cubic_ols_global\`, \`cubic_ols_tail\`, \`cubic_robust_tail\`, plus \`oracle_jerk\` **in synthetic data only**. Freeze the last-\(k\) window (a candidate is \(k=25\), matching the current extrapolator), robust loss tuning and \(S\) candidate set **before evaluation on held-out vehicles**.

Do not call the new policy “optimal \(\mu\)” until you define a population loss, an information set, a selection algorithm, numerical stability checks, and genuine out-of-sample evaluation. Do not tune \(\mu\) on the same future positions later used as the test.

## Recommended machine-readable schema for future data

Every trial should save \`experiment_id\`, \`seed\`, \`dataset\`, \`track_id\`, \`origin\`, \`horizon\`, \`dt\`, \`n_train\`, \`d\`, \`smoothing_S\`, \`selector\`, \`mu_policy\`, \`mu_discrete\`, \`mu_jerk_m_s3\`, \`tail_k\`, \`robust_loss\`, \`fit_reference_policy\`, \`continuation_reference_policy\`, \`forecast_rule\`, \`forecast_mse_m2\`, \`jerk_mse_m2_s6\` (synthetic only), \`is_heldout\`, \`validity_status\`, \`code_sha\`, and \`data_sha256\`.

Distinguish **measured** evaluation rows from **planned** parameter combinations.
