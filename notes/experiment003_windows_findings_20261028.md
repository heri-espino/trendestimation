# Experiment003 — Windows results and computational interpretation (2026-10-28)

**Scope:** Only \`heri-espino/trendestimation\`. No results from the separate
\`Trend-Estimation\` project are used. This report reads the four complete,
existing \`experiment003/windows-local\` archives; it runs **no new timed work**.
The numerical source CSVs and source scripts are unchanged.

## Source of truth

Base directory: \`paper/benchmarks/experiment003_large_s_grid/runs/\`

| Run folder | Preset | Distinct data seeds | Timing repetitions | Result |
|---|---|---:|---:|---|
| \`exp003_20261028T174226Z_quick_seed20261028\` | quick | 2 | 3 | complete |
| \`exp003_20261028T174233Z_full_seed20261028\` | full | 3 | 4 | complete |
| \`exp003_20261028T174305Z_large_seed20261028\` | large | 2 | 3 | complete |
| \`exp003_20261028T211219Z_quick_seed20261028\` | quick repeat | 2 | 3 | complete |

All records identify Windows 10 build 26100, Python 3.11.17,
SciPy 1.17.1, single-threaded BLAS, and the same Intel family/model.
The \`full\` and \`large\` source-revision hashes differ from \`quick\`
because earlier benchmark outputs were committed between runs.
GitHub's commit comparison from
\`bae98e76a079528b006a3404ed007606c241e2f4\`
to \`b0421f88af95e78ebbedacbf5c71c8243fb5f017\` shows
**no changes** to either new experimental script; all 38 changed
files belong to output run directories.

The primary numerical QA columns in
\`numerical_validation.csv\` are the maximum absolute discrepancy
between banded Cholesky and full SVD curves at three sampled penalties,
and the relative difference between \`eig_banded\`-derived and SVD-derived
inverse grids.

| Preset | Maximum absolute fitted-curve difference | Maximum inverse penalty relative difference |
|---|---:|---:|
| quick (first) | 3.73e-11 | 9.30e-15 |
| full | 1.06e-7 | 1.09e-13 |
| large | 2.56e-9 | 6.23e-15 |

These are **maximum observed** numerical discrepancies, not inferred
accuracy guarantees. A comprehensive high-smoothness boundary test is
not part of this study: the benchmark restricts targets to
\(S\in[0.15,0.80]\).

## Main matched-length result: an S-only interface does not require full SVD

**Fixed case:** \(d=2,\,M=21,\,R=4,\,\mu=0\); the same 21 penalties
were used for every solver, and all workflows include the appropriate
one-time preparation and parameter mapping costs.
Times are **milliseconds**, based on medians of derived total costs.
For n=256/512 use the \`full\` archive; for n=1024/1536/2048 use
the independent \`large\` archive.

| n | Full SVD + S grid + all trends | Banded eigenvalues + S mapping + cached Cholesky trends | SVD / banded total ratio |
|---:|---:|---:|---:|
| 256 | 10.320 | 5.150 | 2.00 |
| 512 | 44.908 | 9.683 | 4.64 |
| 1024 | 288.788 | 21.888 | 13.19 |
| 1536 | 1111.257 | 39.188 | 28.36 |
| 2048 | 2895.680 | 59.541 | 48.63 |

The ratio rises dramatically with length in this tested range.
At n=2048 the banded S-grid pipeline takes about 60ms while full-SVD
preparation and trends take about 2.90s. The result is **specific
to this PC, dtype, BLAS thread count, grid, and full-curve task**,
not a universal method ranking.

The same n=1024 case gave an SVD-total of 321.942ms in \`full\`
versus 288.788ms in \`large\`, while the corresponding banded totals
were 21.856ms and 21.888ms. The nonidentical timing demonstrates
that even same-host repetitions and different workload ordering
can affect elapsed time. Do not treat those two runs as independent
experimental populations.

## Why the S-only banded pipeline is faster at long n

At \(n=2048,d=2,M=21,R=4,\mu=0\), the phase-summary medians
in \`large\` include:

| Operation | Median time (ms) |
|---|---:|
| Banded \(Q\) setup | 3.372 |
| Banded eigenvalues only (\`eig_banded\`) | 35.369 |
| Convert 21 S targets using banded spectrum | 17.199 |
| Build 21 Cholesky factors | 0.867 |
| Solve all trends on first series with cached factors | 0.688 |
| Solve all trends on remaining 3 series | 1.920 |
| Full SVD setup, alternative pipeline | 2821.607 |

The eigenvalues-only route does **not** allocate/compute a full
dense eigenvector basis. Crucially, the map is not free:
\`eig_banded\` setup + the scalar inverse calls dominate
the S-based banded pipeline. Still, their measured combined
cost is far below full-SVD setup at n=2048.

The known-\(\lambda\) cached-Cholesky workflow at n=2048 cost
**6.906 ms**. The otherwise comparable S-only banded workflow
cost **59.541 ms**. Thus 59.541/6.906 ≈ **8.62×** total overhead
for preparing and converting smoothness targets \emph{when the
other method is handed the correct penalty candidates for free}.
This is a deliberate control, not a fair parameter-selection
comparison: a real \(\lambda\)-only user may incur their own
criterion/search/selection costs.

## Cache reuse has a separate measurable benefit

For \(n=512,d=2,M=21,\mu=0\), increasing the number
of independent series \(R\) shifts total times dramatically:

| R | Repeated inverse per series + GCV (ms) | Invert S grid once + reuse + GCV (ms) | Speedup of caching |
|---:|---:|---:|---:|
| 1 | 42.986 | 42.742 | 1.01× |
| 4 | 58.378 | 43.218 | 1.35× |
| 12 | 99.578 | 43.598 | 2.28× |

The one-time spectral preprocessing is common to both approaches
and dominates when R=1. For R=12, repeated inversion consumes
substantial additional time; the cached strategy moves this
work outside the per-series loop. The same 21 S targets and the
same GCV scores are used.

**Independent quick rerun sanity check:** at n=256,d=2,M=21,R=4,
mu=0, the first and second quick runs reported repeated-inversion
GCV 19.441 vs 20.695ms, cached-inverse GCV 10.148 vs 10.388ms,
and S-grid cached Cholesky 5.185 vs 5.186ms. These are
descriptive repeat measurements, not formal confidence intervals.

For the \(\lambda\)-known baseline, cached banded factorizations
begin to help once the penalty grid is reused across multiple
series. For \(n=512,d=2,M=21,\mu=0\), compare:

| R | Cholesky re-factor each time (ms) | Cache penalty-factor grid (ms) |
|---:|---:|---:|
| 1 | 1.299 | 1.322 |
| 4 | 2.824 | 2.057 |
| 12 | 7.101 | 4.083 |

This directly demonstrates the preparation-versus-reuse crossover:
when only one series is needed, the factor cache does not necessarily
reduce wall time; for 12 series it does.

## Complexity interpretation, with caveats

For fixed low difference order d, the normal-equation matrix
\(A_\lambda=I+\lambda D_d^\top D_d\) has bandwidth \(O(d)\).
A new banded Cholesky factorization costs \(O(nd^2)\) and a
subsequent solve costs \(O(nd)\). With M stored factors, cache
memory is \(O(Mnd)\) and total reuse for R series costs
\(O(Mnd^2+RMnd)\), excluding the one-time S mapping.

Evaluating normalized smoothness \(S(\lambda)\) from positive
penalty eigenvalues costs \(O(n)\), and one safeguarded inverse
with k iterations costs \(O(kn)\) after obtaining the spectrum.
A cached M-point inverse grid therefore costs \(O(Mkn)\).
Computing positive penalty eigenvalues via \`eig_banded\` has
its own, separately measured setup cost; a banded Cholesky
factorization alone does not supply them.

A full SVD/eigendecomposition is a dense \(O(n^3)\)-class
preparation, after which M full reconstructions for R series
have \(O(RMn^2)\) cost. For GCV with preprojected data,
each penalty score can cost \(O(n)\), but projecting each
new observed series still costs \(O(n^2)\).

These complexity bounds are algorithmic approximations,
not predictors of exact crossover sizes. In particular,
\`eig_banded\` must be analyzed as the actual LAPACK
eigenvalue-only procedure; it is **not** the same thing
as a banded Cholesky factorization.

## Current limitations / checks before entering the paper

1. **Small independent-seed counts.** \`full\` uses three distinct
   seeds, \`large\` uses two, and the quick run uses two.
   Technical repeats are not independent data sets. Avoid
   formal significance language and unqualified confidence intervals.
2. **Derived end-to-end totals.** The workflow numbers sum
   individual measured phases, then summarize those totals.
   They are not independent clock measurements of a
   single monolithic operation. Direct total-walltime
   replication is still desirable.
3. **Same-machine specificity.** Only one Windows computer
   and one BLAS thread configuration were tested.
4. **Finite interior grid only.** No \(S\approx 1\)
   conditioning conclusions follow from experiment003.
5. **Single mathematical objective.** GCV scoring is not the
   same cost as reconstructing M full curves. CV with leverage
   diagonals may lead to a different backend ranking.
6. **No automatic production cache yet.** The benchmark explicitly
   precomputes the S-grid/factors, but \`fit_smoothness\`
   or a future \`PreparedSmoothnessGrid\` public cache requires
   its own API and validation review.
7. **Baseline fairness.** Known-\(\lambda\) methods deliberately
   do not pay for selecting or deriving penalties; never interpret
   their times as a complete solution to the S-controlled task.
8. **Numerical comparisons at sampled penalties.** The QA checks
   three positions in each mapped grid; a production-level cache
   implementation should also assert all selected fit/score
   outputs and edge conditions.

## Recommended paper finding

> On the tested Windows host, for matched smoothness grids at
> n=256–2048, an eigenvalues-only banded \(S\to\lambda\) map
> combined with cached banded Cholesky outperformed a
> full-SVD smoothness pipeline for repeated complete trends,
> with measured total-time ratios increasing from about 2×
> at n=256 to about 49× at n=2048. Reusing an already
> mapped grid was additionally beneficial for repeated
> GCV searches across multiple series. These descriptive
> results separate one-time setup, conversion, and reuse
> costs; they are not machine-independent performance guarantees.

Do **not** claim that S is universally faster than lambda,
or that lambda has disappeared from the numerical mathematics.
The contribution is the ability to keep the \emph{scientific
interface} in S while choosing an efficient, explicitly
charged internal backend.

## Reproduction (all data already archived; no rerun required)

All input tables, output plots, setup metadata and validation
files are directly accessible under the four run folders above.
Do not rerun the old numerical study to modify a figure.
Only rerender plots from the existing CSVs:

\`\`\`powershell
python paper\benchmarks\experiment003_analyze.py --run-dir paper\benchmarks\experiment003_large_s_grid\runs\exp003_20261028T174305Z_large_seed20261028

git add .
git commit -m "experiment003: document and render archived large-series results"
git push
\`\`\`

This report is a post-hoc synthesis of archived numerical outputs,
not an additional experiment or a claim of statistical inference.
