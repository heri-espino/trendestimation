# Preliminary local timing observations — NOT FOR PUBLICATION

These are **exploratory** wall-clock results from a Linux execution
container (October 2026), **one BLAS thread and five repetitions**.
A local source-compatible replica of the TrendSmoother API was used,
rather than an exact installation of a tagged GitHub checkout.
Consequently these are **not author-machine or release benchmarks**.
The reproducible benchmark scripts in this PR call the real public
library API when run from an installed checkout.

- Host: Linux 6.18.55 x86_64, containerized; processor model not exposed.
- 5 logical CPU resources reported by the container runtime.
- NumPy 2.3.5; SciPy 1.17.0; 1 BLAS thread; median of five repeats.
- All compared trends passed numerical parity checks to the declared tolerance.
- End-to-end times include setup; these times may vary even within one host.

## Full fitted curves (d=2, mu=0, M=64)

| Algorithm | n=100 (ms) | n=180 (ms) |
| --- | ---: | ---: |
| Naive fresh dense solve | 9.887 | 34.121 |
| Cached-Q dense solve | 5.469 | 19.046 |
| Reused spectral SVD | 3.375 | 7.231 |
| Direct banded solve | **2.386** | **2.908** |

The spectral method was about 2.93× faster than the naive fresh dense
approach at n=100 and 4.72× at n=180, **including SVD preparation**.
The directly banded method was even faster than spectral by
approximately 1.41× and 2.49× respectively.

**One fit** at n=100, d=2 showed the opposite preference:
fresh dense ~0.126 ms, spectral ~1.51 ms, because a full SVD
was computed for a single requested value of lambda.

## EDF/trace evaluations (setup plus M evaluations)

| n | M | Fresh dense trace (ms) | Cached dense trace (ms) | Spectral trace (ms) | Banded trace (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 40 | 8 | 0.485 | 0.418 | 0.329 | 0.511 |
| 100 | 8 | 3.669 | 2.372 | 1.958 | **1.754** |
| 100 | 32 | 11.137 | 10.335 | **1.785** | 8.274 |
| 180 | 32 | 57.000 | 44.777 | **5.582** | 18.132 |

These trace numbers refer to computing tr(H), **not** to fitting
a complete trend M times. The spectral method uses a sum over
eigenvalues after the initial factorization.

## Remaining verification before journal inclusion

Run `python paper/benchmarks/run_all.py --preset full --repeats 7`
from an installed **exact** source revision; keep the generated
`paper/benchmarks/results/` CSVs and the environment manifest.
Record the CPU model, BLAS vendor/thread count, source commit and
runtime variation. Independently verify the numerical tolerances.

Avoid a claim that spectral is always faster than structured banded
solvers. GPU execution, electricity use, and actual monetary cost have
**not been measured**.
