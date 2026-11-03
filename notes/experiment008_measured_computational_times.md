# Experiment008 — committed computational timing results

Research goal: complete-criterion elapsed time, **not RMSE**. All figures in this note are real repository data, not fabricated extrapolations.

## Exact measurement provenance (2026-11-02)

| Immutable result branch | Actual successful rows | Completed slices | Notes |
| --- | ---: | ---: | --- |
| results/experiment008-hosted-41528426191 | 392 | 9 | initial hosted batch; mu=data CLI forwarding error affected 10 other slices (excluded) and 5 slices timed out |
| results/experiment008-hosted-41529170696 | 632 | 15 | corrected conditional mu=data; no CLI errors, 9 slice timeouts |
| results/experiment008-hosted-broad-41529218986 | 2214 | 42 | round-robin n,d; 8 timeouts; other 2374 candidate slices not executed within batch budget |
| results/experiment008-naive-41530425009 | 1008 | 14 | real explicit inverse versus SVD versus banded, all 1008 rows valid, including 168 naive full-grid timing rows |

**Total:** 4246 real successful timing records from these completed runs. This is **not** 4246 independent data seeds: repetitions, method choices, and matched workloads share input series. All data are in the above pushed results branches, including raw_times.csv, summary.csv, paired_speedups.csv, environment.json, hardware/BLAS information and status masks.

## The complete plan is not the measured tensor

Each hosted batch archives full_factorial_plan.csv.gz with **252000** distinct planned factorial cells (one-S workloads deduplicated across grid denominator). Under the declared hardware/work model: 111600 marked eligible, 120000 budget_exceeded, 3600 infeasible_naive_runtime and 16800 infeasible_dense_memory. Eligibility is only a plan estimate, not a completed timing result. The 100000 candidate grid at n=131072 with dense inversion is physically infeasible; one dense float64 n*n array alone uses 128 GiB.

## Actual baseline comparison (n=64/128, d=2, mu='data', GCV)

All times are mean cold setup+selection from 3 repeated runs on the same GitHub-hosted workflow, mapped-lambda policy. Milliseconds:

| Method | n=64, one S | n=64, grid M=100 | n=128, grid M=100 |
| --- | ---: | ---: | ---: |
| Literal dense inverse | 1.3233 | 21.6907 | 59.1485 |
| Full SVD | 2.2111 | 13.2453 | 18.3545 |
| Banded Cholesky | 1.9077 | 37.5285 | 60.0780 |

The SVD is roughly 1.64x faster than explicit inversion at n=64/M=100 and 3.22x at n=128/M=100 for this particular complete-GCV workload. Conversely, naive inversion was fastest at n=64/M=1. Do not call those ratios universal; the n=64/128 limited pilot is not a complexity proof.

## Measured AICc scaling on the broad hosted batch

For d=1, fixed mu=0, high-amplitude y, mapped-lambda, one series, S grid M=100:

| n | SVD ms | Banded Cholesky ms | Sparse LU + exact banded-trace ms |
| --: | --: | --: | --: |
| 64 | 19.10 | 47.00 | 67.21 |
| 128 | 24.17 | 75.55 | 88.14 |
| 256 | 51.14 | 111.27 | 135.96 |
| 512 | Not measured (resource gate) | 256.46 | 282.61 |

Two repeated timings per cell; full SVD setup is included and the backend is not allowed to win an invalid numerical cell. Limited n ranges and Python overhead mean observed slopes are not asymptotic O(n^p) proofs.

## Known exclusions and next batches

- The n16384/131072 structured-only Windows task was triggered at GitHub Actions run 41527345441; inspect its eventual published results branch instead of guessing a time.
- The bounded self-hosted pilot and broad matrix jobs were triggered at run 41529113497; no Windows results are counted here before committed CSVs exist.
- CV/GCV/AICc/BIC for mu=data are *conditional plug-in* scores, not exact leave-one-out re-estimation of the data-derived mean. MLE is also conditional plug-in.
- Pure fit-only speed is never reported as full-criterion selection time. The sparse and PCG hybrids include extra exact banded leverage/EDF and likelihood work.
- Improve high-n selected inverse mapping, numerical forward-error checks, and matched independent seed repetitions before final publication rankings. Preserve completed historic runs even when better algorithms supersede them.
