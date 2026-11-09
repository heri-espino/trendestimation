# Paper C — experiment004: expanded real NGSIM evaluation

**Status:** Source-controlled implementation, requiring successful PCAG103A-08 run to establish numerical results. No simulations.

## Scientific question

Compare third-difference PLS with **GCV** and the library's **profiled Gaussian marginal-likelihood criterion (API: mle)**, both for a zero and a training-derived third-difference reference mean, to familiar trajectory filters.

Eight PLS methods result from GCV/profile ML × zero/sample mu × three-point/local-25 continuation. Three controls are a training-only GCV natural cubic smoothing spline with quadratic Taylor continuation, Savitzky–Golay endpoint derivatives with quadratic Taylor continuation, and local quadratic polynomial extrapolation from raw positions. Methods use 80 historical samples, a predeclared forecast origin at index 100, and horizons 0.5, 1, and 2 seconds.

**Likelihood qualification:** The repository's src/trendestimation/likelihood.py computes a profile Gaussian marginal likelihood on the penalized spectral coordinates (REML-style), with an unknown observation variance profiled out. A data-derived mu is used **conditionally**, not jointly maximum-likelihood estimated. This is the implemented criterion, not an independent proof of equivalence to any different Guerrero likelihood specification.

## Data collection and quality controls

Official FHWA/USDOT [NGSIM trajectories](https://data.transportation.gov/d/8ect-6jqj), DOI [10.21949/1504477], 10-Hz longitudinal positions. Location-specific, vehicle-ID-bounded, offset-paginated API queries retrieve US-101 and I-80. Every original byte of each CSV source page is stored on the VM with its original URL, SHA-256, byte count and download manifest.

Episodes are defined by **site, numeric vehicle ID, first timestamp**, 100-ms time continuity and consecutive frame IDs. The provider warns that Vehicle_ID can repeat and repeated IDs **are not associated**. Episode identity is not certified unique physical vehicle identity. The prespecified historical speed QC uses only observations **before** the forecast cutoff. The selection rule takes up to 100 early qualifying episodes per site (or fewer when unavailable), without choosing trajectories by forecast error. It is a convenience sample, not a population-random sample.

## Metrics and inference

For every method/episode/horizon, save future recorded-position MSE (m²), MAE (m), and endpoint displacement error (m), invalid statuses, selected lambda, selected smoothness, mu in discrete units and m/s³, and criterion score. Summarize by location and both combined with explicit valid denominators.

Compare episode-paired mean squared errors against the GCV spline, with 2,000 bootstrap resamples **stratified by site**, a fixed seed, and explicit limitations: overlapping horizons within episodes, shared traffic/video scenes, nonrandom sampled episodes, and multiple comparisons. These are exploratory intervals; neither actual latent position nor physical jerk is independently observed. No true-jerk RMSE claim is supported by this experiment.

## Persistent VM directories and filenames

The canonical full-data location is **outside GitHub Actions' ephemeral checkout**, under:

~~~text
%USERPROFILE%\Documents\TrendEstimation-PaperC\experiment004\
  run-<GitHub run ID>-a<attempt>\
    data\
      raw\us-101\page0000.csv, ...
      raw\i-80\page0000.csv, ...
      selected_positions.csv
      episode_catalog.json
      download_manifest.json
    results\
      forecast_rows.csv
      selection_rows.csv
      summary.csv
      paired_bootstrap.csv
      RESULTS.md
      run_manifest.json
    build\
      ngsim.pdf
      ngsim.log
      build_manifest.json
      ...
    logs\
      download.log
      evaluate.log
      compile.log
    metadata\
      source_commit.txt
      requirements-resolved.txt
      file_inventory.json
~~~

The inventory explicitly lists **every generated directory** and every file, with VM-relative path, bytes and SHA-256 (excluding itself). The download manifest provides the exact official API query and byte-level hash for each raw page. Files are **never overwritten** within a run ID. The workflow mirrors the smaller complete tables, manifest, log, environmental versions and file inventory into an **isolated results-only Git branch** for agent access. Raw NGSIM pages remain on the persistent university VM as documented external storage, not as committed oversized Git files. Note: a VM is not an off-site backup; long-term preservation requires a second audited copy if the VM will be retired.

## Reproduction (PCAG103A-08)

~~~powershell
conda activate trendestimation
$root = Join-Path $env:USERPROFILE "Documents\TrendEstimation-PaperC\experiment004\run-manual001"
if (Test-Path $root) { throw "Refusing to overwrite an existing run" }
python paper/ngsim-jerk-case-study/experiments/experiment004/fetch_real_ngsim.py --data-dir "$root\data"
python paper/ngsim-jerk-case-study/experiments/experiment004/evaluate.py --data-dir "$root\data" --output-dir "$root\results"
python scripts/build_papers_pc08.py --paper ngsim --output-dir "$root\build" --require-runner
python paper/ngsim-jerk-case-study/experiments/experiment004/inventory.py --run-root "$root" --status complete --output "$root\metadata\file_inventory.json"
~~~

The GitHub workflow paper-c-real-ngsim-gcv-mle-pc08.yml runs the same pipeline on the designated Windows runner and preserves a separate result branch plus an Actions archive. It does not alter existing experiment001–003 data, Springer Experiment011 or anyone else's branch.

## Handoff

- Verify the **actual workflow success and manifest counts** before reporting how many episodes were acquired or any numerical result. A target of 200 episodes is NOT an observed count.
- Check raw source-page hashes, selected episode uniqueness and repeated-ID caveat; investigate failed methods without silently dropping rows.
- Read the full VM result inventory and run-specific Git results branch. Keep all future changes reproducible and sequential.
- Do not make strong physical jerk, worldwide novelty, or population significance claims based solely on NGSIM future recorded positions.
- Preserve all raw pages, every outcome row, scripts, configs, paper and logs. No simulation should be introduced without a separate author decision.
