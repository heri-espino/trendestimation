# AGENTS.md — trendestimation research repository

Read README.md, this file, paper/benchmarks/README.md,
paper/benchmarks/experiment005/README.md, source modules, and tests
before editing. Existing numerical decisions and archived results are
authoritative. Preserve all experiment artifacts, metadata and manuscript
figures in Git; never invent or overwrite measured timings.

## Non-negotiable scientific contracts

- PLS objective: ||y-tau||^2 + lambda ||D_d tau - mu 1||^2.
- For fixed mu, A = I + lambda D_d.T D_d is SPD at finite lambda>=0.
- Guerrero's normalized smoothness coordinate depends only on n,d,lambda,
  not on y or fixed mu; preserve spectral S and inversion.
- The default fit-only method remains full SVD with shift-free reconstruction.
- New structured backends calculate trends only; selection and EDF remain
  spectral until separately validated equivalent criterion implementations exist.
- A fast incorrect, incomplete, or nonconverged result cannot win a timing
  comparison. Failed and optional-dependency cases must be retained.
- CHOLMOD/scikit-sparse is optional; SciPy SuperLU is not Cholesky.

## Concurrent agent workflow

Work on your own branch. Preserve other agents' branches, worktrees, PRs
and experiments. Name experiments sequentially as experiment001,
experiment002, etc. Include rationale, commands, seeds, actual outputs,
machine environment, findings and next steps. Never merge unrelated PRs.
Commit/push scripts, raw benchmark data, figures, numeric QA, and handoffs.
Use Git LFS or documented storage for oversized outputs and never commit secrets.

## Experiment005 handoff

See paper/benchmarks/experiment005/README.md for the new sparse,
banded-LU and PCG parity benchmark and run presets. Python tests:

    python -m pytest tests/test_experiment005_structured_solvers.py -q
    python paper/benchmarks/experiment005/run.py --preset smoke

Large timing presets are manual on a designated machine; CI does not
establish universal performance rankings. See AI_HANDOFF.md for status.


## Experiment006 repository-first rules

For any experiment006 work first inspect README.md, this AGENTS.md,
AI_HANDOFF.md, paper/benchmarks/experiment006/README.md, actual source,
tests and current draft PR #95. Preserve all previous experiments.
Keep source, numerical validation, full-factorial manifest and measured
results in Git. Use independent branches/worktrees for Windows runs.
The primary outcomes are computation time, memory, exactness and
failure status. No trend RMSE claims. The three implemented complete
criterion pipelines must not be conflated with Experiment005 fit-only
solvers; missing methods remain explicitly not implemented. High-order
nonzero-mu regimes and S=1 require independent numerical auditing.
Never merge without explicit user authorization.

## Experiment006 hybrid scientific contract (latest)

Six hybrid sparse/iterative plus banded selected-inverse diagnostic
pipelines have been added to the Experiment006 runner. Compare their
full measured cost including every factorization, not just their trend
fit time. Check tests/test_experiment006_hybrid_criteria.py before
interpreting speed rankings. No unrecorded timing or numerical results.
