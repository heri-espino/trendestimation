# Experiment012 — controlled 100-seed amortization of complete CV/GCV

Status: **implementation and reproducibility protocol**. No measured
Experiment012 timing results have been collected or reported by this
change. This is a separate, newly numbered experiment; the 97-seed
Experiment011 observations remain immutable.

## Scientific question

For the same synthetic series and the same sequence of distinct penalties,
how do the measured, **complete statistical criterion** costs differ between

1. `naive_inverse`: explicit dense `numpy.linalg.inv(I+lambda D.T D)` per
   new penalty, including criterion-specific residuals and leverages;
2. `banded_cholesky`: new banded factorization, selected-inverse diagnostic
   and complete criterion for each penalty; and
3. `spectral_svd`: one reusable SVD of the difference matrix, once-per-series
   spectral projection, then diagonal criterion evaluations?

All three methods use the SAME `Evaluator` in
`paper/benchmarks/experiment006/run.py`, same fixed `mu=0`, same
synthetic data, same criterion (CV or GCV), same ordered penalty grid,
one process, one BLAS thread, and a rotated method execution order.

The predeclared distinct penalty grid is geometrically spaced from
1e-3 to 1e3, with prefixes of **1, 10, 100, 1,000** at n=64. The predeclared maximum is 100 at n=128 and 10 at n=256 to bound the cost of repeated dense inverses. This is *not* the
Experiment011 normalized-S grid; it intentionally avoids timing the
shared S-to-lambda mapper and isolates full criterion evaluation,
method initialization and reuse. Do not present its timings as the
same exact computational task as the existing direct-S/mapped-lambda
Experiment011 rows. Here, "inversion 10" means the 10th distinct
penalty criterion evaluation, **not** inverting the same frozen matrix
10 times. Reusing a single fixed-lambda Cholesky factor can also
amortize and is a different experiment.

For each method/seed/prefix, the runner saves method setup plus the
cumulative measured criterion evaluation time, first-evaluation time,
number completed, selected penalty and criterion score, and error
status. A separate numerical audit compares the selected solution with
the explicit dense reference; numerical mismatches are **not** claimed
as measured speed winners.

The 100 independent seeds are new to this homogeneous single-worker
campaign, not relabeled legacy seed identities. Rotate method order
to reduce execution-order drift. Use CPU idle-state documentation,
environment metadata, single-thread BLAS, matching seeds and complete
numerical masks. The sample size is 100 **only after** 100 seeds have
actually finished; otherwise label measured coverage.

## Reproduce (PCAG103A-08)

From the repository root after activating the verified environment:

```powershell
python paper/benchmarks/experiment012/run.py --n 64 --d 3 --criterion gcv --seeds 100 --checkpoints 1,10,100,1000
# The preceding command is PLAN ONLY.
python paper/benchmarks/experiment012/run.py --n 64 --d 3 --criterion gcv --seeds 100 --checkpoints 1,10,100,1000 --execute --out paper/benchmarks/experiment012/runs/pc08_experiment012_001
# Never re-use the same output directory.
python paper/benchmarks/experiment012/render.py --input paper/benchmarks/experiment012/runs/pc08_experiment012_001 --out paper/benchmarks/experiment012/figures/pc08_experiment012_001
python -m pytest tests/test_springer_amortization.py -q
```

The renderer refuses to draw the publication plot unless all 100
seed indices have recorded a status for all three methods and every
checkpoint, the source CSV hash matches, and at least 20 paired valid
seeds are available at each checkpoint. The published line medians
use the SAME intersection of valid seeds among the three methods.
The source plot uses real AwesomeFigures
(`set_style`, `color_palette`, `save_figure`), and saves PDF/SVG/PNG
plus a SHA-256 evidence summary. Do not insert a hypothetical plot in
the Springer manuscript. Evaluate the numerical audit before
interpreting conditional timings.

The new manually dispatched workflow
`.github/workflows/springer-100seed-amortization-pc08.yml` runs on the
specific Windows PC08 runner and archives all raw files and derived
figures under a unique results-only Git branch. No workflow executes
a large benchmark automatically on a push.

## Experiment011: closing 97 -> 100 without restarting

`paper/benchmarks/experiment011/complete_100_seeds.py` prepares three
**additional** seed indices `s100`, `s101`, `s102` for each of 29
historical cases. The original 97 indices are `s003..s099`, giving
`97+3=100` proposed independent realizations per case. Run the new
jobs only, archive their raw records and recompute a **new** hash-audited
timing tensor using both datasets. Do not merely edit 97 to 100 in
`paper/main.tex`; the existing reported statistics and 95% intervals
cannot be reused unchanged.

The historical workload had phases of 24, 12 and one concurrent job;
the extension may have a different phase. For any new aggregate, record
concurrency and source environment **as strata**, and do not interpret
the 100 as 100 identically timed isolated CPU samples. The old 2,813
job report, raw snapshots, plots, PDF and manuscript claims remain
preserved until validated replacements exist.

## Planned publication deliverable

After the two new datasets are verified, regenerate a distinct
AwesomeFigures amortization comparison with all **three** real backends;
show prefix checkpoint 1/10/100/1000, setup cost, valid-pair support and
conditional timing ratios. Retain method-level exclusions, numerical
status and the original complete-criterion figures, not fabricated
naive times at infeasible n. Recalculate the Springer abstract, methods,
tables, confidence intervals and figure captions from the new audit
before changing the claimed seed count.

No new numerical performance result, figure or PDF is asserted
by this code-only protocol.
