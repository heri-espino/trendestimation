# Paper C Experiment006 — joint unknown-mean REML and forecasting-oriented mu

**Status:** Source-controlled, testable study launched on the GitHub-hosted scientific runner and on designated PCAG103A-08 Windows self-hosted runner. A completed job and validated run manifest are required before reporting any numerical result. The first pilot computation evaluated all 96 trials but exposed a bootstrap-config lookup error before writing reports; that bug was fixed and both workflows retriggered, preserving previous failure logs.

## Research question and scientific isolation

Can the existing PLS reference mean \(\mu\) be *estimated jointly with smoothing* instead of using a raw/sample/global-OLS plug-in, and does that improve reconstruction of known jerk and out-of-sample forecasting?

This is the sequential next experiment following [Exp005 known-truth simulations](../experiment005/RUN_LEDGER.md) and [Exp004 real NGSIM](../experiment004/RUN_LEDGER.md). All original trajectories, experimental code, figures, scientific conclusions and the broader paper repo are **unchanged**.

The numerical comparison uses the **identical 96 pilot and 1,296 confirmation trajectories** saved in the verified Experiment005 branch, as well as **the same 200 recorded NGSIM episodes** originally downloaded for Experiment004. No synthetic episodes are regenerated, no different noise realizations are substituted, and real NGSIM is never treated as having known jerk. Every data source has a SHA-256 hash and a precise Git or VM provenance path. This is a *matched reanalysis*, not an independent replication with new drivers/noise draws.

## Mathematical specification

For a full-row-rank \(D=D_3\in\mathbb R^{(n-3)\times n}\), let \(m=n-3\), \(v=Dy\), \(B=DD^\top\succ0\) and \(W_\lambda=I_m+\lambda B\). The Gaussian variance-ratio model is

\[
v\sim N(\mu\mathbf1,\sigma_u^2W_\lambda),\quad
\lambda=\sigma_\varepsilon^2/\sigma_u^2.
\]

**Joint unknown-mean REML** (one additional eliminated nuisance mean direction) is

\[
\widehat\mu_\lambda=
\frac{\mathbf1^\top W_\lambda^{-1}v}
{\mathbf1^\top W_\lambda^{-1}\mathbf1},
\quad
r_\lambda=v-\widehat\mu_\lambda\mathbf1,
\]
\[
F_R(\lambda)=\log|W_\lambda|
+\log(\mathbf1^\top W_\lambda^{-1}\mathbf1)
+(m-1)\log\left(\frac{r_\lambda^\top
 W_\lambda^{-1}r_\lambda}{m-1}\right).
\]

