# Experiment005 — Joint numerical accuracy and computational cost

Status: paired hosted pilot completed, 2026-10-29. Not yet a
publication-grade full factorial. Branch: experiment005/joint-accuracy-runtime.

## Sources and provenance

Original run: https://github.com/heri-espino/trendestimation/actions/runs/40966276100

Raw source: paper/benchmarks/experiment005/runs/pilot-hosted-40966276100/

Implementation: paper/benchmarks/experiment005/run_joint.py

Analysis: paper/benchmarks/experiment005/analyze_joint.py

The previous accuracy experiment did not time its numerical solutions; the
previous computational companion did not compare every timed output with
the same 85-digit reference. Experiment005 does both on the same inputs,
same penalty grid, and same processor. Reference computations are excluded
from the measured library runtimes.

Design: n=32,64; d=2,3,5,6; two truth shapes; iid and AR1 noise; seed 0
per condition; fixed mu=0 and empirical mu=mean(D_d y); 17 normalized S
candidates including 0 and 1; three solver families; five selection criteria.
BIC is restricted to S>=0.10 as a sensitivity analysis, not a repaired score.
Three timing repetitions per identical work item; one BLAS thread.
The hosted Linux workflow did NOT use PCAG103A-08.

## Results

3,264 timed fit outputs, 960 criterion-level selection runs, 1,088
candidate reference rows (960 independent 85-digit finite-penalty
references and 128 analytic endpoint projections). Largest recorded
multiprecision KKT residual 1.854e-54.

| Solver | Accurate fits | Inaccurate fits | Failed fits | Largest finite-fit relative error |
| --- | ---: | ---: | ---: | ---: |
| Shift-free SVD | 1088 | 0 | 0 | 9.614e-11 |
| Gram eigendecomposition | 983 | 105 | 0 | 6.812e-2 |
| Banded Cholesky | 907 | 141 | 40 | 6.814e2 |

A selection is admissible only when the backend agrees with the reference
criterion over the complete eligible candidate grid AND its selected fit
is accurate. The reference checks and other post-hoc validation are NOT
charged to the measured end-to-end selection time.

| Solver | Complete valid selections | Invalid grid | Inaccurate selected fit | Failed run |
| --- | ---: | ---: | ---: | ---: |
| Shift-free SVD | 320 | 0 | 0 | 0 |
| Gram eigendecomposition | 252 | 63 | 5 | 0 |
| Banded Cholesky | 0 | 120 | 0 | 200 |

On the 252 paired complete valid eigendecomposition/SVD selections,
the median eigendecomposition-to-SVD warm time ratio was 1.062.
Maximum differences in selected S and latent-trend RMSE were about
1e-12 and 1.41e-7, respectively. These are descriptive host-specific
statistics on selected valid cases, not an unbiased population speed ratio.

## Interpretation and limitations

Full SVD is reliable in this pilot's high-order high-smoothness tests.
Banded Cholesky has valid individual fits but could not finish a complete
accurate full-grid criterion search, so cannot be called a fast winner.
This is NOT evidence that spectral SVD is universally optimal: a specialized
structured GCV implementation may outperform the current score backend.

Only one independent seed per truth/noise condition was tested. The three
timing repetitions are nested within cases and cannot be treated as
independent Monte Carlo replicates. RMSE here measures reconstruction of
the known historical latent trend, not out-of-sample forecast accuracy.
The empirical mu is plugged into conditional CV/ML rather than jointly
estimated or refit after leaving out observations. Endpoint references
are analytic, not 85-digit finite-lambda solves.

Warm selection time includes actual score-grid evaluation plus the chosen
fit, excluding setup and one-time S-grid mapping. Assembled cold cost is
the sum of separately timed stages rather than an independently timed
single call. The source hashes and machine information are saved.

## Research gates before the definitive joint paper

1. Include the stable augmented-QR and dual-SVD fitting routes from the
earlier high-precision study. Do not conflate fit timing with CV/GCV/MLE
scoring time unless the scoring implementation is actually comparable.
2. Add structured selected-inverse GCV/trace computations for a fair
Weinert-style competing algorithm.
3. Confirm the most difficult cases using 55, 85, 110 digit convergence
and retain all numerical failures.
4. After the numerical gate, run multiple independent seeds at wider n,
measure actual repeated-series caching, and construct paired uncertainty
intervals and valid-method time/error Pareto frontiers.
5. Integrate the qualified findings into the combined CSDA manuscript
without rewriting or overwriting the two existing companion papers.

All raw data, scripts, summaries, visualizations, checksums, and agent
handoff remain archived in the repository branch.
