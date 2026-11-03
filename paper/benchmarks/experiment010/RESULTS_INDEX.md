# Experiment010 — immutable measured-result index

Never merge a results branch into main merely to make it visible:
raw evidence is committed in unique immutable GitHub branches, with
this index linking to it. Read the exact source SHA in each run's
run_metadata.json. Planned factorial rows and numeric failures are NOT
measured times; only raw_times.csv rows with status=ok are such times.

## First actual university-Windows run: 41586066141

[GitHub Actions execution](https://github.com/heri-espino/trendestimation/actions/runs/41586066141)
on PCAG103A-08, Windows 11, pre-existing Conda environment
trendestimation. Benchmark source SHA
fc76c8c9d5366870e665b0897137da71e00f0dd7.

### Completed smoke (observed, not a theoretical prediction)

[Immutable results branch](https://github.com/heri-espino/trendestimation/tree/results/experiment010-41586066141-a1-smoke/paper/benchmarks/experiment010/runs/windows-41586066141-a1-smoke)

- GitHub Actions smoke job: **success**.
- 3 configurations: n=64, d=1, high data amplitude,
  criterion GCV; mu=0 versus mu="data" versus fixed mu=0.15.
- All ten existing benchmark method policies attempted for each
  configuration: 30 method–case subprocesses finished and archived
  complete CSVs, **420 raw status=ok timing records** (two paired
  seed-block repeats, four workloads and two coordinate policies,
  subject to resource/availability skips).
- 420 rows agree on selected criterion scores with the spectral
  reference under the scripted relative tolerance, but this is
  **not an independent high-precision forward-error certification**.
  30 additional rows have failed/partial status, mostly optional
  CHOLMOD unavailability and memory/work budget skips. Do not
  rank skipped or numerically unreliable candidates as winners.
- Full manifest has **403,200 planned policy/workload/coordinate
  rows**, and those are NOT empirical records.

Selected illustrative real *median total cold time* in milliseconds;
n=64, d=1, GCV, high amplitude, **mu=0**, mapped lambda coordinate,
two repetitions on PCAG103A-08:

| complete pipeline | one S, one series | 100 S, one series |
|---|---:|---:|
| naive explicit inverse | 0.991 | 13.276 |
| shift-free spectral SVD | 1.196 | 9.546 |
| banded Cholesky + selected inverse | 1.414 | 24.099 |
| general banded LU + exact diagnostics | 1.698 | 25.183 |
| sparse LU + exact banded diagnostics | 1.764 | 33.063 |
| FFT-PCG + exact banded diagnostics | 1.739 | 36.331 |
| DST-PCG + exact banded diagnostics | 1.744 | 37.101 |
| Jacobi-PCG + exact banded diagnostics | 2.041 | 80.220 |
| optional sparse Cholesky / CHOLMOD | unavailable | unavailable |

The guarded composite uses banded Cholesky for d=1 and is
reported as a policy, not an independent numerical primitive;
its measured medians were 1.367 ms (one S) and 22.811 ms (100 S).
These figures show a *possible* finite-workload reversal between
a single evaluation and a 100-point grid. They do not establish
a universal frontier or its crossover location. The differences
between mu=0, mu="data" and mu=0.15 in the tiny smoke are small
relative to broader missing variation; no equivalence or universal
winner is inferred. Two repeats cannot robustly estimate timing
uncertainty. Moreover, the current Experiment006 implementation
charges separately instantiated S-grid mapper setup per method.

### Pilot

Pilot is the second job of the same workflow run, with up to 60
bounded method-case attempts, chosen to cover difference orders
1..6, all three mean policies and all five criteria early in its
case schedule. Inspect the **live Actions run** and its resulting
immutable results branch
'results/experiment010-41586066141-a1-pilot' before making any
completion/accuracy statement. This index does not fabricate pilot
results while the job is running.

## Completion contract for future agents

1. Preserve every measured run with source SHA, actual timings,
   numerical statuses, mean policies, candidate grids, machine
   description, installed optional dependencies, caching and seeds.
2. Resume the rest of the pilot and every feasible comprehensive
   shard by reading each prior batch_summary.json next_attempt_offset,
   reusing shard index/count with the next start-attempt and writing
   a *new* immutable output.
3. Perform an independent high-precision numerical certificate,
   especially for d>=5 and large S, before ranking method winners.
4. Derive and calibrate the per-method complete cost components;
   validate crossovers on genuinely class-balanced held-out
   n,d,M,R,criterion,mu cases. Record empirical oracle regret and
   second-choice fallback failures; do not select from Big-O alone.
5. Update the paper only once model comparisons and held-out
   uncertainty are supported by archived source-derived evidence.
