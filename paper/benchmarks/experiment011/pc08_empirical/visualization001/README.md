# Scientific figure and table redesign: visualization001

This is a **visualization-only postprocessing step**, not a numerical
experiment. The paper's eight figures and three tables are regenerated from
the immutable, source-hashed Experiment011 outcome records without changing
the estimators, numerical acceptance thresholds, seeds, grid configuration,
or physical raw/backup files.

## Input and execution
Run from the repository root:

    python paper/benchmarks/experiment011/pc08_empirical/visualization001/render.py

Inputs in the immutable derived analysis folder include:
- timing_tensor.csv.gz (all 92,679 outcome and masked rows);
- paired_backend_rows.csv.gz (valid matching of end-to-end cold times);
- paired_backend_seed_bootstrap.csv (previously calculated 700-resample
  independent seed-cluster percentile uncertainty);
- paired_coordinate_rows.csv.gz;
- timing_cell_summary.csv.

The output evidence.json stores input SHA-256 digests and checks 76,220
complete records, 9096 banded-KKT rejection rows, 6336 S-inversion failure
rows (including spectral statuses where the same exception was reported as
a numerical failure), 970 work-budget exclusions, and 57 unavailable
case-seed jobs. Incomplete searches never enter the measured timing-ratio
distributions. There is no new parameter fitting or experiment run.

## Figures used in the Springer manuscript
1. fig01_reliability_stacked: 100% horizontal stacked acceptance and
   exclusion fractions, faceted by criterion. The accepted part is colored
   by numerical implementation; patterned segments distinguish failure
   mechanisms.
2. fig02_runtime_distributions: kernel-density violins, interquartile
   boxplots and individual seed-level paired ratios for representative
   valid full grids; original geometric means and bootstrap intervals
   remain in Table 1.
3. fig03_mapping_distributions: mapped-penalty/direct-smoothness cold-time
   distributions, grouped by criterion, grid size and method. Exploratory
   pooling across heterogeneous cases is disclosed.
4. fig04_workload_stacked: method-colored, component-wise median
   initialization, S-to-lambda mapping and criterion-evaluation time
   stacks for a representative first-order GCV design. The sum of
   component medians is not claimed to equal median total time.
5. fig05_grid_completion: grid-admissibility failure contrast with
   method-specific stacked and patterned completion bars for nine
   identified configurations. The isolated-candidate tasks completed
   for both methods.
6. fig06_order4_failures: status decomposition for fourth-order cases,
   preserving shared smoothness inversion failures.
7. fig07_crossover_distributions: seed-wise complete-cold-time
   distribution shifts when increasing from one to 100 candidates.
8. fig08_memory_scaling: fixed source-policy dense workspace allowance
   compared with two banded working arrays. Not peak-memory measurements.

## Tables
- table01_runtime: valid paired 100-candidate grid results, per-seed
  median and interquartile range, geometric mean and its original
  seed-cluster 95% bootstrap interval.
- table02_reliability: scientifically classified complete/failed
  method-level records with **comment-based** inversion counts. A
  spectral inversion error is not mislabeled a Cholesky/KKT failure.
- table03_grid_failures: nine exact full-grid reversal configurations
  and per-method completion counts.

All figure files are in PDF (vector typography) and PNG (preview).
All tables use valid doubled LaTeX row terminators. No repo development
nomenclature appears in figure titles/captions in the manuscript.

## Interpretation and review
Distributions are descriptive kernel-density estimates; individual points
are correlated within seeds in the raw data, so distributions first
average log timing ratios within an independent seed. Bootstrap confidence
intervals remain those originally computed from the frozen experiment.
Some pooled coordinate distributions combine heterogeneous cases and are
not universal scaling laws.

The measured advantage supports spectral SVD as the conditional preferred
backend for repeated complete-criterion search at memory-feasible sizes.
It does not establish a universal solver ranking, identical per-method
KKT checks, or observed physical RAM exhaustion.

Run the source-only analysis tests and compile with the existing official
Springer sn-jnl workflow on the scoped self-hosted PCAG103A-08
Windows runner; verify a *new* manuscript PDF by its Actions run SHA and
render all pages before advertising it as final. Do not merge or submit
the draft manuscript without the author's separate permission.
