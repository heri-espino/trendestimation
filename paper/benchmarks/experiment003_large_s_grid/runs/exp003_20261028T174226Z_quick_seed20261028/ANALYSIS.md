# Experiment003 — Archived results

- Run folder: \`exp003_20261028T174226Z_quick_seed20261028\`
- Preset: \`quick\`
- Python and SciPy versions: 3.11.17, 1.17.1
- Numerical precision: float64; BLAS threads: 1
- Root source revision: \`bae98e76a079528b006a3404ed007606c241e2f4\`
- Numerical maximum absolute trend error: 3.729e-11

**Interpretation:** These are within-host technical timing medians. Seed-level medians are separately archived. They are not publication-grade uncertainty intervals by themselves.

## Matched-workload end-to-end costs

All times below include appropriate setup, mapping and/or factorization costs. These are sums of separately measured components, not a single independently timed monolithic call.

| n | d | M | R | μ | Workflow | Median total (ms) |
|---:|---:|---:|---:|---:|---|---:|
| 128 | 2 | 11 | 4 | 0.0 | S→λ + cached Cholesky | 1.985 |
| 128 | 2 | 11 | 4 | 0.0 | Banded Cholesky, cached λ | 0.599 |
| 128 | 2 | 11 | 4 | 0.0 | Banded Cholesky, uncached λ | 0.772 |
| 128 | 2 | 11 | 4 | 0.0 | Spectral GCV, cached S grid | 2.735 |
| 128 | 2 | 11 | 4 | 0.0 | Spectral GCV, repeated S inversion | 6.006 |
| 128 | 2 | 11 | 4 | 0.0 | S→λ + spectral full trends | 2.725 |
| 128 | 2 | 11 | 4 | 0.0 | Spectral GCV, λ supplied | 1.621 |
| 128 | 2 | 11 | 4 | 0.0 | Spectral full trends, λ supplied | 1.613 |
| 128 | 2 | 11 | 4 | 0.15 | S→λ + cached Cholesky | 1.933 |
| 128 | 2 | 11 | 4 | 0.15 | Banded Cholesky, cached λ | 0.599 |
| 128 | 2 | 11 | 4 | 0.15 | Banded Cholesky, uncached λ | 0.793 |
| 128 | 2 | 11 | 4 | 0.15 | Spectral GCV, cached S grid | 2.668 |
| 128 | 2 | 11 | 4 | 0.15 | Spectral GCV, repeated S inversion | 6.138 |
| 128 | 2 | 11 | 4 | 0.15 | S→λ + spectral full trends | 2.667 |
| 128 | 2 | 11 | 4 | 0.15 | Spectral GCV, λ supplied | 1.564 |
| 128 | 2 | 11 | 4 | 0.15 | Spectral full trends, λ supplied | 1.563 |
| 256 | 2 | 1 | 4 | 0.0 | S→λ + cached Cholesky | 1.325 |
| 256 | 2 | 1 | 4 | 0.0 | Banded Cholesky, cached λ | 0.435 |
| 256 | 2 | 1 | 4 | 0.0 | Banded Cholesky, uncached λ | 0.457 |
| 256 | 2 | 1 | 4 | 0.0 | Spectral GCV, cached S grid | 6.583 |
| 256 | 2 | 1 | 4 | 0.0 | Spectral GCV, repeated S inversion | 7.144 |
| 256 | 2 | 1 | 4 | 0.0 | S→λ + spectral full trends | 6.592 |
| 256 | 2 | 1 | 4 | 0.0 | Spectral GCV, λ supplied | 6.406 |
| 256 | 2 | 1 | 4 | 0.0 | Spectral full trends, λ supplied | 6.416 |
| 256 | 2 | 1 | 4 | 0.15 | S→λ + cached Cholesky | 1.274 |
| 256 | 2 | 1 | 4 | 0.15 | Banded Cholesky, cached λ | 0.424 |
| 256 | 2 | 1 | 4 | 0.15 | Banded Cholesky, uncached λ | 0.437 |
| 256 | 2 | 1 | 4 | 0.15 | Spectral GCV, cached S grid | 6.663 |
| 256 | 2 | 1 | 4 | 0.15 | Spectral GCV, repeated S inversion | 7.182 |
| 256 | 2 | 1 | 4 | 0.15 | S→λ + spectral full trends | 6.669 |
| 256 | 2 | 1 | 4 | 0.15 | Spectral GCV, λ supplied | 6.489 |
| 256 | 2 | 1 | 4 | 0.15 | Spectral full trends, λ supplied | 6.496 |
| 256 | 2 | 11 | 4 | 0.0 | S→λ + cached Cholesky | 3.208 |
| 256 | 2 | 11 | 4 | 0.0 | Banded Cholesky, cached λ | 0.878 |
| 256 | 2 | 11 | 4 | 0.0 | Banded Cholesky, uncached λ | 1.133 |
| 256 | 2 | 11 | 4 | 0.0 | Spectral GCV, cached S grid | 8.594 |
| 256 | 2 | 11 | 4 | 0.0 | Spectral GCV, repeated S inversion | 13.653 |
| 256 | 2 | 11 | 4 | 0.0 | S→λ + spectral full trends | 8.743 |
| 256 | 2 | 11 | 4 | 0.0 | Spectral GCV, λ supplied | 6.932 |
| 256 | 2 | 11 | 4 | 0.0 | Spectral full trends, λ supplied | 7.065 |
| 256 | 2 | 11 | 4 | 0.15 | S→λ + cached Cholesky | 3.215 |
| 256 | 2 | 11 | 4 | 0.15 | Banded Cholesky, cached λ | 0.889 |
| 256 | 2 | 11 | 4 | 0.15 | Banded Cholesky, uncached λ | 1.134 |
| 256 | 2 | 11 | 4 | 0.15 | Spectral GCV, cached S grid | 8.311 |
| 256 | 2 | 11 | 4 | 0.15 | Spectral GCV, repeated S inversion | 13.273 |
| 256 | 2 | 11 | 4 | 0.15 | S→λ + spectral full trends | 8.448 |
| 256 | 2 | 11 | 4 | 0.15 | Spectral GCV, λ supplied | 6.660 |
| 256 | 2 | 11 | 4 | 0.15 | Spectral full trends, λ supplied | 6.797 |
| 256 | 2 | 21 | 4 | 0.0 | S→λ + cached Cholesky | 5.185 |
| 256 | 2 | 21 | 4 | 0.0 | Banded Cholesky, cached λ | 1.310 |
| 256 | 2 | 21 | 4 | 0.0 | Banded Cholesky, uncached λ | 1.833 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral GCV, cached S grid | 10.148 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral GCV, repeated S inversion | 19.441 |
| 256 | 2 | 21 | 4 | 0.0 | S→λ + spectral full trends | 10.415 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral GCV, λ supplied | 7.059 |
| 256 | 2 | 21 | 4 | 0.0 | Spectral full trends, λ supplied | 7.312 |
| 256 | 2 | 21 | 4 | 0.15 | S→λ + cached Cholesky | 5.072 |
| 256 | 2 | 21 | 4 | 0.15 | Banded Cholesky, cached λ | 1.334 |
| 256 | 2 | 21 | 4 | 0.15 | Banded Cholesky, uncached λ | 1.834 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral GCV, cached S grid | 10.027 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral GCV, repeated S inversion | 19.109 |
| 256 | 2 | 21 | 4 | 0.15 | S→λ + spectral full trends | 10.332 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral GCV, λ supplied | 6.942 |
| 256 | 2 | 21 | 4 | 0.15 | Spectral full trends, λ supplied | 7.248 |

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
