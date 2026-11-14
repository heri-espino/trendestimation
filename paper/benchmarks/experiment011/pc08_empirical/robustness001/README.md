# Experiment011 post hoc robustness analysis (robustness001)

This is a **derived postprocessing analysis**, not a new experimental
campaign. It consumes the immutable, SHA-256-audited Experiment011 timing
tensor from GitHub Actions 42636962129 and never runs a solver, chooses a
new penalty parameter, changes a tolerance, or touches the original raw
Windows checkout. New manuscript section: paper/sections/experiment011_robustness.tex.

## Research questions

1. Exactly where did the banded Cholesky complete-criterion implementation
   report failures, and were they factorization errors, KKT rejections,
   smoothness-inversion errors or budget skips?
2. Can it complete a single candidate when the full grid fails? Does the
   spectral SVD implementation complete that same grid in the archived cases?
3. Where both methods validly complete the same search, what is the
   measured banded/SVD cold-time ratio for one candidate versus M=100?
4. What are the **code-defined** dense memory gates, rather than invented
   measured RAM usage?

## Reproduction

From a clean checkout of the manuscript PR branch, with the existing
Conda trendestimation environment, run:

    python paper/benchmarks/experiment011/pc08_empirical/robustness001/render.py

The frozen inputs (tracked repository files) are:

    paper/benchmarks/experiment011/pc08_empirical/derived/42636962129/timing_tensor.csv.gz
    paper/benchmarks/experiment011/pc08_empirical/derived/42636962129/paired_backend_seed_bootstrap.csv
    paper/benchmarks/experiment011/pc08_empirical/derived/42636962129/analysis_summary.json

The script asserts the campaign counts (2813 jobs, 92,679 long-form rows,
76,220 complete status-admissible), 9096 banded KKT-rejection timing
rows, 6336 logged smoothness-inversion rows and nine exactly matching
single-versus-grid reversal case families, with the original 97 seed
indices per case. It saves CSV tables, source-fingerprint metadata,
a claim ledger, and four new PDF/PNG figure pairs. The output is
deterministic except for floating-point rendering differences across
graphics versions. No new seed draws or bootstrap runs occur here:
the plotted paired 95% intervals were already computed using 700
independent seed-cluster bootstrap resamples by analysis run 42636962129.

The fourth-order failure-mode chart preserves explicit mapping
failures for **both** SVD and Cholesky, while Cholesky's specific
PLS-KKT check applies after a factor and solve. It is not a
head-to-head high-precision forward-error certificate, because the
SVD scorer does not run precisely the same banded KKT check.
The memory figure uses the versioned Experiment006 source
\`memory_budget_status\` policy: 40 n^2 bytes for the spectral
admission allowance, 56 n^2 for naive inverse, versus illustrative
16 n(d+1) bytes for two banded working arrays. These are
**model/policy formulae**, not peak RSS measurements. Experiment011
allowed 2 GiB dense workspaces. The 970 existing
\`budget_exceeded\` timing rows were CPU-work policy skips (776
naive inverse, 194 spectral), not demonstrated RAM exhaustion.

## Products

- fig05_complete_grid_failure.pdf/png: nine-case complete-grid
  failure matrix (97 seed clusters per case).
- fig06_fourth_order_failure_modes.pdf/png: fourth-order
  status breakdown (observed method-row denominator).
- fig07_single_vs_grid_speedups.pdf/png: matched CV/GCV
  one-candidate/grid ratios with already-verified seed CIs.
- fig08_memory_policy.pdf/png: transparent source policy
  memory scaling, explicitly not measured RSS.
- nine_failure_cases.csv, fourth_order_failure_mechanisms.csv,
  representative_paired_speedups.csv, memory_policy_model.csv,
  all_method_statuses.csv, summary.json, claim_to_data_ledger.json,
  figure_index.json.

## Interpretation and next step

The 9096 KKT rejections are timing/status rows with correlated
within-seed repeats, not 9096 independent numerical events.
Nine matched case families exhibit 100% banded single-candidate
success, 0% banded full-grid success and 100% SVD full-grid
completion in the tested configurations. At higher n and d, SVD
itself has shared inversion failures and can be resource-gated.
Future work could separately study the exact failing candidate
smoothness and independently certify solutions, but would require
a new explicitly authorized experiment. Do not quietly modify
the original numerical program or its tolerances.
