# Experiment003 — Archived results

- Run folder: \`exp003_20261028T211219Z_quick_seed20261028\`
- Preset: \`quick\`
- Python and SciPy versions: 3.11.17, 1.17.1
- Numerical precision: float64; BLAS threads: 1
- Root source revision: \`3f81582fd94f66e87dd6d5abfcd3e97783ab5ce0\`
- Numerical maximum absolute trend error: 3.729e-11

**Interpretation:** These are within-host technical timing medians. Seed-level medians are separately archived. They are not publication-grade uncertainty intervals by themselves.

## Matched-workload end-to-end costs

All times below include appropriate setup, mapping and/or factorization costs. These are sums of separately measured components, not a single independently timed monolithic call.

| n | d | M | R | μ | Workflow | Median total (ms) |
|---:|---:|---:|---:|---:|---|---:|
| 128 | 2 | 11 | 4 | 0.0 | S→λ + cached Cholesky | 1.973 |
| 128 | 2 | 11 | 4 | 0.0 | Banded Cholesky, cached λ | 0.614 |
| 128 | 2 | 11 | 4 | 0.0 | Banded Cholesky, uncached λ | 0.837 |
| 128 | 2 | 11 | 4 | 0.0 | Spectral GCV, cached S grid | 2.750 |
| 128 | 2 | 11 | 4 | 0.0 | Spectral GCV, repeated S inversion | 6.155 |
| 128 | 2 | 11 | 4 | 0.0 | S→λ + spectral full trends | 2.718 |
| 128 | 2 | 11 | 4 | 0.0 | Spectral GCV, λ supplied | 1.572 |
| 128 | 2 | 11 | 4 | 0.0 | Spectral full trends, λ supplied | 1.555 |
| 128 | 2 | 11 | 4 | 0.15 | S→λ + cached Cholesky | 1.978 |
| 128 | 2 | 11 | 4 | 0.15 | Banded Cholesky, cached λ | 0.608 |
| 128 | 2 | 11 | 4 | 0.15 | Banded Cholesky, uncached λ | 0.835 |
| 128 | 2 | 11 | 4 | 0.15 | Spectral GCV, cached S grid | 2.649 |
| 128 | 2 | 11 | 4 | 0.15 | Spectral GCV, repeated S inversion | 6.197 |
| 128 | 2 | 11 | 4 | 0.15 | S→λ + spectral full trends | 2.639 |
| 128 | 2 | 11 | 4 | 0.15 | Spectral GCV, λ supplied | 1.514 |
| 128 | 2 | 11 | 4 | 0.15 | Spectral full trends, λ supplied | 1.510 |
| 256 | 2 | 1 | 4 | 0.0 | S→λ + cached Cholesky | 1.352 |
| 256 | 2 | 1 | 4 | 0.0 | Banded Cholesky, cached λ | 0.462 |
| 256 | 2 | 1 | 4 | 0.0 | Banded Cholesky, uncached λ | 0.476 |
| 256 | 2 | 1 | 4 | 0.0 | Spectral GCV, cached S grid | 6.761 |
| 256 | 2 | 1 | 4 | 0.0 | Spectral GCV, repeated S inversion | 7.301 |
| 256 | 2 | 1 | 4 | 0.0 | S→λ + spectral full trends | 6.769 |
| 256 | 2 | 1 | 4 | 0.0 | Spectral GCV, λ supplied | 6.583 |
| 256 | 2 | 1 | 4 | 0.0 | Spectral full trends, λ supplied | 6.591 |
| 256 | 2 | 1 | 4 | 0.15 | S→λ + cached Cholesky | 1.385 |
| 256 | 2 | 1 | 4 | 0.15 | Banded Cholesky, cached λ | 0.483 |
| 256 | 2 | 1 | 4 | 0.15 | Banded Cholesky, uncached λ | 0.514 |
| 256 | 2 | 1 | 4 | 0.15 | Spectral GCV, cached S grid | 6.790 |
| 256 | 2 | 1 | 4 | 0.15 | Spectral GCV, repeated S inversion | 7.439 |
| 256 | 2 | 1 | 4 | 0.15 | S→λ + spectral full trends | 6.798 |
| 256 | 2 | 1 | 4 | 0.15 | Spectral GCV, λ supplied | 6.612 |
| 256 | 2 | 1 | 4 | 0.15 | Spectral full trends, λ supplied | 6.621 |
| 256 | 2 | 11 | 4 | 0.0 | S→λ + cached Cholesky | 3.309 |
| 256 | 2 | 11 | 4 | 0.0 | Banded Cholesky, cached λ | 0.894 |
| 256 | 2 | 11 | 4 | 0.0 | Banded Cholesky, uncached λ | 1.149 |
| 256 | 2 | 11 | 4 | 0.0 | Spectral GCV, cached S grid | 8.665 |
| 256 | 2 | 11 | 4 | 0.0 | Spectral GCV, repeated S inversion | 13.820 |
| 256 | 2 | 11 | 4 | 0.0 | S→λ + spectral full trends | 8.809 |
| 256 | 2 | 11 | 4 | 0.0 | Spectral GCV, λ supplied | 6.818 |
| 256 | 2 | 11 | 4 | 0.0 | Spectral full trends, λ supplied | 6.962 |
| 256 | 2 | 11 | 4 | 0.15 | S→λ + cached Cholesky | 3.276 |
| 256 | 2 | 11 | 4 | 0.15 | Banded Cholesky, cached λ | 0.898 |
| 256 | 2 | 11 | 4 | 0.15 | Banded Cholesky, uncached λ | 1.178 |
| 256 | 2 | 11 | 4 | 0.15 | Spectral GCV, cached S grid | 8.584 |
| 256 | 2 | 11 | 4 | 0.15 | Spectral GCV, repeated S inversion | 13.564 |
| 256 | 2 | 11 | 4 | 0.15 | S→λ + spectral full trends | 8.735 |
| 256 | 2 | 11 | 4 | 0.15 | Spectral GCV, λ supplied | 6.775 |
| 256 | 2 | 11 | 4 | 0.15 | Spectral full trends, λ supplied | 6.926 |
| 256 | 2 | 21 | 4 | 0.0 | S→λ + cached Cholesky | 5.186 |
| 256 | 2 | 21 | 4 | 0.0 | Banded Cholesky, cached λ | 1.348 |
| 256 | 2 | 21 | 4 | 0.0 | Banded Cholesky, uncached λ | 1.882 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral GCV, cached S grid | 10.388 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral GCV, repeated S inversion | 20.695 |
| 256 | 2 | 21 | 4 | 0.0 | S→λ + spectral full trends | 10.668 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral GCV, λ supplied | 7.246 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral full trends, λ supplied | 7.526 |
| 256 | 2 | 21 | 4 | 0.15 | S→λ + cached Cholesky | 5.115 |
| 256 | 2 | 21 | 4 | 0.15 | Banded Cholesky, cached λ | 1.309 |
| 256 | 2 | 21 | 4 | 0.15 | Banded Cholesky, uncached λ | 1.880 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral GCV, cached S grid | 10.037 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral GCV, repeated S inversion | 20.451 |
| 256 | 2 | 21 | 4 | 0.15 | S→λ + spectral full trends | 10.314 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral GCV, λ supplied | 6.935 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral full trends, λ supplied | 7.232 |

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
