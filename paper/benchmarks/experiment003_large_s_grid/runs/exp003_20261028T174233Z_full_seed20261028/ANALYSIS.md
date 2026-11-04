# Experiment003 — Archived results

- Run folder: \`exp003_20261028T174233Z_full_seed20261028\`
- Preset: \`full\`
- Python and SciPy versions: 3.11.17, 1.17.1
- Numerical precision: float64; BLAS threads: 1
- Root source revision: \`dcf9e785e21807a19f7b52a2e4abe3278b86e895\`
- Numerical maximum absolute trend error: 1.057e-07

**Interpretation:** These are within-host technical timing medians. Seed-level medians are separately archived. They are not publication-grade uncertainty intervals by themselves.

## Matched-workload end-to-end costs

All times below include appropriate setup, mapping and/or factorization costs. These are sums of separately measured components, not a single independently timed monolithic call.

| n | d | M | R | μ | Workflow | Median total (ms) |
|---:|---:|---:|---:|---:|---|---:|
| 256 | 2 | 21 | 4 | 0.0 | S→λ + cached Cholesky | 5.150 |
| 256 | 2 | 21 | 4 | 0.0 | Banded Cholesky, cached λ | 1.328 |
| 256 | 2 | 21 | 4 | 0.0 | Banded Cholesky, uncached λ | 1.855 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral GCV, cached S grid | 10.169 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral GCV, repeated S inversion | 19.492 |
| 256 | 2 | 21 | 4 | 0.0 | S→λ + spectral full trends | 10.320 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral GCV, λ supplied | 7.084 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral full trends, λ supplied | 7.237 |
| 256 | 2 | 21 | 4 | 0.15 | S→λ + cached Cholesky | 5.181 |
| 256 | 2 | 21 | 4 | 0.15 | Banded Cholesky, cached λ | 1.329 |
| 256 | 2 | 21 | 4 | 0.15 | Banded Cholesky, uncached λ | 1.828 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral GCV, cached S grid | 10.083 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral GCV, repeated S inversion | 19.276 |
| 256 | 2 | 21 | 4 | 0.15 | S→λ + spectral full trends | 10.233 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral GCV, λ supplied | 6.948 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral full trends, λ supplied | 7.099 |
| 512 | 1 | 21 | 4 | 0.0 | S→λ + cached Cholesky | 9.511 |
| 512 | 1 | 21 | 4 | 0.0 | Banded Cholesky, cached λ | 1.716 |
| 512 | 1 | 21 | 4 | 0.0 | Banded Cholesky, uncached λ | 2.446 |
| 512 | 1 | 21 | 4 | 0.0 | Spectral GCV, cached S grid | 42.793 |
| 512 | 1 | 21 | 4 | 0.0 | Spectral GCV, repeated S inversion | 58.859 |
| 512 | 1 | 21 | 4 | 0.0 | S→λ + spectral full trends | 44.139 |
| 512 | 1 | 21 | 4 | 0.0 | Spectral GCV, λ supplied | 37.560 |
| 512 | 1 | 21 | 4 | 0.0 | Spectral full trends, λ supplied | 38.789 |
| 512 | 1 | 21 | 4 | 0.15 | S→λ + cached Cholesky | 9.524 |
| 512 | 1 | 21 | 4 | 0.15 | Banded Cholesky, cached λ | 1.721 |
| 512 | 1 | 21 | 4 | 0.15 | Banded Cholesky, uncached λ | 2.462 |
| 512 | 1 | 21 | 4 | 0.15 | Spectral GCV, cached S grid | 43.150 |
| 512 | 1 | 21 | 4 | 0.15 | Spectral GCV, repeated S inversion | 59.081 |
| 512 | 1 | 21 | 4 | 0.15 | S→λ + spectral full trends | 44.341 |
| 512 | 1 | 21 | 4 | 0.15 | Spectral GCV, λ supplied | 37.745 |
| 512 | 1 | 21 | 4 | 0.15 | Spectral full trends, λ supplied | 38.993 |
| 512 | 2 | 1 | 4 | 0.0 | S→λ + cached Cholesky | 3.606 |
| 512 | 2 | 1 | 4 | 0.0 | Banded Cholesky, cached λ | 0.862 |
| 512 | 2 | 1 | 4 | 0.0 | Banded Cholesky, uncached λ | 0.859 |
| 512 | 2 | 1 | 4 | 0.0 | Spectral GCV, cached S grid | 37.475 |
| 512 | 2 | 1 | 4 | 0.0 | Spectral GCV, repeated S inversion | 38.382 |
| 512 | 2 | 1 | 4 | 0.0 | S→λ + spectral full trends | 37.537 |
| 512 | 2 | 1 | 4 | 0.0 | Spectral GCV, λ supplied | 37.151 |
| 512 | 2 | 1 | 4 | 0.0 | Spectral full trends, λ supplied | 37.213 |
| 512 | 2 | 1 | 4 | 0.15 | S→λ + cached Cholesky | 3.637 |
| 512 | 2 | 1 | 4 | 0.15 | Banded Cholesky, cached λ | 0.836 |
| 512 | 2 | 1 | 4 | 0.15 | Banded Cholesky, uncached λ | 0.855 |
| 512 | 2 | 1 | 4 | 0.15 | Spectral GCV, cached S grid | 37.241 |
| 512 | 2 | 1 | 4 | 0.15 | Spectral GCV, repeated S inversion | 38.152 |
| 512 | 2 | 1 | 4 | 0.15 | S→λ + spectral full trends | 37.301 |
| 512 | 2 | 1 | 4 | 0.15 | Spectral GCV, λ supplied | 36.957 |
| 512 | 2 | 1 | 4 | 0.15 | Spectral full trends, λ supplied | 37.017 |
| 512 | 2 | 21 | 1 | 0.0 | S→λ + cached Cholesky | 8.944 |
| 512 | 2 | 21 | 1 | 0.0 | Banded Cholesky, cached λ | 1.322 |
| 512 | 2 | 21 | 1 | 0.0 | Banded Cholesky, uncached λ | 1.299 |
| 512 | 2 | 21 | 1 | 0.0 | Spectral GCV, cached S grid | 42.742 |
| 512 | 2 | 21 | 1 | 0.0 | Spectral GCV, repeated S inversion | 42.986 |
| 512 | 2 | 21 | 1 | 0.0 | S→λ + spectral full trends | 43.097 |
| 512 | 2 | 21 | 1 | 0.0 | Spectral GCV, λ supplied | 37.742 |
| 512 | 2 | 21 | 1 | 0.0 | Spectral full trends, λ supplied | 38.097 |
| 512 | 2 | 21 | 1 | 0.15 | S→λ + cached Cholesky | 8.906 |
| 512 | 2 | 21 | 1 | 0.15 | Banded Cholesky, cached λ | 1.310 |
| 512 | 2 | 21 | 1 | 0.15 | Banded Cholesky, uncached λ | 1.287 |
| 512 | 2 | 21 | 1 | 0.15 | Spectral GCV, cached S grid | 41.898 |
| 512 | 2 | 21 | 1 | 0.15 | Spectral GCV, repeated S inversion | 41.936 |
| 512 | 2 | 21 | 1 | 0.15 | S→λ + spectral full trends | 42.268 |
| 512 | 2 | 21 | 1 | 0.15 | Spectral GCV, λ supplied | 36.624 |
| 512 | 2 | 21 | 1 | 0.15 | Spectral full trends, λ supplied | 36.974 |
| 512 | 2 | 21 | 4 | 0.0 | S→λ + cached Cholesky | 9.683 |
| 512 | 2 | 21 | 4 | 0.0 | Banded Cholesky, cached λ | 2.057 |
| 512 | 2 | 21 | 4 | 0.0 | Banded Cholesky, uncached λ | 2.824 |
| 512 | 2 | 21 | 4 | 0.0 | Spectral GCV, cached S grid | 43.218 |
| 512 | 2 | 21 | 4 | 0.0 | Spectral GCV, repeated S inversion | 58.378 |
| 512 | 2 | 21 | 4 | 0.0 | S→λ + spectral full trends | 44.908 |
| 512 | 2 | 21 | 4 | 0.0 | Spectral GCV, λ supplied | 38.044 |
| 512 | 2 | 21 | 4 | 0.0 | Spectral full trends, λ supplied | 39.761 |
| 512 | 2 | 21 | 4 | 0.15 | S→λ + cached Cholesky | 9.547 |
| 512 | 2 | 21 | 4 | 0.15 | Banded Cholesky, cached λ | 2.063 |
| 512 | 2 | 21 | 4 | 0.15 | Banded Cholesky, uncached λ | 2.796 |
| 512 | 2 | 21 | 4 | 0.15 | Spectral GCV, cached S grid | 43.097 |
| 512 | 2 | 21 | 4 | 0.15 | Spectral GCV, repeated S inversion | 57.977 |
| 512 | 2 | 21 | 4 | 0.15 | S→λ + spectral full trends | 44.876 |
| 512 | 2 | 21 | 4 | 0.15 | Spectral GCV, λ supplied | 38.165 |
| 512 | 2 | 21 | 4 | 0.15 | Spectral full trends, λ supplied | 39.944 |
| 512 | 2 | 21 | 12 | 0.0 | S→λ + cached Cholesky | 11.884 |
| 512 | 2 | 21 | 12 | 0.0 | Banded Cholesky, cached λ | 4.083 |
| 512 | 2 | 21 | 12 | 0.0 | Banded Cholesky, uncached λ | 7.101 |
| 512 | 2 | 21 | 12 | 0.0 | Spectral GCV, cached S grid | 43.598 |
| 512 | 2 | 21 | 12 | 0.0 | Spectral GCV, repeated S inversion | 99.578 |
| 512 | 2 | 21 | 12 | 0.0 | S→λ + spectral full trends | 47.536 |
| 512 | 2 | 21 | 12 | 0.0 | Spectral GCV, λ supplied | 38.509 |
| 512 | 2 | 21 | 12 | 0.0 | Spectral full trends, λ supplied | 42.466 |
| 512 | 2 | 21 | 12 | 0.15 | S→λ + cached Cholesky | 11.797 |
| 512 | 2 | 21 | 12 | 0.15 | Banded Cholesky, cached λ | 4.072 |
| 512 | 2 | 21 | 12 | 0.15 | Banded Cholesky, uncached λ | 7.041 |
| 512 | 2 | 21 | 12 | 0.15 | Spectral GCV, cached S grid | 43.551 |
| 512 | 2 | 21 | 12 | 0.15 | Spectral GCV, repeated S inversion | 98.595 |
| 512 | 2 | 21 | 12 | 0.15 | S→λ + spectral full trends | 47.251 |
| 512 | 2 | 21 | 12 | 0.15 | Spectral GCV, λ supplied | 38.168 |
| 512 | 2 | 21 | 12 | 0.15 | Spectral full trends, λ supplied | 41.917 |
| 512 | 2 | 81 | 4 | 0.0 | S→λ + cached Cholesky | 28.047 |
| 512 | 2 | 81 | 4 | 0.0 | Banded Cholesky, cached λ | 5.675 |
| 512 | 2 | 81 | 4 | 0.0 | Banded Cholesky, uncached λ | 8.703 |
| 512 | 2 | 81 | 4 | 0.0 | Spectral GCV, cached S grid | 58.809 |
| 512 | 2 | 81 | 4 | 0.0 | Spectral GCV, repeated S inversion | 117.548 |
| 512 | 2 | 81 | 4 | 0.0 | S→λ + spectral full trends | 63.923 |
| 512 | 2 | 81 | 4 | 0.0 | Spectral GCV, λ supplied | 39.352 |
| 512 | 2 | 81 | 4 | 0.0 | Spectral full trends, λ supplied | 44.306 |
| 512 | 2 | 81 | 4 | 0.15 | S→λ + cached Cholesky | 27.736 |
| 512 | 2 | 81 | 4 | 0.15 | Banded Cholesky, cached λ | 5.656 |
| 512 | 2 | 81 | 4 | 0.15 | Banded Cholesky, uncached λ | 8.612 |
| 512 | 2 | 81 | 4 | 0.15 | Spectral GCV, cached S grid | 58.479 |
| 512 | 2 | 81 | 4 | 0.15 | Spectral GCV, repeated S inversion | 116.509 |
| 512 | 2 | 81 | 4 | 0.15 | S→λ + spectral full trends | 63.226 |
| 512 | 2 | 81 | 4 | 0.15 | Spectral GCV, λ supplied | 39.011 |
| 512 | 2 | 81 | 4 | 0.15 | Spectral full trends, λ supplied | 43.862 |
| 512 | 3 | 21 | 4 | 0.0 | S→λ + cached Cholesky | 10.050 |
| 512 | 3 | 21 | 4 | 0.0 | Banded Cholesky, cached λ | 2.542 |
| 512 | 3 | 21 | 4 | 0.0 | Banded Cholesky, uncached λ | 3.369 |
| 512 | 3 | 21 | 4 | 0.0 | Spectral GCV, cached S grid | 43.419 |
| 512 | 3 | 21 | 4 | 0.0 | Spectral GCV, repeated S inversion | 58.699 |
| 512 | 3 | 21 | 4 | 0.0 | S→λ + spectral full trends | 44.723 |
| 512 | 3 | 21 | 4 | 0.0 | Spectral GCV, λ supplied | 38.411 |
| 512 | 3 | 21 | 4 | 0.0 | Spectral full trends, λ supplied | 39.670 |
| 512 | 3 | 21 | 4 | 0.15 | S→λ + cached Cholesky | 9.963 |
| 512 | 3 | 21 | 4 | 0.15 | Banded Cholesky, cached λ | 2.494 |
| 512 | 3 | 21 | 4 | 0.15 | Banded Cholesky, uncached λ | 3.323 |
| 512 | 3 | 21 | 4 | 0.15 | Spectral GCV, cached S grid | 43.113 |
| 512 | 3 | 21 | 4 | 0.15 | Spectral GCV, repeated S inversion | 58.269 |
| 512 | 3 | 21 | 4 | 0.15 | S→λ + spectral full trends | 44.445 |
| 512 | 3 | 21 | 4 | 0.15 | Spectral GCV, λ supplied | 38.000 |
| 512 | 3 | 21 | 4 | 0.15 | Spectral full trends, λ supplied | 39.264 |
| 1024 | 2 | 21 | 4 | 0.0 | S→λ + cached Cholesky | 21.856 |
| 1024 | 2 | 21 | 4 | 0.0 | Banded Cholesky, cached λ | 3.542 |
| 1024 | 2 | 21 | 4 | 0.0 | Banded Cholesky, uncached λ | 4.840 |
| 1024 | 2 | 21 | 4 | 0.0 | Spectral GCV, cached S grid | 310.679 |
| 1024 | 2 | 21 | 4 | 0.0 | Spectral GCV, repeated S inversion | 337.733 |
| 1024 | 2 | 21 | 4 | 0.0 | S→λ + spectral full trends | 321.942 |
| 1024 | 2 | 21 | 4 | 0.0 | Spectral GCV, λ supplied | 301.756 |
| 1024 | 2 | 21 | 4 | 0.0 | Spectral full trends, λ supplied | 313.019 |
| 1024 | 2 | 21 | 4 | 0.15 | S→λ + cached Cholesky | 21.480 |
| 1024 | 2 | 21 | 4 | 0.15 | Banded Cholesky, cached λ | 3.491 |
| 1024 | 2 | 21 | 4 | 0.15 | Banded Cholesky, uncached λ | 4.773 |
| 1024 | 2 | 21 | 4 | 0.15 | Spectral GCV, cached S grid | 310.072 |
| 1024 | 2 | 21 | 4 | 0.15 | Spectral GCV, repeated S inversion | 336.783 |
| 1024 | 2 | 21 | 4 | 0.15 | S→λ + spectral full trends | 321.169 |
| 1024 | 2 | 21 | 4 | 0.15 | Spectral GCV, λ supplied | 301.121 |
| 1024 | 2 | 21 | 4 | 0.15 | Spectral full trends, λ supplied | 312.217 |

## Figures

All diagrams use pinned AwesomeFigures APIs.
- scaling_matched_workloads.pdf
- scaling_matched_workloads.svg
- scaling_matched_workloads.png
- preparation_breakdown.pdf
- preparation_breakdown.svg
- preparation_breakdown.png
- reused_series.pdf
- reused_series.svg
- reused_series.png

## Limitations
- Do not compare distinct M or R as if only n changed.
- The S-grid and internal penalties are matched across solvers.
- The known-lambda baseline intentionally omits the cost of choosing S.
- S inversion from banded eigenvalues costs setup and iterations; it is not free or inherent to a Cholesky factorization.
- GCV scoring uses the spectral eigensystem; it is a different workload from M full reconstructed trends.
- The timings are hardware-, thread-, workload- and reuse-dependent.
- Technical repetitions are not independent data seeds.
