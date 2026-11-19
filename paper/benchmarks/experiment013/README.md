# Experiment013 — homogeneous complete-criterion timing grid

## Scientific purpose

This is a NEW, sequentially numbered benchmark following Experiments011–012.
It makes all seven requested sample sizes and **all three difference orders,
including d=2**, explicit. It records all three complete-criterion backends
(naive dense inverse, exact selected-inverse banded Cholesky and spectral SVD)
and all five selection criteria: CV, GCV, MLE, AICc, BIC.

**Implementation stage, not a set of measured results.** The archived
97-seed Experiment011 evidence is immutable. Do not edit its historical
confidence intervals or present this experiment as a source-matched
extension of the 2011 protocol.

## Complete fixed-primary design

- n = 32, 64, 128, 256, 512, 1024, 2048
- d = 1, **2**, 3
- backend = `naive_inverse`, `banded_cholesky`, `spectral_svd`
- criterion = `cv`, `gcv`, `mle`, `aicc`, `bic`
- M = 10, 100, 1000, 10000 distinct penalty candidates
- independent realizations = **100** per (n,d,criterion), using the same
  random series across all three methods and all five criteria

There are 7 × 3 × 3 × 5 × 4 = **1260** requested method-level
configurations (126,000 planned method/seed cells), plus an
**M=1 checkpoint** for first-use cost: 1575 method/configuration/checkpoint
records and 157,500 scheduled method/seed/checkpoint status cells.
Statuses are `ok`, a numerical failure or an explicit resource
ineligibility; none are silently dropped. The actual number of completed
timings will be smaller than this manifest if the resource gates or
numerical checks reject some cells.

**Controlled/held fixed:** reference mean mu=0, low-amplitude simulated
series from the existing Experiment006 sampler, R=1 independent series
per seed, a single worker, one BLAS thread, no cross-method setup sharing
and no across-penalty factor caching for Cholesky or naive inversion.
Method order rotates by seed and case. The source experiment's exact
`Evaluator` implementation is reused unchanged. The five criterion
names match the repository's existing definitions and conventions.

**Candidate coordinate:** `direct_lambda` with a nested log-uniform
van-der-Corput sequence inside lambda in (1e-3, 1e3), as in
Experiment012. Every backend receives the *identical* candidate
values and every prefix is a subset of a longer prefix. Hence the
10th, 100th, etc. checkpoints are genuinely cumulative without
repeatedly executing the first ten candidate evaluations. This
is intentionally **different** from Experiment011's uniform normalized
smoothness `S_j=j/M` grid and excludes S-to-lambda inversion;
do not combine the two studies into a single numerically matched
timing sample. This experiment isolates method-level amortization
under a complete criterion; a separate S-mapping robustness layer
is appropriate after the homogeneous primary evidence is collected.

**Timing definitions:** for k candidates,

    total_cold(k) = one_time_setup + sum_{j=1}^k complete_criterion_evaluation_j

Record the first evaluation, the one-time setup and cumulative
criterion costs separately. SVD pays for difference-matrix basis
construction and series projection once per realization; banded
Cholesky and the naive inverse pay for each distinct matrix in
the grid. This compares *complete CV/GCV/ML/AICc/BIC scores*,
not merely fitted trends. SVD may be slower on k=1 and overtake
structured methods after repeated evaluations.

## Compute feasibility and the nonrectangular measured subset

The manifest covers **every requested cell**, but the runner
does not attempt infeasible dense inversions or unbounded repeated
spectral setups. Its default *predeclared* work policy is

    W_naive = n^3 M
    W_banded = n (d+1)^2 M
    W_spectral_CV = n^2 M
    W_spectral_other = n M

