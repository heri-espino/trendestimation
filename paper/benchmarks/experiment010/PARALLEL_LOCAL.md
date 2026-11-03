# Experiment010 — parallel local VM execution

## Why this exists

The uncapped sequential VM run on 2026-11-03 showed times including
139.45 s for naive inverse, 88.31 s for spectral SVD, 220.56 s
for banded Cholesky, 220.67 s for guarded Cholesky and 244.08 s for
banded LU in a single high-grid method-case. These were actual
user-observed subprocess durations, not proof of numerical correctness.
Sequentially launching the ten methods wastes available throughput
on a PC with 32 logical processors.

The user requested parallelization. This branch adds
run_parallel.py, a subprocess-based worker pool that can run
**independent method/case tasks simultaneously**, without removing
numerical validation or record preservation.

The result is *throughput parallelism*, not parallelization within one
PLS criterion evaluation. Each subprocess still uses one BLAS thread.
Elapsed method times under contention are not equivalent to isolated
serial method runtimes and should be compared as a separate experiment.

## Start safely, without interfering with a running sequential batch

If the earlier PowerShell command on shard 0 was started with
StartAttempt=10, MethodAttempts=10, **let that entire batch finish and
push its raw results** before switching. The sequential launcher prints
the next cursor in its batch_summary.json and commits results to a
unique results/experiment010-uncapped-* branch.

Create a new independent worktree from any trendestimation checkout
after fetching:

```powershell
git fetch origin
git worktree add --detach ..\trendestimation-parallel origin/research/experiment010-parallel-local
Set-Location ..\trendestimation-parallel
```

Then run eight workers, one BLAS thread each:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paper\benchmarks\experiment010\run_uncapped_local.ps1 -ShardIndex 0 -ShardCount 16 -StartAttempt 20 -MethodAttempts 10 -Workers 8
```

**StartAttempt=20 is ONLY correct if the previous
StartAttempt=10 / MethodAttempts=10 batch completed and its
next_attempt_offset is actually 20.** Otherwise read its ledger
and archive partial output before choosing a nonoverlapping cursor.
Do not start a new run on the same case IDs while the previous
batch is active; doing so distorts times and duplicates results.

For additional throughput after testing, increase Workers to 12 or 16
only when Task Manager confirms headroom. The default per-worker dense
budget is 2 GiB and the default *aggregate reservation* is 16 GiB:
Workers*MaxDenseBytes must not exceed TotalParallelDenseBytes.
These are conservative scheduling/accounting caps, NOT OS-enforced RSS
limits. Use -TotalParallelDenseBytes only after checking available RAM.
Going straight to 32 often hurts total throughput and can exhaust RAM,
despite there being 32 logical CPUs.

Example 12-worker **explicit aggregate reservation**:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paper\benchmarks\experiment010\run_uncapped_local.ps1 -ShardIndex 0 -ShardCount 16 -StartAttempt 20 -MethodAttempts 20 -Workers 12 -TotalParallelDenseBytes 25769803776
```

If your data are currently on a different shard or cursor, substitute
those numbers. This does not run any new GitHub Actions benchmark.

## Scientific and operational contract

- Exactly the same deterministic case_id, n,d,mu,criterion,
  amplitude, series seeds, S grid, exact S=1, and ten methods.
- Each worker calls the existing Experiment006 complete-criterion
  implementation with no artificial time limit and max-work=infinity.
- Each worker owns a unique slices/<case_id>/<method>/ directory and
  streams exceptions/stderr to <method>.log.
- Experiment006 writes its raw_times.csv atomically after each
  completed row. If a later task hangs or crashes, previous rows
  remain on disk.
- The main process alone writes method_attempts.csv atomically
  after each worker completes. Status is pending_or_running
  for not-yet-finished jobs (not numerical failure); only completed
  jobs are scientific benchmark observations.
- All status categories, missing optional dependencies and score
  parity checks are preserved. No invalid method is ranked as a
  valid timing observation.
- The launcher runs regression tests first, records source SHA,
  BLAS/OpenMP caps and environment, then commits and pushes each
  finished batch to its own results branch. The same result-branch
  name and output directory are never reused.
- Max-method-attempts counts tasks in a checkpoint batch; it is
  NOT a runtime cutoff.
- A 32-logical-processor machine does not imply a 32x speedup.
  The speedup of 8 workers must be measured on actual completion.
- When comparing *algorithm speed* rather than parallel throughput,
  retain isolated one-worker trials; multi-worker cold timings
  include CPU, cache and memory-bandwidth contention.
- Real VM reboot, Ctrl+C, OS memory limits, or power loss can still
  interrupt a batch. If interrupted, preserve files from runs/
  and examine unfinished ledger rows before running overlapping tasks.

## Source controls and scope

This work is staged on
research/experiment010-parallel-local, derived from independent
PR #103; both are draft and unmerged. Do not alter other agents' branches.
All older capped and uncapped measurements remain immutable on their
existing results branches.

The manuscript scope remains a numerical accuracy/error audit and
a small measured computing-time comparison. This change does NOT
introduce prediction models, regret/fallback studies or additional
unimplemented dual solvers.
