# Experiment005 agent handoff

## Purpose
Earlier Experiment004 high-precision results and Windows computational
timings came from different runs. Experiment005 joins these measurements
on the same generated data, same lambda, one host and one environment.
It does not claim that numerical-error RMSE is forecasting RMSE.

## Read-first order
1. Root README.md, and the experiment005 README.
2. paper/benchmarks/experiment004/run_pilot.py.
3. paper/benchmarks/experiment004/verify_stable_solvers.py.
4. paper/benchmarks/experiment004/verify_bic_precision.py.
5. paper/benchmarks/full_s_backend_criteria.py and full_s_search_modes.py.
6. The two paper/csda-* manuscripts and original benchmark sources.
7. tests/test_experiment005_paired.py.

## Decisions and status
- Branch: experiment005/paired-accuracy-runtime, not main.
- Original nine fit methods, three complete-criterion backends.
- Normalized S is PRIMARY; no independently spaced log-lambda grid.
- Orders 1..6, two mu policies, iid and AR(1), smooth and kink trend shapes.
- MP dual reference uses 85 decimal digits by default and is excluded
  from timed methods; reference KKT is separately recorded.
- Reuses the same finite penalty for every solver within a pair.
- Validity checks the COMPLETE grid, not merely the selected point.
- The current criterion QA is relative to double-SVD scores, NOT
  high-precision score truth.
- Exact endpoint trends have no independently certified MP accuracy;
  mark them unverified in the joint frontier.
- BIC S>=0.10 is a documented boundary sensitivity restriction.
- No code in the public trendestimation library is altered.

## Reproduce
Run the smoke preset on GitHub-hosted CI first; use the workstation or
PCAG103A-08 self-hosted runner for larger paired timings if online.
Record per-run CSVs, checksums, environment and input commit, and push.
Never overwrite results or silently drop failed cases.

## Next research actions
Inspect smoke output, quantify numerical-failure rates, check whether
ML selects S=1, then run quick with independent seeds. Develop the
eligible-only Pareto analysis with paired bootstrap CIs and plots using
AwesomeFigures, recording every source CSV and generated figure. If
necessary refine code before the large full preset. Do not merge without
explicit authorization from the user or coordinator.
