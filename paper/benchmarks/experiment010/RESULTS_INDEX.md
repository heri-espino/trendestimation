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

### Completed pilot — IMPORTANT numerical / scoring caveat

[Immutable pilot results](https://github.com/heri-espino/trendestimation/tree/results/experiment010-41586066141-a1-pilot/paper/benchmarks/experiment010/runs/windows-41586066141-a1-pilot)

- GitHub Actions pilot job: **success**.
- **60** method-case attempts finished and were archived;
  **720 raw status=ok timing records**.
- The 60 attempts cover six n=64 cases, one for each
  d=1,...,6, distributed over all three mean policies and
  five criteria. No n=128 case was attempted yet.
- The 900 score-audit rows include **616 pass**, **104 score
  disagreements**, **180 failed/partial**; passing score
  parity is NOT a high-precision numerical certificate.
- Of the 104 disagreements, **100** involve d=5 and
  mu="data" with the MLE criterion, and **4** involve
  d=6, mu=0.15 and ordinary CV (naive inverse).
- The d=5 MLE scores revealed an **inconsistent additive
  normalization** in the original banded/hybrid/naive
  benchmark scores relative to spectral MLE and the
  exact S=1 limit. That was corrected on PR #100,
  preserving the original results unchanged. See
  [the mathematical audit](../../../notes/experiment010_mle_normalization_audit.md).
  The first pilot's cross-method absolute MLE scores are
  **not eligible for an empirical solver ranking**.
  High-order numerical error may remain after correction.
- Pilot continuation cursor is **next_attempt_offset=60**
  of 1800 planned pilot method-case attempts. Subsequent
  invocations must use a new output path and source SHA.

The initial pilot can be used as historical evidence of the
bug and its measured runtimes, but not as a corrected MLE
comparison. A NEW source-version run and independent
numerical validation are required.

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


## Corrected MLE normalization rerun — completed #41587467639

[GitHub Actions run](https://github.com/heri-espino/trendestimation/actions/runs/41587467639)
on the SAME university Windows VM and Conda environment; run source SHA
532f0aab8abe3af8a4b47acce9a72e08c7895ea7 (the post-normalization
code). BOTH smoke and pilot jobs completed successfully and their
numerical prerequisite tests passed.

- [Corrected smoke raw data](https://github.com/heri-espino/trendestimation/tree/results/experiment010-41587467639-a1-smoke/paper/benchmarks/experiment010/runs/windows-41587467639-a1-smoke):
  30 complete method-case CSVs, 420 status=ok timing records,
  420 score-parity-only passes, 30 failed/partial.
- [Corrected pilot raw data](https://github.com/heri-espino/trendestimation/tree/results/experiment010-41587467639-a1-pilot/paper/benchmarks/experiment010/runs/windows-41587467639-a1-pilot):
  60 complete method-case CSVs, 720 status=ok timings,
  **704 score-parity-only passes, 16 disagreements, 180 failed/partial**.
- Compared with the pre-correction pilot (616 parity, 104 disagreements),
  correction changes 88 rows from disagreement to score-parity pass.
  This is not additional independent data: the same deterministic
  seed blocks and workload design are used under different source SHAs.
- The 16 remaining score disagreements are ALL from the naive
  dense inverse: 12 for n64,d5,mu=data,MLE, and 4 for
  n64,d6,mu=0.15,CV. High-order forward numerical accuracy
  remains a mandatory separate independent gate; do not declare
  a ten-method numerical winner yet.
- These two run IDs MUST NOT have their MLE scores directly pooled:
  first is mathematically inconsistently normalized, second is corrected.
  Both complete raw timing archives are preserved.

**Pilot extension started:** [GitHub Actions #41587723422](https://github.com/heri-espino/trendestimation/actions/runs/41587723422)
has four bounded nonoverlapping continuation blocks starting at offsets
60, 120, 180, 240, each covering 60 additional method-case attempts
against the same corrected experimental scoring code. Consult the
actual run/branches before claiming how many succeeded.


## Corrected pilot continuation: archived offset 60

[Actions #41587723422](https://github.com/heri-espino/trendestimation/actions/runs/41587723422)
started a nonoverlapping continuation on the same PCAG103A-08 machine,
using the post-normalization source and the same pilot schedule.

[Offset-60 immutable results](https://github.com/heri-espino/trendestimation/tree/results/experiment010-41587723422-a1-pilot-offset60/paper/benchmarks/experiment010/runs/windows-41587723422-a1-pilot-offset60)

- 60/60 method-case subprocesses completed with raw CSVs.
- **680 actual status=ok timing rows** and 680 spectral
  selected-score-parity-only passes. 208 other rows are
  failed/partial; **zero** recorded score disagreements for
  the successfully completed comparisons on this offset.
- Continuation cursor: next_attempt_offset **120** of
  1,800 planned pilot method-case attempts. Later offsets
  120/180/240 are separate jobs and must each be verified
  from their immutable archives before counting successes.
- Do not count these 680 as **numerically independently
  certified**; selected-score parity does not imply accurate
  trend reconstruction in finite precision.

All timings remain archived as raw per-method records, not
inferred from method subprocess wall times.


## Completed corrected pilot through cursor 300 (verified)

All four continuation jobs of
[Actions #41587723422](https://github.com/heri-espino/trendestimation/actions/runs/41587723422)
**completed successfully**, each with an independently archived
immutable results branch. Together, the four windows contributed
**3,200** status=ok full-criterion timing observations:

| Offset | Method-case attempts | Timing records status=ok | Parity only | Failed/partial rows | Next cursor |
|---|---:|---:|---:|---:|---:|
| [60](https://github.com/heri-espino/trendestimation/tree/results/experiment010-41587723422-a1-pilot-offset60) | 60 | 680 | 680 | 208 | 120 |
| [120](https://github.com/heri-espino/trendestimation/tree/results/experiment010-41587723422-a1-pilot-offset120) | 60 | 840 | 840 | 60 | 180 |
| [180](https://github.com/heri-espino/trendestimation/tree/results/experiment010-41587723422-a1-pilot-offset180) | 60 | 840 | 840 | 60 | 240 |
| [240](https://github.com/heri-espino/trendestimation/tree/results/experiment010-41587723422-a1-pilot-offset240) | 60 | 840 | 840 | 60 | 300 |

Combined with the corrected first 60-attempt pilot,
there are **300 out of 1,800** executed pilot method-case
attempts and **3,920** status=ok timing observations.
The corrected smoke contributes a further distinct
420 timing observations, for a total of **4,340**
from the corrected source family. These are not
4,340 independent statistical test problems.
The 1,500 unexecuted pilot attempts and unexecuted
complete factorial remain explicit, and none are
asserted to have physically measured times.
Score-parity successes alone do not establish
independent high-precision numerical correctness.

## Targeted n256/n512 frontier — initiated, not yet verified

[GitHub Actions #41642508020](https://github.com/heri-espino/trendestimation/actions/runs/41642508020)
was launched on PCAG103A-08 to measure ALL ten
complete-criterion method policies at n256 and n512,
with paired three-mean blocks, difference orders
1/2/5/6, four criterion selections GCV/MLE/AICc/CV,
and exact shared S candidates across both policies.
Its two nonoverlapping method-case offsets are
0 and 60. Consult the actual job conclusions and
unique results branches before claiming any
n256/n512 timings or numerical accuracy.
