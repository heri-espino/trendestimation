**LATEST Springer empirical robustness/PDF certification (2026-11-09; supersedes older 11-page PDF records below):** In draft [PR #126](https://github.com/heri-espino/trendestimation/pull/126), the canonical Springer \`paper/main.tex\` now contains the explicitly requested Cholesky KKT/grid reliability, matched single-vs-grid speedups and memory-policy discussion, illustrated by four additional vector figures (Figs. 5–8). The frozen Experiment011 source shows 9096 banded post-solve KKT rejection rows; nine 97-seed families succeeded for single-candidate both methods and on full grid for SVD, but banded full grid failed; 6336 inversion-error rows involve both methods. All counts are correlated timing/status rows, not independent failure events or high-precision certificates. The source-code 2 GiB cap with 40n² SVD allowance versus 16n(d+1) for two band buffers is explicitly *not observed RAM*. Figures/CSV/JSON generator and outputs are archived on [results/experiment011-robustness001-pc08-42642807292](https://github.com/heri-espino/trendestimation/tree/results/experiment011-robustness001-pc08-42642807292), with successful [PC08 run 42642807292](https://github.com/heri-espino/trendestimation/actions/runs/42642807292). The **NEW 15-page compiled PDF** is on [artifacts/springer-empirical-pc08-42643291205](https://github.com/heri-espino/trendestimation/tree/artifacts/springer-empirical-pc08-42643291205), [successful PC08 build 42643291205](https://github.com/heri-espino/trendestimation/actions/runs/42643291205), SHA-256 aad05992ae19f4d5db9c7c2ec1e1a4fcc67bb086c3465a645b472b70a4a859a8, 529793 bytes. Seven tests passed, final TeX pass was free of undefined references/citations and overfull boxes, and all 15 pages and new figures were downloaded/rendered/visually reviewed. Read [robustness001/RESULTS.md](paper/benchmarks/experiment011/pc08_empirical/robustness001/RESULTS.md) and [robustness001/FINAL_VERIFICATION.md](paper/benchmarks/experiment011/pc08_empirical/robustness001/FINAL_VERIFICATION.md). Raw files untouched; no new campaign, merge, journal submission or author-approval claim.

**Open draft manuscript PR #126 (do not merge):** https://github.com/heri-espino/trendestimation/pull/126 . It is stacked on the still-open PR #124 handoff branch; retarget after integration/review, do not merge or submit without approval. The newly built PDF source revision and verified artifact remain unchanged by these documentation-only updates.

# Experiment011 Springer empirical analysis handoff

Updated 9 November 2026. Read this alongside root and paper AGENTS.md, the
Experiment011 completion handoff, SPRINGER_ANALYSIS_AGENT_PROMPT.md, and
paper/SPRINGER_READINESS.md before changing results. This folder owns only the
empirical complete-criterion timing analysis. The original completed numerical
experiment, CSDA numerical/complexity manuscripts, NGSIM application and
historical SNCS paper must not be changed here.

## Canonical inputs

Original, immutable read-only Windows checkout:
    C:\Users\175199\trendestimation-PC08_add97svd_20261105_025108

Original cumulative report, relative to the checkout:
    paper\benchmarks\experiment011\campaigns\PC08_resume12_20261108_200034\report.json

Read-only author-verified same-disk backup:
    C:\Users\175199\experiment011-backups\experiment011_20261109_072910742

Final report SHA-256:
    c5d4898c83c731ada23a10957f80adc43616200206dc76573f365d38ba37f723

The complete six-stage source chain appended 2272, 11, 55, 0, 0 and 475
authoritative case-seed records respectively. Reconstruct each accepted run
folder from the report stage that first appended the record. Never use
recursive folder scanning to count interrupted attempts as independent trials.

The 29-case/97-seed campaign has 2813 distinct recorded jobs and 57 nonzero
process exits. Preflight run:
https://github.com/heri-espino/trendestimation/actions/runs/42633415411

The corrected complete analysis is:
https://github.com/heri-espino/trendestimation/actions/runs/42636962129

Its 21-file Actions artifact was recovered without any numerical rerun:
https://github.com/heri-espino/trendestimation/actions/runs/42637443986

Permanent repaired evidence branch:
https://github.com/heri-espino/trendestimation/tree/results/experiment011-springer-derived-42636962129

The first analysis snapshot 42634293076 is preserved as history but its
Figure 2 is INVALID: a string/int M-filtering mismatch caused an empty plot.
Use repaired snapshot 42636962129 and no older Figure 2.

## Derived evidence

Folder:
    paper/benchmarks/experiment011/pc08_empirical/derived/42636962129/

Main files:
- analysis_summary.json and accepted_file_manifest.csv: exact run-chain provenance.
- timing_tensor.csv.gz: sparse long-form measured and explicitly masked cells.
- timing_cell_summary.csv: setup, mapping, scoring, cold/warm totals by phase.
- paired_backend_rows.csv.gz and paired_coordinate_rows.csv.gz: matched observations.
- paired_backend_seed_bootstrap.csv and paired_coordinate_seed_bootstrap.csv: per-seed
  cluster geometric ratios and 700-resample 95 percent percentile intervals.
- criterion_backend_reliability.csv: denominators and invalid-reason counts.
- integrity_issues.json: missing original/backup file paths.
- claim_to_data_ledger.json: source mapping for every manuscript claim.
- empirical_results.tex: generated selected-case table.
- figures/fig01_reliability, fig02_paired_cv_gcv, fig03_mapping_cost,
  fig04_workloads, each with vector PDF and raster PNG preview.
- figure_index.json: source and captions.

There are 92,679 recorded-or-masked rows, 76,220 complete status-admissible
rows and 16,459 excluded rows: 11,208 numerical-failure rows, 4224 mapping
errors, 970 budget exclusions, 57 failed jobs with missing files (60 missing
individual files). Scheduling completion is not numerical certification.
High-difference-order grids can fail despite valid isolated evaluations.
Method speedups retain only complete searches with matching selected-S and
double-precision selected-score parity. This is not an independent
high-precision forward-error certificate. Do not pool the 24-, 1-, and
12-worker phases into one purported isolated-latency benchmark.

## Reproduce on PC08 (read-only, not a benchmark rerun)

From a separate source checkout using the existing trendestimation Conda env:

    python -m unittest discover -s paper/benchmarks/experiment011/pc08_empirical -p test_*.py -v

    python paper/benchmarks/experiment011/pc08_empirical/preflight.py --root ORIGINAL --backup BACKUP --output preflight_verification001.json

    python paper/benchmarks/experiment011/pc08_empirical/analyze_campaign.py --original ORIGINAL --backup BACKUP --out NEW_UNCREATED_OUTPUT_DIR

The analyzer refuses to overwrite an existing derived directory. No command
above invokes the original numerical benchmark, changes solver tolerances, or
modifies the raw experiment checkout/backup. One BLAS thread per job was used
for the original campaign, but this analysis stage is a postprocessing job.

Build the canonical Springer manuscript only after all figure and TeX files
exist in a source checkout:

    python scripts/build_papers_pc08.py --paper springer --output-dir paper/builds/pc08/new_build001 --require-runner

Check the source SHA-256, freshly generated PDF digest, TeX logs, bibliography,
pages and figure layout. The workflow in
.github/workflows/springer-empirical-pc08.yml archives a new PDF on a
scoped artifacts branch, in addition to its Actions artifact.

## Constraints and next steps

Paper boundaries: numerical high-precision and theoretical operation counts
belong to CSDA companions; the vehicle jerk/forecast application belongs
to NGSIM. Preserve the source code, tests, prior snapshots, derived tables,
figures, checksums and manuscript outputs. Never merge the manuscript PR,
release raw results, assert coauthor disclosures or submit to Springer without
explicit authorization. Before editing the generator or rerendering,
inspect its actual selected-case filters and verify the associated
case-level parity and missingness counts.

## Current build request

The canonical paper and workflow refer only to corrected analysis snapshot 42636962129. Compile from this source revision using PCAG103A-08; inspect the final LaTeX pass and fresh PDF, preserving build logs and page proofs in a new immutable artifacts branch.
