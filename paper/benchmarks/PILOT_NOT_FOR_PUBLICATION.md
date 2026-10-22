# Preliminary local timing observations — NOT FOR PUBLICATION

These numbers are **exploratory checks** made in a Linux execution container
(October 2026), with **one BLAS thread and 3 repetitions**. They used a
small source-compatible replica of the `TrendSmoother` API because this
execution container could not directly clone the GitHub repository.
They are **not** evidence that the exact GitHub release binary was timed.
Use the scripts in this PR to reproduce on the actual checkout and on
Heriberto's computer before incorporating results into the SMCCA text.

- Host: Linux 6.18.55 x86_64 (containerized)
- CPU description: unavailable from `platform.processor()`; 5 logical CPUs
  visible to the benchmark process.
- NumPy 2.3.5; SciPy 1.17.0.
- 1 BLAS thread; 3 full workload repetitions; median end-to-end time.
- Every method returned the same trends within approximately
  `2.1e-13` for the displayed full-fit cases.
- Benchmarks report wall-clock seconds; no energy or GPU data are available.

## Complete fitted trends: d=2, mu=0, M=64

| Method | n=100 (ms) | n=180 (ms) |
|---|---:|---:|
| Dense, fresh D and Q per lambda | 9.454 | 35.130 |
| Dense, Q cached | 7.989 | 19.133 |
| Spectral, SVD prepared once | 3.148 | 8.662 |
| Direct banded solve | **2.301** | **3.657** |

In these exploratory cases, spectral reuse is about 3.00× (n=100)
and 4.06× (n=180) faster than the naive dense method **including
setup**, but the banded solver is faster than spectral by about 1.37×
and 2.37×, respectively. These ratios are specific to the stated
workloads, library versions, and temporary container.

For **one fit** at n=40,d=2, naive dense setup + fitting took
0.0501 ms and spectral setup + fitting 0.528 ms: here spectral
preprocessing was substantially more expensive.

## EDF/trace sweep (including setup)

| n | M | Dense fresh (ms) | Cached dense (ms) | Spectral trace (ms) | Banded trace (ms) |
|---:|---:|---:|---:|---:|---:|
| 40 | 8 | 0.538 | 0.348 | 0.356 | 0.602 |
| 100 | 8 | 2.654 | 2.519 | 1.484 | 1.863 |
| 100 | 32 | 11.270 | 8.817 | **1.499** | 6.137 |
| 180 | 32 | 47.091 | 38.097 | **5.230** | 16.832 |

A trace-only spectral computation is distinct from producing all
the fitted trends. It exploits
`trace(H_lambda)=d+sum_{j=1}^{n-d}1/(1+lambda*delta_j)`
after an expensive one-off factorization.

## Publication-quality protocol

1. Install the actual source revision with `python -m pip install -e .`.
2. Run `python paper/benchmarks/run_all.py --preset full --repeats 7`.
3. Record source commit, CPU model, BLAS implementation, number of
   threads, Python/NumPy/SciPy versions, and raw outputs under
   `paper/benchmarks/results/`.
4. Compare both end-to-end and post-setup times, and disclose
   whether a specialized banded solution wins.
5. Repeat on a second workstation if making a general efficiency claim.
6. Only then move exact numerical findings into the main manuscript.

The manuscript section contains the experimental design and conditional
figures; it does not silently promote these exploratory numbers to
author-verified published measurements.
