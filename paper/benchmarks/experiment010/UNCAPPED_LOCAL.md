# Experiment010 — uncapped local Windows rerun (VM PowerShell)

## Decision

We intentionally removed **algorithm-level** per-method timeouts, the
whole-batch elapsed-time cap, and all predicted-work/n-only runtime
exclusions **only when** `--no-time-limit` is explicitly supplied.
This lets methods finish naturally and gives real wall-clock observations.
It does NOT remove RAM/physical feasibility checks, solver convergence
requirements, numerical validity standards, or normal process exceptions.

**GitHub Actions has its own job-duration ceiling.** Use Windows
PowerShell on university PCAG103A-08 instead. The PC must stay powered
on, and the logged-in session/process must stay alive. VM reboots,
process termination, power failures, Python crashes and out-of-memory
termination remain possible; no software can promise a truly infinite
run. A test that never converges may also run indefinitely; stop it
only with explicit reporting of the interruption.

The current paper scope remains **numerical accuracy/failures and real
complete-criterion computation times**, not calibrated cost predictors
or optimal fallbacks.

## Use an isolated checkout from any repository directory

Run Windows PowerShell from your existing trendestimation checkout:

```powershell
git fetch origin
git worktree add --detach ..\trendestimation-uncapped origin/research/experiment010-uncapped-checkpointed
Set-Location ..\trendestimation-uncapped
powershell -ExecutionPolicy Bypass -File .\paper\benchmarks\experiment010\run_uncapped_local.ps1 -ShardIndex 0 -ShardCount 16 -StartAttempt 0 -MethodAttempts 10
```

No installation, no environment creation, no GitHub Actions runner,
and no file edits to other agents' source branches.

The launcher verifies the existing Conda environment named exactly
`trendestimation`, runs the numerical regression tests, pins the
starting source SHA, sets numerical BLAS/OpenMP thread caps to 1,
and starts the comprehensive matrix using `--no-time-limit`.
It emits a unique timestamped output directory and at the end pushes
a **new immutable results branch** under
`results/experiment010-uncapped-<host>-<UTC timestamp>-shard...-offset...`.
It preserves raw CSVs, numerical failures, exception logs, source
and machine metadata and installed dependencies. Even a normally
reported Python failure will trigger the attempted Git archival of
partial records.

The batch size `-MethodAttempts 10` is **not a runtime cutoff**:
it limits the number of method-case pairs processed before a permanent
Git checkpoint. One method could legitimately occupy the VM for many
hours. Increasing the batch size increases the possible uncommitted
loss on abnormal interruption.

Use the printed `next_attempt_offset` (also inside the result branch's
`batch_summary.json`) for the next batch on **the same shard count**:

```powershell
powershell -ExecutionPolicy Bypass -File .\paper\benchmarks\experiment010\run_uncapped_local.ps1 -ShardIndex 0 -ShardCount 16 -StartAttempt 10 -MethodAttempts 10
```

The start offset of 10 is only an example: read the *actual* cursor
before launching the next batch. Do not skip or duplicate attempts
accidentally. After finishing one shard, choose any other shard
0 through 15 and start from offset 0. The full implementation covers
50,400 method-case attempts, so do not represent a partial block as a
complete grid. For a small first verification run, 10 methods correspond
to one complete case in deterministic shard order.

## Exact changed behavior

- Experiment010 `--no-time-limit` gives subprocess.run(timeout=None)
  and ignores whole-run elapsed seconds, while honoring
  `--max-method-attempts` as a **checkpoint-size** parameter.
- Experiment006 `--allow-unbounded-runtime` disables
  estimated-work limits and fixed-n runtime exclusions, but keeps
  the dense-memory budget. Experiment010 passes it automatically.
- Experiment006 writes `raw_times.csv` atomically after *each*
  completed status row; an interruption can leave partial evidence
  rather than losing all numerical outcomes.
- Method subprocess output and tracebacks are streamed to
  `<method>.log`, not accumulated indefinitely in RAM.
- Each method-case ledger records process return state and wall time.
  Status=ok, partial failures, undefined scores, setup exceptions,
  and missing optional CHOLMOD are not merged into fake successes.
- A zero elapsed time for resource exclusion is a *placeholder*;
  never a measured zero-second computation.
- No physical machine memory limit is bypassed; the default 2 GiB
  dense-memory cap can be adjusted explicitly using
  `-MaxDenseBytes` only after verifying free system memory.
- Running a million/100,000 candidate-point inversions can be
  extremely expensive even without an artificial cutoff.
  No speed or finishing-time guarantee is implied.

## Source and historical result separation

The original 25-second GitHub Windows runs and full factorial design
remain unchanged on archived result branches and PR #101. The
uncapped source lives on its *own* branch,
`research/experiment010-uncapped-checkpointed`, stacked on PR #101;
do not merge without user authorization. Compare timings across
source revisions and environments only with clearly documented
provenance. A full statistical criterion score agreement is not
an independent high-precision forward-error certification.

If PowerShell itself is terminated before the cleanup/archive stage,
files remain in the working directory under
`paper/benchmarks/experiment010/runs/`. Reopen the VM, inspect
`method_attempts.csv` and any partial `raw_times.csv`, then
manually commit and push those partial outputs to a new results branch
before resuming. Never overwrite that directory.


## Parallel version: begin here for the 32-logical-processor VM

[PARALLEL_LOCAL.md](PARALLEL_LOCAL.md) is the updated parallel
launcher protocol. Use an independent worktree on the
research/experiment010-parallel-local branch and
`run_uncapped_local.ps1 -Workers 8`. It starts eight separate
one-BLAS-thread Python subprocesses, retains the uncapped criteria,
all previous numerical/error logging, and result-branch archival.
The current shard0 offset10 serial batch must be completely
archived before attempting offset20. The exact cursor is determined
by its committed batch_summary.json, not by a guessed offset.
