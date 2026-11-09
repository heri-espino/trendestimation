# Experiment004 — verified PCAG103A-08 run ledger

**Status:** **COMPLETED, 2026-11-08 local Mexico time** (manifest UTC 2026-11-09T00:10:04Z).
[GitHub Actions run #42538556206](https://github.com/heri-espino/trendestimation/actions/runs/42538556206)
completed successfully, including data download, Python unit tests, expanded real-data forecast comparison, the existing NGSIM LaTeX build, and recursive SHA-256 file inventory.

## Data locations and preservation

**PCAG103A-08 persistent root:**

    C:\Users\175199\Documents\TrendEstimation-PaperC\experiment004\run-42538556206-a1

Full raw page bytes, the selected-position CSV, all 6,600 errors, 800 parameter-selection records, bootstrap comparisons, compiled PDF, logs and package freeze remain under this VM path.

**Permanent Git result index / compact full outcomes:** [results-only branch](https://github.com/heri-espino/trendestimation/tree/results/paper-c-exp004-pc08-42538556206-a1/paper/ngsim-jerk-case-study/experiments/experiment004/runs/pc08-42538556206-a1). It contains the complete forecast and model-selection rows, FHWA query/page hashes, episode catalog, statistical comparisons, logs, environment snapshot and [file inventory](https://github.com/heri-espino/trendestimation/blob/results/paper-c-exp004-pc08-42538556206-a1/paper/ngsim-jerk-case-study/experiments/experiment004/runs/pc08-42538556206-a1/metadata/file_inventory.json). The *raw official downloaded CSV pages* stay on the VM and are indexed as external storage, **not** committed into Git. An Actions artifact is retained for 90 days. The original five-track experiment and its manuscript outputs were not overwritten.

The recursive inventory lists **38 actual generated files in 8 data/build/log/metadata directories** (approximately 34.2 MB before inventory bytes). The two source-site downloads each fetched **10 pages × 20,000 rows**, 400,000 original NGSIM position records total. Both site queries hit the configured **page cap**, not full API exhaustion; the last possibly truncated contiguous episode per site was excluded from selection. Every source page's query, exact count, byte length and SHA-256 is in the retained data/download_manifest.json. The selected-position file SHA-256 is:

    e6b594edd0cde7165302c4c7b65720645ec940122af23152db24f7eb1230598e

The source SHA for the *executed* code is **265f3e17fb3aabfcac608661c2e2f661ae578519**. Scientific scripts and method definitions were not altered after this execution; later commits only add notes/handoffs.

## Selection and statistical grouping

- **200 real recorded episodes:** 100 I-80 and 100 US-101, first quality-qualified episodes by ascending vehicle ID and timestamp, from the downloaded page caps.
- **113 distinct (location, integer Vehicle_ID) pairs, not 200 certified physical vehicles.** Some IDs recur across recording sessions; USDOT's source explicitly says repeated Vehicle_ID values are not necessarily associated.
- The 200 episodes span just **five coarse 15-minute recording-time proxy groups**: I-80 groups of 45 and 55; US-101 groups of 24, 38, 38.
- One prespecified origin index 100 per episode, using the preceding 80 historical positions and 0.5/1/2-second recorded future positions.
- 11 methods × 3 horizons × 200 episodes = **6,600 valid errors, 0 failed**, and 4 PLS selection policies × 200 episodes = **800 valid selection records**.
- The complete comparison summary has 99 location/method/horizon rows and 30 paired exploratory episode-bootstrap rows. Bootstrap seed 20261108 and 2,000 site-stratified episode resamples.

**Statistical independence warning:** only five recording-time proxy groups means simultaneous or correlated traffic episodes are not independent population units. The episode bootstrap assumes more independence than the data necessarily support. Its confidence limits are **descriptive/sensitivity intervals, not verified population-level significance tests**. Manuscript claims should not promote nominal episode-level confidence to traffic-population confidence without a more appropriate recording-block design.

## Results: future recorded-position RMSE (m)

| Method | 0.5 s | 1.0 s | 2.0 s |
| --- | ---: | ---: | ---: |
| **GCV cubic smoothing spline, quadratic Taylor continuation** | **0.135427** | **0.348043** | **0.878735** |
| PLS, profiled Gaussian ML, mu=0, last-three-point recurrence | 0.143349 | 0.512384 | 1.868646 |
| PLS, GCV, mu=0, last-three-point recurrence | 0.145254 | 0.516648 | 1.880504 |
| PLS, profile ML, training-derived mu, last-three-point recurrence | 0.145743 | 0.531006 | 2.014156 |
| PLS, GCV, training-derived mu, last-three-point recurrence | 0.147630 | 0.535176 | 2.025396 |
| PLS, GCV, mu=0, local-25 continuation | 0.340639 | 0.618422 | 1.344673 |
| PLS, GCV, training-derived mu, local-25 continuation | 0.316623 | 0.576409 | 1.353547 |
| Savitzky–Golay, quadratic Taylor | 0.354719 | 0.850622 | 2.410597 |

**Main result:** A GCV cubic smoothing spline with quadratic Taylor continuation has the smallest **pooled overall RMSE at all three horizons**. The earlier five-segment PLS advantage does not generalize to this expanded convenience sample. PLS profile ML changes performance only modestly relative to GCV in this configuration; the nonzero reference is also not universally favorable.

**Exploratory paired ΔMSE at 1 s:** PLS profile-ML, mu=0, last-three recurrence minus GCV spline has mean **+0.14140 m²** and stratified episode-bootstrap interval **[+0.04375,+0.25759] m²**, favoring the spline. At 0.5 s the same interval is **[-0.00694,+0.01101] m²**, compatible with either ordering under the limited resampling assumptions.

**Location-specific 1 s RMSE:** On I-80, GCV spline 0.38077 m vs PLS profile ML, zero mu, last3 0.44444 m. On US-101, GCV spline 0.31190 m vs corresponding PLS 0.57232 m. The pooled result is not driven by a reversal of the overall winner between the two sites, but trajectories within each site share recording environments.

## Important distinction: ML is available, but not jointly estimated

The library's criterion="mle" is **profile Gaussian marginal likelihood**, with lambda chosen over the same 15-point normalized smoothness grid as GCV; the observation noise variance is profiled out on the penalized spectral coordinates. The mean mu is **fixed at zero or plugged in from the training window**. Thus the current experiment **does not** jointly estimate (mu, lambda, sigma) by exact maximum likelihood, and its likelihood is not claimed to be mathematically identical to every approach in Guerrero's papers. See src/trendestimation/likelihood.py and selection_rows.csv.

## Exactly what the workflow created

Read the run-specific file_inventory.json for the authoritative file-by-file record. Standard complete run structure:

- data/raw/us-101/pageNNNN.csv and data/raw/i-80/pageNNNN.csv — downloaded CSV pages, untouched.
- data/download_manifest.json — URLs, page byte lengths and hashes; API pagination/selection status.
- data/episode_catalog.json and data/selected_positions.csv — selected episodes/positions.
- results/forecast_rows.csv — one method/episode/horizon row, **all 6,600**.
- results/selection_rows.csv — criterion, selected S and lambda, mu, **all 800**.
- results/summary.csv and results/paired_bootstrap.csv — pooled and per-site summaries and comparisons.
- results/RESULTS.md and results/run_manifest.json — readable findings, complete configuration, source/data hashes.
- build/ngsim.pdf, build/ngsim.log, build/build_manifest.json — successfully compiled existing paper (no injection of this new evidence).
- logs/download.log, logs/evaluate.log, logs/compile.log — VM execution records.
- metadata/requirements-resolved.txt, source_commit.txt, runner_name.txt, file_inventory.json — exact software/VM/file provenance.

## Recommended next manuscript action

**Do not blindly replace the five-track table with this result without revising the abstract, discussion, and limitations.** This is strong evidence that a *fair, tuned spline baseline matters* and that PLS cannot be advertised as generally best at trajectory position forecasting. The current study is still valuable as a transparent comparison of third-difference reference jerk, likelihood selection and continuation sensitivity; a publishable claim might focus on interpretable smoothness and divergence among forecasting rules, not universal optimality.

Before population-level inference, improve independence by including more **recording sessions or an additional road dataset**, and explicitly cluster at the recording session level. If limited to five session groups, report directional effects and uncertainty qualitatively. None of these recorded future positions supplies independently measured true physical jerk.
