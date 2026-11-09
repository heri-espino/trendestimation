# Paper C — Experiment005: known-jerk simulations and forecast attribution

**Status: COMPLETED on GitHub-hosted scientific runner (2026-11-08).** [Successful workflow #42547883064](https://github.com/heri-espino/trendestimation/actions/runs/42547883064) completed 96 pilot + 1,296 independent confirmation trials, preserved all first-party clean/noisy trajectories, and produced no invalid numerical rows. Read the [verified RUN_LEDGER.md](RUN_LEDGER.md) for actual results, scientific limitations, and the [full permanent Git results archive](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp005-cloud-42547883064-a1). **PCAG103A-08 remains a separate queued Windows execution at last check; do not claim VM computation or storage until verified.** The author explicitly authorized simulations, superseding the earlier real-only choice for Experiment004.

## Research questions

1. Can the \`trendestimation\` third-difference penalized least-squares (PLS) smoother recover a **known** physical jerk, not merely smooth noisy camera-derived positions?
2. How do **GCV versus the existing profiled Gaussian marginal likelihood** choose smoothness on the same finite \(S\) grid? The existing \`criterion="mle"\` is not joint likelihood estimation of \((\lambda,\mu,\sigma^2)\).
3. When does a **nonzero** third-difference mean improve the historical jerk estimate and/or future clean-position forecasting?
4. Is any improvement due to the historical **PLS fit**, to the separately added **cubic continuation**, or to both?
5. Do these results persist against **GCV cubic splines** and **Savitzky–Golay** under controlled, physically interpretable simulated measurement noise?

The experiment explicitly tests these questions. It does not assume that PLS or nonzero \(\mu\) is better.

## Mathematical model and known truth

Sample at \(\Delta t=0.1\) s, with 80 historical position observations and 20 future clean-position observations. Ground truth follows analytic jerk processes. For a piecewise-constant jerk process,

\[
j(t)=j_0+\sum_k\Delta j_k\mathbf1\{t\ge t_k\},
\]
\[
x(t)=x_0+v_0t+\tfrac12a_0t^2+
\tfrac{j_0}{6}t^3+\sum_k\tfrac{\Delta j_k}{6}(t-t_k)_+^3.
\]

For sinusoidal jerk \(j(t)=A\sin(\omega t)\), integrate it analytically to obtain exact position/velocity/acceleration and jerk. The full analytic \(x,v,a,j\) truth is stored for **every trial**, with its independently generated noisy observations.

We evaluate the discrete-jerk target

\[
j^{\mathrm{discrete}}_i=\frac{(D_3x_{\mathrm{true}})_i}{(\Delta t)^3},
\]

against the same difference operator applied to the fitted historical positions. This alignment is essential: at a jerk discontinuity, centered finite differences need not equal the instantaneous piecewise jerk at exactly one timestamp. The target is in m/s³ and exactly matches the finite-difference PLS functional.

## Predeclared study

[config.json](config.json) is the authoritative immutable scenario, noise, method, seed and output specification.

| Dimension | Design |
| --- | --- |
| Motion regimes | Zero jerk; constant \(+\!0.25\) and \(-\!0.25\) m/s³; sinusoidal jerk; sign reversal; finite braking-jerk pulse |
| Position noise (standard deviation) | 0.03, 0.12, 0.30 m |
| Noise structures | Independent Gaussian; AR(1) with \(\rho=0.65\); final training-point contamination (4σ) |
| Historical/future frame counts | 80 observed + 20 future, at 10 Hz |
| \(\mu\) policies | Zero; sample third-difference mean; global cubic OLS; last-25 cubic OLS; **known-truth oracle** (synthetic only) |
| PLS smoothing selection | In-sample GCV and conditional profiled Gaussian marginal ML on the exact same 15-point \(S\) grid |
| Forecast continuations | Algebraic last-three-point \(d=3\) recurrence; original local-25 quadratic continuation |
| External controls | Training-only GCV natural cubic smoothing spline; 21-point degree-3 Savitzky–Golay; raw local quadratic |
| Primary outcomes | Exact historical **jerk RMSE** (m/s³); future **clean-position RMSE** (meters) at 0.5/1/2 seconds |
| Secondary outcomes | Last-25 third-difference jerk MSE; historical clean-position MSE; reference-mean estimation bias |
| Causal attribution check | Fixed \(S=0.6\): crossed \(\mu_{\mathrm{fit}}\in\{0,\widehat\mu\}\) and \(\mu_{\mathrm{forecast}}\in\{0,\widehat\mu\}\) for sample and oracle references |
| Statistics | Scenario-stratified independent-seed paired bootstrap (1,000 replicates), **conditional on synthetic DGP**, not real-traffic inference |

### Two sequential stages

- **Pilot:** 6 regimes × 2 noise levels × 2 error structures × 4 independent seeds = **96 trials**.
- **Confirm:** 6 regimes × 3 noise levels × 3 error structures × 24 **different** seeds = **1,296 trials**.

Pilot and confirm use disjoint, deterministic SHA-256-derived random seeds. Full confirm must not run unless the pilot tests and complete-output checks pass. The confirm stage is **not** intended to select favorable methods based on the pilot; the full predeclared method grid is retained.

**Important design separation:** The synthetic oracle is an upper-bound control, not a candidate practical NGSIM estimator. Its \(\mu\) is computed from **clean historical positions only**, never from future truth. Real-data GCV or ML should not use clean truth or post-hoc future losses to set \(\lambda\).

## Persistent storage, with full trajectories

The PCAG103A-08 runner stores **everything** outside the temporary GitHub checkout:

~~~text
%USERPROFILE%\Documents\TrendEstimation-PaperC\experiment005\
  run-<GITHUB_RUN_ID>-a<attempt>\
    pilot\
      config.json
      trajectories.jsonl.gz          # All clean/noisy x,v,a,j per trial
      forecast_rows.csv              # Every method/trial/horizon
      jerk_rows.csv                  # Historical clean-position and jerk errors
      selection_rows.csv             # Every ML/GCV selected lambda/S/mu
      ablation_rows.csv              # Fixed-S 2x2 fit/future-reference crosses
      scenario_forecast_summary.json
      scenario_jerk_summary.json
      pooled_forecast_summary.json
      pooled_jerk_summary.json
      paired_bootstrap.json
      figures\forecast_rmse.png
      RESULTS.md
      run_manifest.json
    confirm\
      ...same entire structure, with independent seeds...
    build\
      ngsim.pdf
      ngsim.log
      build_manifest.json
    metadata\
      source_commit.txt
      runner_name.txt
      requirements-resolved.txt
      file_inventory.json
    logs\
      preflight.log
      pilot.log
      confirm.log
      compile.log
~~~

A recursive SHA-256 inventory records every generated directory/file and its exact persistent path. **Unlike third-party FHWA raw data, all synthetic first-party trajectories and complete numerical output files are eligible for versioned archival**: the Windows workflow pushes the full pilot/confirm directories (including compressed trajectory truth and all raw numeric rows) into a unique **results-only GitHub branch**. It also uploads an Actions artifact for shorter-term convenience, without replacing the permanent VM data.

When results grow beyond suitable Git limits, use Git LFS or documented external immutable storage rather than omitting information. No secrets or licensed private PDFs are committed.

## Reproduction

From the repository root on PCAG103A-08 in the existing \`trendestimation\` Conda environment:

~~~powershell
conda activate trendestimation
$root = Join-Path $env:USERPROFILE "Documents\TrendEstimation-PaperC\experiment005\run-manual001"
if (Test-Path $root) { throw "Refusing to overwrite $root" }
python -m pytest -q tests/test_paper_c_experiment005.py
python paper/ngsim-jerk-case-study/experiments/experiment005/run.py --stage pilot --output-dir "$root\pilot"
python paper/ngsim-jerk-case-study/experiments/experiment005/run.py --stage confirm --output-dir "$root\confirm"
python paper/ngsim-jerk-case-study/experiments/experiment004/inventory.py --run-root "$root" --status "completed" --output "$root\metadata\file_inventory.json"
~~~

The GitHub workflow [paper-c-known-jerk-simulations-pc08.yml](../../../../.github/workflows/paper-c-known-jerk-simulations-pc08.yml) additionally verifies output counts before starting confirmation, captures the exact environment and source SHA, compiles the existing Paper C LaTeX as a separate artifact, and pushes the complete results into a unique archive branch. The older Paper C experiments 001–004 and all Springer/CSDA work are preserved unchanged.

## Limitations and falsifiable outcomes

The main simulated comparisons depend on these **particular known-jerk generating processes, chosen noise levels, and fixed \(S\) grid**. Their uncertainty intervals describe variation across independently simulated seeds conditional on the experimental design; they do not establish traffic-population probabilities. Exact synthetic jerk accuracy does not establish accurate *real* jerk when NGSIM measurement noise, driver behaviors or sensor biases depart from the simulated mechanisms.

Possible outcomes include improved reference-jerk recovery only under constant jerk, zero-\(\mu\) superiority under sign changes or noisy boundary means, or spline superiority at longer forecast horizons. Report unfavorable cases and invalid estimates. Compare simulation mechanisms explicitly with the real observational [Experiment004 results](../experiment004/RUN_LEDGER.md). Do not claim general superiority, historical first use of \(d=3\) PLS, or that the profiled marginal ML implementation is the exact historical joint-mean MLE.
