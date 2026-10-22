# SMCCA numerical benchmark suite

All experimental source, timings, configurations and optional figures live **under paper/**.
No package source files in src/trendestimation/ are modified.

## Question

How much computation is saved by computing one SVD of the finite-difference
operator and reusing its spectral decomposition for **M different smoothing
parameters**, compared with solving the PLS normal equations each time?

We compare **four** algorithms for the same fixed n, d, mu and lambda grid:

1. dense_fresh — deliberately naive, construct D and D.T@D, then solve the
   full n-by-n normal equations for every lambda;
2. dense_cached — cache Q=D.T@D once, but repeat the dense solve for each lambda;
3. spectral — use the actual public TrendSmoother.fit method (one full SVD
   followed by M reconstructed trends);
4. banded — construct the banded penalty *directly*, then call scipy.linalg
   solve_banded per candidate (proper structural competitor).

A second experiment benchmarks **EDF/trace-only** evaluation:
tr[(I+lambda*Q)^(-1)]. A spectral trace is O(n) after SVD, while
a dense solve of all columns of H is O(n^3) per lambda.

## One command (manual)

From the **repository root** after pip-installing the source checkout:

    python -m pip install -e .
    python -m pip install threadpoolctl
    python paper/benchmarks/run_all.py --preset quick --repeats 5

For a faster smoke check:

    python paper/benchmarks/run_all.py --preset smoke --repeats 2

For a comprehensive CPU run on your own computer:

    python paper/benchmarks/run_all.py --preset full --repeats 7

**Do not commit outputs from somebody else's computer as your own.**
Outputs default to paper/benchmarks/results/ (gitignored). The generated
artifacts include:

- full_fit_timings.csv — setup, M fits, total median, range, median absolute
  deviation, and numerical difference from the banded reference;
- full_fit_speedups.csv — ratios of total times relative to spectral;
- trace_timings.csv — independently measured repeated EDF profiles;
- environment.json — software versions, host, threadpools, CPU count, Git
  revision when available, conditions and complexity models;
- full_fit_plot.dat and trace_plot.dat — optional PGFplots-ready figures;
- full_fit_table.tex and trace_table.tex — generated LaTeX tables of actual
  host measurements in milliseconds;
- benchmark_environment.tex — machine and software provenance for the paper;
- paper_result_manifest.json — numerical deviations and input file provenance.

The run intentionally uses one BLAS thread by default (via threadpoolctl).
This minimizes oversubscription noise, but is not a universal performance
configuration. Document the number of threads you choose and measure
multiple repetitions on an idle host.

The runner automatically generates LaTeX tables from measured CSV outputs:
the paper includes these via conditional \input directives. A manuscript
compiled without raw measurements explicitly says results are pending; it
does not silently substitute pilot timings from a different machine.
The smoke preset is a correctness check, **not** publication-grade timing.
The quick and full presets should be repeated and inspected before publishing.

## Presets

- smoke: three short fits and one trace experiment, to catch errors;
- quick: 13 complete-fit workloads (varying n, d, M, nonzero mu), four trace
  workloads, all four methods;
- full: 21 complete-fit workloads and five trace workloads; increases series
  length up to 400 and M up to 256. Depending on machine this may take time.

A separate correctness check validates the fit methods for the *same*
lambda grid outside all time measurements. Maximum permitted discrepancy is
3e-6 in absolute trend value. High d may be poorly conditioned. The trace
experiment checks agreement to 1e-6. These tolerances are local diagnostic
thresholds and are not mathematical theorems.

## Costs and limits

For fixed differencing order d and M requested **full fitted curves**:

| Algorithm | Setup | M full curves | Dominant storage |
| --- | --- | --- | --- |
| Naive dense | Rebuilt every time | O(M n^3) | O(n^2) |
| Cached dense | O(n^2) storage prep | O(M n^3) | O(n^2) |
| Spectral SVD | O(n^3) | O(M n^2) | O(n^2) |
| Structured banded | O(n d^2) assembly | O(M n d^2) | O(n d) |

These orders are broad arithmetic models, not exact floating-point
operation counts. For EDF/trace sweeps, the spectral method needs only
O(M n) after the spectral decomposition, rather than a matrix of fits.

Spectral fitting need **not** be the fastest at small M. Even at large M,
structured banded solvers can be more efficient. CPU benchmarks do not
demonstrate GPU acceleration; no energy consumption or GPU timing is
measured. Wall time is not a platform-independent cost.

## Paper integration

The paper includes its benchmark methodology, automated result tables,
hardware provenance and optional PGFplots figures in sections/timing_experiments.tex. Run the suite before manual
LaTeX compilation to populate the figures. To publish quantitative claims,
run on the actual source checkout/tag and machine, document the commit SHA,
software/BLAS versions and raw CSV files, and review all tolerances.
