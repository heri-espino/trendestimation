# Experiment010 — focused three-method large experiment

## Decision and scientific scope

On 2026-11-03 the user asked to restrict the **large** factorial
experiment to exactly:

1. `naive_inverse` — explicit dense matrix inverse baseline.
2. `spectral_svd` — shift-free full singular-value decomposition.
3. `sparse_cholesky_banded_trace` — optional CHOLMOD sparse-Cholesky
   trend solver combined with exact banded criterion diagnostics.

The original ten pipeline implementations, 403,200-cell planning design,
raw experiments, and previous results branches remain intact. This is a
focused, opt-in Experiment010 campaign, **not** a new experiment number.

The paper remains about independently checked numerical accuracy,
completeness/failure statuses, and genuine end-to-end criterion timings,
not predicted cost models or fallback regret.

## What actually happened in the first uncapped parallel run

Actual permanent raw data:
[results/experiment010-uncapped-PCAG103A-08-20261103T165925192Z-shard0-offset20](https://github.com/heri-espino/trendestimation/tree/results/experiment010-uncapped-PCAG103A-08-20261103T165925192Z-shard0-offset20).

- Host: PCAG103A-08, Windows 11, Conda Python 3.11.17.
- Source: `bf4195c12e3c4b07e039df85971b303ab1d83d37`.
- One `n=64,d=1` configuration, `mu=data` (observed-difference
  mean), high data amplitude, BIC, `M=100000`.
- Eight concurrent Python subprocess workers, one BLAS thread each.
- No per-method/whole-run artificial timeouts; source work limits
  disabled; dense RAM preflight retained.
- Ten method-case subprocesses finished and archived.
- Total batch wall time 1109.3040 s (18.4884 min).
- 144 valid numerical timing rows, all with selected-score parity
  against SVD at recorded tolerance; **not** independent 85-digit
  forward-error certification.
- Eight failed-or-partial comparison rows all come from
  `sparse_cholesky_banded_trace`: the actual raw status is
  `setup_failed_ImportError`, indicating unavailable optional
  `sksparse.cholmod` on this Windows environment.
  Its approximately 0.82-second process time is **NOT a successful
  sparse-Cholesky algorithm time**.
- The `method_attempts.csv` says `completed_with_csv` for
  sparse Cholesky because a CSV of failures was successfully written;
  the method had **zero** `status=ok` observations.
- Parallel subprocess wall-clock durations (s): naive 171.75,
  spectral SVD 111.85, banded Cholesky 268.56, guarded 271.95,
  banded LU 291.15, sparse LU 388.36, PCG FFT 421.46,
  PCG DST 437.83, PCG Jacobi 997.23.
  These are completion durations across all workload variants,
  including concurrent CPU-resource contention.
- For the `grid_one_series, mapped_lambda` workload with 100000
  candidate smoothness values, median **criterion** cold time
  was 10.2265 s for SVD and 15.1669 s for naive inversion.
  This one result alone cannot establish general algorithm rankings.

## Important limitation of the chosen three

**Sparse Cholesky is currently unavailable**: the Windows Conda
environment lacks a working optional `sksparse.cholmod`
installation. The focused runner records this as
`dependency_unavailable` once per selected case *without*
repeatedly launching identical setup failures. It does not
automatically install anything or silently substitute SuperLU.

Further, dense naive inversion and dense SVD are legitimately
infeasible at the largest `n` values under the default 2 GiB
dense-memory guard. Therefore the selected three do NOT yield
three comparable real outcomes at large `n`. They remain
precisely the three requested named methods, with all impossible
or missing-dependency outcomes recorded explicitly.

If a three-way **working** comparison is required before CHOLMOD
is available, the empirically operational alternative is
`banded_cholesky`, not `sparse_cholesky_banded_trace`; however,
the code does NOT make that substitution without user approval.

## Safe local PowerShell commands

First fetch the latest source. **Do not modify the old
trendestimation-parallel worktree with uncommitted outputs.**
From a clean existing repository checkout:

```powershell
git fetch origin
git worktree add --detach ..\trendestimation-focused origin/research/experiment010-focused-three
Set-Location ..\trendestimation-focused
```

The standalone launcher defaults to exactly the three requested
pipelines. Use eight workers (subject to RAM availability).
The first 30 full-design positions of shard 0 have already
been archived, so the next nonoverlapping offset is 30:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paper\benchmarks\experiment010\run_uncapped_local.ps1 -ShardIndex 0 -ShardCount 16 -StartAttempt 30 -MethodAttempts 40 -Workers 8
```

**Cursor semantics are unchanged:** each source case occupies
ten original full-design method positions. A 40-slot batch
therefore represents four full parameter cases, with
12 selected method-case records and 28 records marked
`method_not_selected`. When CHOLMOD is absent, eight
naive/SVD subprocesses are launched; four sparse-Cholesky
cases receive `dependency_unavailable`, and no other
algorithms execute.

The summary distinguishes `selected_method_cases`,
`actual_attempted` (real worker launches),
`not_selected_by_design`, and `dependency_unavailable`.
`next_attempt_offset` counts *all original method slots*
to prevent overlap with the past ten-method runs. Use the
new actual cursor from the committed `batch_summary.json`
when continuing (not an assumed start offset).

You can opt back into the full ten-method set with
`-Methods all`, or supply a comma-separated list
using `-Methods "naive_inverse,spectral_svd,banded_cholesky"`.
The latter is a different scientific comparison and
must be explicitly reported as such.

### Preserve all evidence

All completed or failed batch source files, output CSVs,
method errors, environment metadata, numerical checks and
timing results are committed and pushed into a unique
`results/experiment010-uncapped-*` branch by the PowerShell
launcher. The Windows locked-ledger retry/recovery fix
remains active. Never classify unavailable methods or
the seven excluded pipelines as "numerically failed".
No new computations have run solely by committing this
focused experimental source branch.

## Next scientific checks

The new focused results need independent high-precision
trend/criterion validation before reporting numerical
superiority, especially for `d=5,6` and `S\to1`.
Compare only fully valid workloads with identical
`n,d,mu,criterion,M,R` and numerical tolerances.
Parallel wall times reflect resource contention,
not isolated one-worker solver latencies.
