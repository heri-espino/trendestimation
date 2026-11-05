# Experiment011 Windows concurrent campaign audit

Run: PC08_concurrent24_20261105_010330
Results branch: results/experiment011-PC08_concurrent24_20261105_010330
Measured source: f58506a61cb1c5103237a5af2634dd6173ab8740

## Findings

All 83 configured case/block subprocesses returned zero, but this does not mean all numerical workloads succeeded. Auditing all 83 experiment011_qa.json files gives 2650 raw outcome rows: 2212 ok, 312 numerical_failed, 96 mapping_failed_ArithmeticError, 30 budget_exceeded. There are 29 float64-parity-classified case/blocks and 54 partial_success_with_skips_or_failures case/blocks. The QA issues arrays are empty even in partial cases; check classifications and status counts, not just issues or process return codes.

The outer launcher failed_jobs=0 counts process errors only. It is not a numerical-success count. Existing raw result statuses accurately preserve failures and must not be overwritten or ranked as complete-grid times.

Example: confirm_gcv_n4096_d4_m100/block000/measurements/raw_times.csv records a direct-S single-series grid stopping after 95 of 100 evaluations with a PLS KKT backward error approximately 1.31e-7. Its mapped-lambda grid fails S inversion at target 0.99, achieved 0.9899657186969449; it records zero scored evaluations. Multiple-series grids also fail. One-S workloads in that case succeed. These are reproducible recorded failure modes, not evidence of a fast complete search.

## Scope

This uploaded campaign contains 29 cases and 83 case/block jobs, not the historical full factorial. At audit, the GitHub matching-refs query for heads/results/experiment010-PC08 returned no branches; no uploaded PC08_fullgrid24 campaign could be verified. This does not establish whether an unpushed local run exists.

## Next work

Distinguish process completion, complete workload coverage, numerical validity and scientific pairing. The controller should prominently summarize non-ok statuses after each job; resource skips are distinct from numerical failures. Independently investigate high-order/high-S inversion and KKT failures without relaxing tolerances merely to obtain success. Preserve the current failures and original grids. Diagnose the full-grid command from its actual terminal output before changing workload scope again. Concurrent timings remain separate from isolated-latency evidence.
