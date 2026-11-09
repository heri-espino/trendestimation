# Paper C Experiment007 — Does normalized PLS smoothness measure relative observation noise?

**Status:** Source-controlled preregistered experiment; interpret numerical results only after verifying a **successful Actions run and its archived \`run_manifest.json\`**. This is the next sequential experiment following completed Experiment006. It does not change any old NGSIM files, existing research branches, the public trendestimation API, or the Paper C manuscript.

The author requested a **focused empirical calibration test** of the *interpretability* of third-difference PLS smoothness, not another parameter-optimization benchmark.

## Hypotheses and terminology

Let \(n=80\), \(d=3\), \(m=n-d\), \(\Delta t=0.1\) s. Let \(D=D_3\), \(B=DD^\top\succ0\) and \(\delta_j>0\) denote the eigenvalues of \(B\). Under the independent Gaussian model

\[
y=\tau+\varepsilon,\quad
D\tau=\mu\mathbf1+u,\quad
\varepsilon\sim N(0,\sigma_\varepsilon^2 I_n),\quad
u\sim N(0,\sigma_u^2 I_m),
\]

the **variance ratio** is \(\lambda=\sigma_\varepsilon^2/\sigma_u^2\). Because \(u=\Delta t^3\,\xi\), where \(\xi\) is the true random jerk innovation with standard deviation \(\sigma_j\) m/s³, \(\sigma_u^2=\Delta t^6\sigma_j^2\). Thus

\[
\lambda_\mathrm{true}=
\frac{\sigma_\varepsilon^2}{\Delta t^6\sigma_j^2}.
\]

The normalized trace-based smoothness index in our library is

\[
S(\lambda)=\frac1m\sum_{j=1}^{m}
\frac{\lambda\delta_j}{1+\lambda\delta_j}.
\]

The terms are the fraction of each **third-difference spectral variance** attributed to measurement noise, under the model. Our theoretical target is therefore \(S_\mathrm{true}=S(\lambda_\mathrm{true})\). This is a **relative noise attribution**, not a percentage of clean observations and not absolute physical sensor precision \(1/\sigma_\varepsilon^2\).

For correlated noises and jerks, the scalar variance-ratio formula no longer gives the correct spectral decomposition. If \(C_\varepsilon=\operatorname{Cov}(D\varepsilon)\) and \(C_u=\operatorname{Cov}(u)\), define the **true covariance fraction**

\[
S_\mathrm{cov}=
\frac1m\operatorname{tr}[(C_u+C_\varepsilon)^{-1}C_\varepsilon].
\]

In the iid Gaussian model it **exactly equals** \(S(\lambda_\mathrm{true})\). Under AR(1) noise, AR(1) jerk, or randomized endpoint contamination it remains a precisely defined noise attribution but **not generally equal** to scalar-\(\lambda\) PLS \(S\). The sign-reversal regime additionally violates the constant-jerk-mean assumption.

Three predeclared hypotheses:

1. **Noise intervention:** with identical jerk innovation draws and jerk volatility held fixed, raising observation-error SD should raise theoretical and, *when identifiable*, fitted \(S\).
2. **Dynamics intervention:** with identical standardized observation noise and position-noise SD held fixed, raising real jerk-innovation SD should lower theoretical and, *when identifiable*, fitted \(S\).
3. **Ratio invariance:** raising both observation SD and jerk SD by the same factor preserves \(\lambda_\mathrm{true}\) and theoretical \(S\), **although absolute observation precision changes**. In particular, \((\sigma_\varepsilon,\sigma_j)=(0.05,2)\) and \((0.20,8)\) have exactly the same nominal variance ratio but the latter has **16 times larger observation variance**.

The experiment is **falsifiable**: if selected \(S\) does not reliably track the theoretical fraction when the assumptions hold, the proposed calibration is not supported; adverse behavior under misspecification must be reported.

## Data-generating processes

All trajectories are **new first-party synthetic series for Experiment007**, not repeated runs of Experiment005. We generate the true physical discrete jerk first and then integrate its third differences into a clean position:

\[
\Delta^3\tau_i=(\Delta t)^3 j_i,\qquad
j_i=j_0+\sigma_j u_i/\operatorname{SD}(u_i)
\]

where \(j_0=0.25\) m/s³. We initialize position \(0\) m, velocity \(18\) m/s, acceleration \(0\) m/s²; the iterative third-difference recurrence gives exactly the designated finite-difference jerk. Observations are \(y_i=\tau_i+\sigma_\varepsilon e_i\). The true clean position, noise values, third-difference jerk, seeds and every model selection are stored.

[config.json](config.json) freezes all levels:

| Factor | Levels |
| --- | --- |
| Observation-noise SD | 0.01, 0.05, 0.20 m |
| True jerk-innovation SD | 0.5, 2, 8 m/s³ |
| Jerk structure | iid Gaussian innovations; stationary AR(1), rho 0.7; iid innovations plus abrupt deterministic jerk sign reversal |
| Measurement errors | iid Gaussian; stationary AR(1), rho 0.65; iid Gaussian plus randomized ±4 SD contamination of the last historical observation |
| Training grid | n=80 observed positions at 10 Hz; d=3 |
| Pilot | 3 jerk structures × 2 independent parents × 3 jerk SD × 3 noise structures × 3 noise SD = **162 cases** |
| Confirm | 3 × 24 independent parent draws × 3 × 3 × 3 = **1,944 cases** |

**Crucial dependence design:** Every parent has a fixed standardized jerk-noise vector, fixed standardized observation-error vector, and fixed randomized endpoint-outlier sign; these are reused across all 27 factorial combinations for that parent. The 1,944 cases therefore contain only **72 independent stochastic parents** (24 per jerk structure), not 1,944 independent replicates. Pilot and confirm use separate deterministic SHA-256-derived seed namespaces. Valid uncertainty intervals resample entire parent vectors of paired treatments, not individual cells.

For the endpoint outlier, random sign makes the disturbance mean zero across parent replicates. Its **unconditional covariance** adds \(16\sigma_\varepsilon^2\) to the final measurement variance. The resulting non-Gaussian mixture violates the Gaussian REML model but retains a known theoretical covariance fraction. The sign reversal creates a nonconstant deterministic mean of jerk rather than a changed covariance; it is a separate structural model stress test.

## Smoothness selection rules

We apply four **existing** PLS selectors on the same 80 observed positions:

| Selector | \(\mu\) treatment | \(\lambda\) selection |
| --- | --- | --- |
| \`known_mu_reml\` | The known fixed generating jerk mean \(j_0\Delta t^3\) (**oracle-control only**) | Gaussian fixed-mean restricted likelihood, continuous numerical search |
| \`joint_reml\` | GLS mean profiled as \(\widehat\mu(\lambda)\) | Correct mean-adjusted Gaussian REML from Experiment006, continuous search |
| \`global_ols_plugin_mle\` | Cubic OLS coefficient estimated from the historical noisy positions | Fixed-mean Gaussian profile likelihood with plug-in \(\mu\), continuous search |
| \`gcv_zero_mu\` | Fixed zero | Classical GCV on the exact 15 normalized smoothness candidates from earlier Paper C studies |

The continuous routine evaluates 61 log-\(\lambda\) mesh points, refines every detected local minimum, and checks both 0 and infinity limits. **This is not a certified globally optimal search**; report boundary frequencies. GCV's discrete 15-point grid includes \(S=1\) but does **not** include \(S=0\).

For each method/trial, we save selected \(S\), \(\lambda\), discrete/physical reference jerk, covariance-fraction truth, \(S\)-calibration error, fitted historical jerk error against clean known jerk, observed/noise/innovation variance components where defined, method status and all input data. No oracle reference is presented as an estimator applicable to NGSIM.

## Statistical comparisons

1. **Calibration:** Spearman correlation between estimated \(S\) and true covariance fraction, mean bias, MAE, RMSE, frequencies of \(S=0\) and \(S=1\), and Gaussian-profile estimated noise variance relative to the known observation variance.
2. **Paired noise effects:** \(\Delta_\varepsilon S=\widehat S(0.20,\sigma_j)-\widehat S(0.01,\sigma_j)\), with identical standardized jerk and observation-noise draws.
3. **Paired dynamics effects:** \(\Delta_j S=\widehat S(\sigma_\varepsilon,8)-\widehat S(\sigma_\varepsilon,0.5)\); expected **negative** in the correctly specified model.
4. **Equal-ratio counterexample:** \(\widehat S(0.20,8)-\widehat S(0.05,2)\). The true population-covariance fraction is equal, while absolute sensor precision changes by a factor of 16.
5. **Misspecification:** Repeat every analysis for correlated measurement noise, correlated jerk innovations, randomized terminal outliers, and abrupt jerk-mean reversals. The stress-test behavior is not to be conflated with iid-model calibration.

The main inference is conditional on the **predeclared DGP**. For each method × dynamics × observation model × intervention, average the multiple repeated factorial contrasts *within the independent parent* before resampling parent indices (1,500 bootstrap replicates, deterministic seed). We also save all individual paired contrasts and within-parent three-level rank correlations. The intervals are **simulation Monte Carlo intervals**, not traffic-population or sensor-certification confidence intervals. Multiple methods/contrasts are explored without a claimed familywise multiple-testing guarantee.

## Run, generated directories and preservation

Cloud workflow: [\`paper-c-experiment007-cloud.yml\`](../../../../.github/workflows/paper-c-experiment007-cloud.yml).
Windows workflow: [\`paper-c-experiment007-pc08.yml\`](../../../../.github/workflows/paper-c-experiment007-pc08.yml).

The Windows runner PCAG103A-08 writes **every raw first-party simulation and result** under a new unique non-overwriting persistent directory:

~~~text
%USERPROFILE%\Documents\TrendEstimation-PaperC\experiment007\
  run-<GITHUB_RUN_ID>-a<ATTEMPT>\
    pilot\
      config.json
      theory_cells.csv
      trials.jsonl.gz                    # full known x, jerk, observation errors and y
      selections.csv                    # every estimated S/lambda/mu and jerk error
      per_cell.csv
      interventions.csv                 # complete paired observations
      effects_summary.csv               # parent-cluster bootstrap
      calibration_summary.csv
      summary.json
      RESULTS.md
      run_manifest.json
      figures\
        S_vs_observation_noise_*.png
        S_calibration_iid.png
    confirm\
      ... same complete structure ...
    metadata\
      source_commit.txt
      runner_name.txt
      requirements-resolved.txt
      data_provenance.txt
      file_inventory.json
    logs\
      preflight.log
      pilot.log
      confirm.log
~~~

All output files, directories, SHA-256 checksums, byte counts and source commit are enumerated under \`metadata/file_inventory.json\` (the inventory does not hash itself). The entire first-party synthetic data, model rows, plots and analyses are also pushed to an **immutable unique Git results branch** \`results/paper-c-exp007-pc08-<id>-a<attempt>\`. A separate GitHub-hosted run archives its identical-seed *independent computation* under \`results/paper-c-exp007-cloud-...\`. These are not additional independent observation samples, because the configured random seed streams are the same.

PowerShell from the repository root in the existing \`trendestimation\` Conda environment:

~~~powershell
conda activate trendestimation
$root = Join-Path $env:USERPROFILE "Documents\TrendEstimation-PaperC\experiment007\run-manual001"
if (Test-Path $root) { throw "Refusing to overwrite: $root" }
python -m pytest -q tests/test_paper_c_experiment007.py
python paper/ngsim-jerk-case-study/experiments/experiment007/run.py --stage pilot --output-dir "$root\pilot"
python paper/ngsim-jerk-case-study/experiments/experiment007/run.py --stage confirm --output-dir "$root\confirm"
python paper/ngsim-jerk-case-study/experiments/experiment004/inventory.py --run-root "$root" --status complete --output "$root\metadata\file_inventory.json"
~~~

No past Experiment004–006 data are read or rewritten during the new source-generation stage. Do not present generated source data as empirical NGSIM. Existing Paper C manuscript and unrelated Springer/CSDA work are untouched.

## What will justify the proposed manuscript language?

Only if fitted \(S\) shows **calibration and reliable expected monotonic paired changes under the correct iid Gaussian DGP**, together with **clearly reported limits under correlation, nonstationarity and contamination**, can Paper C reasonably describe the smoothing index as an **empirically calibrated relative spectral noise indicator under explicit assumptions**.

Even a perfect calibration cannot make \(S\) a measure of **absolute sensor precision**, because scaling both latent-innovation SD and observation SD equally leaves \(\lambda\) and \(S\) unchanged. Negative/mixed results should be preserved and should constrain claims rather than be hidden.