with a 50,000,000-unit cap, dense workspace limits of
56n^2 bytes (naive) / 40n^2 bytes (SVD) and 2 GiB total dense
allocation allowance. The default SVD setup gate is n<=512;
naive dense inversion is also excluded at n>256.
These work-unit formulas are *policy approximations*, not
observed wall-clock seconds or exact algorithmic FLOP counts.
The banded expression is optimistic regarding costly diagnostics
and the spectral expressions exclude O(n^3) setup, which has
its own explicit size gate. Code treats these limits as
**resource skips, not timing measurements**.

The user may explicitly select a larger `-DenseLimitN` or
`-MaxWork`, but such cases should first be tested as a
small pilot, with memory/thermal behavior monitored. Neither
a naive n2048/M10000 run nor a full 100-seed dense SVD n2048
campaign is a sensible default on an interactive machine.
No numerical zeros, synthetic elapsed times, fabricated
speedups or unmeasured grid completions are allowed.

## Copy/paste Windows 11 PowerShell commands

From the current repository root, in a *clean* checkout of `main`:

```powershell
git switch main
git pull --ff-only origin main
.\paper\benchmarks\experiment013\Run-Grid.ps1 -Phase small
```

This first call is **plan-only**, with no expensive computation.
For genuine measurements, run sequentially; each invocation
generates a unique run folder, a source-commit manifest, full
status and timing CSV, paired analysis and a separate pushed
`results/experiment013-*` Git branch:

```powershell
.\paper\benchmarks\experiment013\Run-Grid.ps1 -Phase small  -Seeds 100 -Execute -Archive
.\paper\benchmarks\experiment013\Run-Grid.ps1 -Phase medium -Seeds 100 -Execute -Archive
.\paper\benchmarks\experiment013\Run-Grid.ps1 -Phase large  -Seeds 100 -Execute -Archive
```

For a tiny end-to-end *pilot* before running 100 seeds:

```powershell
.\paper\benchmarks\experiment013\Run-Grid.ps1 -Phase small -Seeds 2 -MaxCandidates 10 -Execute -Archive
```

Each run retains its own `metadata.json`, `coverage_plan.csv`,
`timings.csv`, `completion.json`, `status_counts.csv`,
`numerical_disagreements.csv`, `paired_speedups.csv`,
`analysis_summary.json` and `file_inventory.csv`.
`Run-Grid.ps1` uses a separate Git worktree so results are
archived without committing files onto `main` or erasing another
agent's branch. The original output directory is also kept.
Do not run parallel experiments on the same host during
latency measurement.

To resume a run interrupted before it was archived, use the
original **tag printed in the output folder name** and original
phase/seed/work settings:

```powershell
.\paper\benchmarks\experiment013\Run-Grid.ps1 -Phase small -Seeds 100 -ResumeTag experiment013_small_YYYYMMDD_HHMMSS_PID -Execute -Archive
```

Resuming requires the **identical source revision and environment**
and refuses duplicate/partial method groups. If `main` has changed,
retain the old source in a separate checkout/worktree instead of
silently mixing new code with old timings. Do not use this to
retime a previously completed and archived run.

## Interpretation and extensions

`analyze.py` checks complete candidate coverage, source hashes,
timing arithmetic and matched selected-penalty parity; it computes
paired geometric method speedups and seed bootstrap intervals.
For MLE a candidate-independent score offset can occur, so
selected lambda is required to match but score equality is not
used as a universal ML validity test. Invalid pairs are
listed rather than counted as fast winners.

Additional factors **not varied** in the primary design:
mu=0 vs nonzero fixed mu vs plug-in mu=data; low/high scale;
normalized smoothness S versus lambda; R=1 vs R>1;
direct vs once-mapped candidate coordinates; fit-only vs
complete criterion; repeat/order blocks, concurrency and
hardware/BLAS, numerical tolerance and failure policy.
These belong in a separate prespecified robustness design
rather than multiplying every primary cell by 3×2×2×... .

No new Springer figures/PDF are claimed until actual 100-seed
Windows runs have been archived, audited and independently
checked. Journal submission requires separate author approval.