Estimate lambda by minimizing the profile score, then set \(\widehat\mu=\widehat\mu_{\widehat\lambda}\), and fit the existing \`TrendSmoother\` with the pair \((\widehat\lambda,\widehat\mu)\). **This is not the same as replacing mu in the old fixed-mu likelihood without adjusting the REML degrees of freedom.** See [fixed-mu equivalence and unknown-mu derivation](../../notes/GUERRERO_GAUSSIAN_REML_EQUIVALENCE.md).

\`reml.py\` precomputes the symmetric spectral decomposition of \(B\), so each likelihood/analytic derivative evaluates in \(O(n-d)\) time instead of repeating matrix inverses. The search is across 61 predeclared log-lambda points covering normalized \(S\in[0.0001,0.9999]\), with refinement of *all observed local minima* and explicit evaluations of \(\lambda\to0^+\) and \(\lambda\to\infty\). It is an **auditable approximate global search, not a proof that no narrow interior minimum was missed**. The boundaries represent covariance-model limits; if lambda=0 wins, the fitted historical curve is unsmoothed and physical jerk should be treated with caution.

## Six comparison policies

| Name | How lambda is selected | How mu is selected |
| --- | --- | --- |
| \`joint_reml_continuous\` | Continuous mean-adjusted REML search | GLS mean depending on lambda, estimated jointly |
| \`joint_reml_grid\` | Correct mean-adjusted REML on the earlier 15-value smoothness grid | Same GLS mean |
| \`fixed_zero_continuous\` | Continuous fixed-mu Gaussian profile likelihood | Zero |
| \`plugin_sample_continuous\` | Continuous fixed-mu profile likelihood | Mean of the noisy third differences |
| \`plugin_global_ols_continuous\` | Continuous fixed-mu profile likelihood | Global training-only cubic OLS reference |
| \`shrink_tscv\` | Lambda from joint REML on full history | \(\alpha\widehat\mu_\mathrm{REML}\), with alpha selected from \(\{0,0.5,1\}\) via **training-only rolling-origin forecast CV** |

Each policy uses both third-order \`guerrero_last3\` and 25-point local polynomial continuations, at 5/10/20 future frames. The sixth policy has a **different training-only alpha for each forecast rule/horizon**; it is deliberately forecast-oriented, not another REML solution.

### Nested validation protection

The alpha selection uses internal prefix-based folds, each of which independently fits joint REML to its **own history**. The folds have origins [45,55,65] for horizons 5/10 and [40,50,60] for horizon 20, always satisfying origin+horizon ≤ 80. A prediction at fold origin \(o\) is scored against observations \(y_{o+1:o+h}\), all inside the **outer 80-point history**. There is no access to the held-out outer future when fitting lambda, mu or alpha.

Since the PLS fit and both continuation operators are affine in mu at fixed lambda, evaluating \(\alpha\) by interpolation between mu=0 and mu=mu_REML forecasts is **exact**, not a speed/accuracy approximation. Each fold refits lambda+mu before these two endpoint forecasts.

### Archived competitors and inference

We read the existing Experiment005/004 **unchanged individual forecast records** and label them \`archived:...\`. Key comparisons include \`archived:spline_gcv_taylor2\`, \`archived:pls_mle_zero_local25\`, and \`archived:pls_mle_ols_global_local25\`. Their original scoring targets, seeds and episode IDs are retained, and the new source hashes are recorded. New and original forecasts use identical frames and units.

Simulation truth: historical finite-difference jerk \(D_3x_\mathrm{clean}/0.1^3\), plus future clean-position errors. The oracle mu from Experiment005 is **never** used by any Experiment006 candidate. The scenario-stratified paired Monte Carlo bootstrap (500 replicates, fixed seed 20261109) is conditional on the deliberately selected simulated generating processes.

Real NGSIM: future **recorded** positions only; real physical jerk remains unknown. There are 200 episodes but only five coarse capture-session proxies in the selected sample. We use a **block-resampling sensitivity analysis**, explicitly **not a reliable population-level 95% CI or hypothesis test** given this tiny number of blocks. No multiple-comparison correction or globally best method claim is justified by these repeated methods/horizons.

## Exact archive and VM files

The frozen prior synthetic data come from:
\`results/paper-c-exp005-cloud-42547883064-a1\`,
at \`paper/ngsim-jerk-case-study/experiments/experiment005/runs/cloud-42547883064-a1/{pilot,confirm}/trajectories.jsonl.gz\`.
Previous synthetic baseline forecasts sit in each stage's \`forecast_rows.csv\`.

The verified prior NGSIM data remain at:
\`%USERPROFILE%\Documents\TrendEstimation-PaperC\experiment004\run-42538556206-a1\data\`,
with earlier forecast outcomes at \`...\results\forecast_rows.csv\`. **No raw FHWA NGSIM pages or positions are copied into the new Git branch**; they remain externally documented and source-hashed.

New Windows output is non-overwriting:

~~~text
%USERPROFILE%\Documents\TrendEstimation-PaperC\experiment006\
  run-<GITHUB_RUN_ID>-a<ATTEMPT>\
    pilot\
      selections_rows.csv
      forecasts_rows.csv
      jerk_rows.csv
      cv_rows.csv
      summary.csv
      paired_comparisons.csv
      run_manifest.json
      RESULTS.md
    confirm\       # same files, independent archived confirm seeds
    real\          # same files; jerk errors explicitly unavailable
    metadata\
      source_commit.txt
      runner_name.txt
      requirements-resolved.txt
      experiment005_source_path.txt
      experiment004_source_path.txt
      file_inventory.json
    logs\
      preflight.log
      pilot.log
      confirm.log
      real.log
~~~

All generated files/directories receive a **relative path, byte length and SHA-256** in \`metadata/file_inventory.json\`, using the existing Experiment004 inventory helper. The full new scored rows, selected parameters, validation losses, analyses, logs and provenance are also committed under a unique immutable \`results/paper-c-exp006-pc08-...\` Git branch; an additional Actions artifact lasts 90 days.

The [hosted scientific workflow](../../../../.github/workflows/paper-c-joint-reml-cloud.yml) separately evaluates the synthetic pilot/confirm from the archived source branch and archives **all newly generated results** under \`results/paper-c-exp006-cloud-...\`. The Windows workflow [paper-c-joint-reml-pc08.yml](../../../../.github/workflows/paper-c-joint-reml-pc08.yml) evaluates both synthetic and real records on PCAG103A-08, placing the complete output on the VM. Results from different machines use identical source data/seeds; do not count them as independent trajectories.

## Run manually on the university VM (PowerShell)

~~~powershell
conda activate trendestimation
$root = Join-Path $env:USERPROFILE 'Documents\TrendEstimation-PaperC\experiment006\run-manual001'
if (Test-Path $root) { throw "Refusing to overwrite $root" }
$previousSim = Join-Path $env:USERPROFILE 'Documents\TrendEstimation-PaperC\experiment005\run-42547250403-a1'
$previousReal = Join-Path $env:USERPROFILE 'Documents\TrendEstimation-PaperC\experiment004\run-42538556206-a1'
python -m pytest -q tests/test_paper_c_experiment006.py tests/test_paper_c_experiment006_run.py

python paper/ngsim-jerk-case-study/experiments/experiment006/run.py --mode synthetic --stage pilot --source "$previousSim\pilot\trajectories.jsonl.gz" --archived-forecasts "$previousSim\pilot\forecast_rows.csv" --output-dir "$root\pilot"
python paper/ngsim-jerk-case-study/experiments/experiment006/run.py --mode synthetic --stage confirm --source "$previousSim\confirm\trajectories.jsonl.gz" --archived-forecasts "$previousSim\confirm\forecast_rows.csv" --output-dir "$root\confirm"
python paper/ngsim-jerk-case-study/experiments/experiment006/run.py --mode real --stage real --source "$previousReal\data" --archived-forecasts "$previousReal\results\forecast_rows.csv" --output-dir "$root\real"

python paper/ngsim-jerk-case-study/experiments/experiment004/inventory.py --run-root "$root" --status complete --output "$root\metadata\file_inventory.json"
~~~

The workflow additionally records the full Python dependency snapshot, Git commit SHA, all tool logs and permanent branch links.

## What future agents should do

1. Read this protocol, [config.json](config.json), the old exact REML proof, and the first successful new \`run_manifest.json\`; do not claim the job completed based solely on a submitted workflow.
2. Check \`selections_rows.csv\` and boundary counts; many S=0 or S=1 choices would signal model/test sensitivity. Compare joint REML *grid vs continuous* to separate mean-adjustment from numerical optimization.
3. Analyze true jerk RMSE and future-position RMSE **separately**. Contrast with recorded-position NGSIM, where true jerk was not available.
4. Compare alpha selection by regime/horizon, and test whether a nonzero GLS reference is useful in sustained jerk but harmful at reversals. Avoid post-hoc choices on the final evaluation.
5. Preserve all source archives and results, including unfavorable regimes and failed runs, in separate append-only run branches.
6. Keep PRs #121–125 and their respective ownership unchanged. Do not merge or submit a manuscript without author approval.
