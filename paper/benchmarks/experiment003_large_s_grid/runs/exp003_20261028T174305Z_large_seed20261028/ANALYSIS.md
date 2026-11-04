# Experiment003 — Archived results

- Run folder: \`exp003_20261028T174305Z_large_seed20261028\`
- Preset: \`large\`
- Python and SciPy versions: 3.11.17, 1.17.1
- Numerical precision: float64; BLAS threads: 1
- Root source revision: \`b0421f88af95e78ebbedacbf5c71c8243fb5f017\`
- Numerical maximum absolute trend error: 2.561e-09

**Interpretation:** These are within-host technical timing medians. Seed-level medians are separately archived. They are not publication-grade uncertainty intervals by themselves.

## Matched-workload end-to-end costs

All times below include appropriate setup, mapping and/or factorization costs. These are sums of separately measured components, not a single independently timed monolithic call.

| n | d | M | R | μ | Workflow | Median total (ms) |
|---:|---:|---:|---:|---:|---|---:|
| 1024 | 2 | 21 | 4 | 0.0 | S→λ + cached Cholesky | 21.888 |
| 1024 | 2 | 21 | 4 | 0.0 | Banded Cholesky, cached λ | 3.652 |
| 1024 | 2 | 21 | 4 | 0.0 | Banded Cholesky, uncached λ | 4.872 |
| 1024 | 2 | 21 | 4 | 0.0 | Spectral GCV, cached S grid | 281.258 |
| 1024 | 2 | 21 | 4 | 0.0 | Spectral GCV, repeated S inversion | 309.216 |
| 1024 | 2 | 21 | 4 | 0.0 | S→λ + spectral full trends | 288.788 |
| 1024 | 2 | 21 | 4 | 0.0 | Spectral GCV, λ supplied | 272.243 |
| 1024 | 2 | 21 | 4 | 0.0 | Spectral full trends, λ supplied | 279.773 |
| 1024 | 2 | 21 | 4 | 0.15 | S→λ + cached Cholesky | 22.036 |
| 1024 | 2 | 21 | 4 | 0.15 | Banded Cholesky, cached λ | 3.481 |
| 1024 | 2 | 21 | 4 | 0.15 | Banded Cholesky, uncached λ | 4.906 |
| 1024 | 2 | 21 | 4 | 0.15 | Spectral GCV, cached S grid | 283.542 |
| 1024 | 2 | 21 | 4 | 0.15 | Spectral GCV, repeated S inversion | 310.942 |
| 1024 | 2 | 21 | 4 | 0.15 | S→λ + spectral full trends | 290.889 |
| 1024 | 2 | 21 | 4 | 0.15 | Spectral GCV, λ supplied | 274.649 |
| 1024 | 2 | 21 | 4 | 0.15 | Spectral full trends, λ supplied | 281.842 |
| 1024 | 2 | 81 | 4 | 0.0 | S→λ + cached Cholesky | 54.288 |
| 1024 | 2 | 81 | 4 | 0.0 | Banded Cholesky, cached λ | 9.059 |
| 1024 | 2 | 81 | 4 | 0.0 | Banded Cholesky, uncached λ | 14.075 |
| 1024 | 2 | 81 | 4 | 0.0 | Spectral GCV, cached S grid | 313.545 |
| 1024 | 2 | 81 | 4 | 0.0 | Spectral GCV, repeated S inversion | 419.247 |
| 1024 | 2 | 81 | 4 | 0.0 | S→λ + spectral full trends | 340.375 |
| 1024 | 2 | 81 | 4 | 0.0 | Spectral GCV, λ supplied | 278.423 |
| 1024 | 2 | 81 | 4 | 0.0 | Spectral full trends, λ supplied | 306.210 |
| 1024 | 2 | 81 | 4 | 0.15 | S→λ + cached Cholesky | 53.616 |
| 1024 | 2 | 81 | 4 | 0.15 | Banded Cholesky, cached λ | 9.012 |
| 1024 | 2 | 81 | 4 | 0.15 | Banded Cholesky, uncached λ | 14.014 |
| 1024 | 2 | 81 | 4 | 0.15 | Spectral GCV, cached S grid | 310.286 |
| 1024 | 2 | 81 | 4 | 0.15 | Spectral GCV, repeated S inversion | 413.650 |
| 1024 | 2 | 81 | 4 | 0.15 | S→λ + spectral full trends | 337.727 |
| 1024 | 2 | 81 | 4 | 0.15 | Spectral GCV, λ supplied | 275.099 |
| 1024 | 2 | 81 | 4 | 0.15 | Spectral full trends, λ supplied | 302.016 |
| 1536 | 2 | 21 | 4 | 0.0 | S→λ + cached Cholesky | 39.188 |
| 1536 | 2 | 21 | 4 | 0.0 | Banded Cholesky, cached λ | 5.114 |
| 1536 | 2 | 21 | 4 | 0.0 | Banded Cholesky, uncached λ | 6.893 |
| 1536 | 2 | 21 | 4 | 0.0 | Spectral GCV, cached S grid | 1090.370 |
| 1536 | 2 | 21 | 4 | 0.0 | Spectral GCV, repeated S inversion | 1131.045 |
| 1536 | 2 | 21 | 4 | 0.0 | S→λ + spectral full trends | 1111.257 |
| 1536 | 2 | 21 | 4 | 0.0 | Spectral GCV, λ supplied | 1076.969 |
| 1536 | 2 | 21 | 4 | 0.0 | Spectral full trends, λ supplied | 1097.129 |
| 1536 | 2 | 21 | 4 | 0.15 | S→λ + cached Cholesky | 39.720 |
| 1536 | 2 | 21 | 4 | 0.15 | Banded Cholesky, cached λ | 5.201 |
| 1536 | 2 | 21 | 4 | 0.15 | Banded Cholesky, uncached λ | 7.104 |
| 1536 | 2 | 21 | 4 | 0.15 | Spectral GCV, cached S grid | 1110.228 |
| 1536 | 2 | 21 | 4 | 0.15 | Spectral GCV, repeated S inversion | 1154.282 |
| 1536 | 2 | 21 | 4 | 0.15 | S→λ + spectral full trends | 1129.073 |
| 1536 | 2 | 21 | 4 | 0.15 | Spectral GCV, λ supplied | 1097.011 |
| 1536 | 2 | 21 | 4 | 0.15 | Spectral full trends, λ supplied | 1115.856 |
| 2048 | 2 | 21 | 4 | 0.0 | S→λ + cached Cholesky | 59.541 |
| 2048 | 2 | 21 | 4 | 0.0 | Banded Cholesky, cached λ | 6.906 |
| 2048 | 2 | 21 | 4 | 0.0 | Banded Cholesky, uncached λ | 9.513 |
| 2048 | 2 | 21 | 4 | 0.0 | Spectral GCV, cached S grid | 2842.417 |
| 2048 | 2 | 21 | 4 | 0.0 | Spectral GCV, repeated S inversion | 2896.866 |
| 2048 | 2 | 21 | 4 | 0.0 | S→λ + spectral full trends | 2895.680 |
| 2048 | 2 | 21 | 4 | 0.0 | Spectral GCV, λ supplied | 2825.074 |
| 2048 | 2 | 21 | 4 | 0.0 | Spectral full trends, λ supplied | 2878.050 |
| 2048 | 2 | 21 | 4 | 0.15 | S→λ + cached Cholesky | 61.043 |
| 2048 | 2 | 21 | 4 | 0.15 | Banded Cholesky, cached λ | 6.736 |
| 2048 | 2 | 21 | 4 | 0.15 | Banded Cholesky, uncached λ | 9.573 |
| 2048 | 2 | 21 | 4 | 0.15 | Spectral GCV, cached S grid | 2830.282 |
| 2048 | 2 | 21 | 4 | 0.15 | Spectral GCV, repeated S inversion | 2881.988 |
| 2048 | 2 | 21 | 4 | 0.15 | S→λ + spectral full trends | 2882.477 |
| 2048 | 2 | 21 | 4 | 0.15 | Spectral GCV, λ supplied | 2813.644 |
| 2048 | 2 | 21 | 4 | 0.15 | Spectral full trends, λ supplied | 2865.839 |

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
