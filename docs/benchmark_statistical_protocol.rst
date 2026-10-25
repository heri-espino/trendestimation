Formal statistical benchmark protocol
====================================

Purpose
-------

This document specifies a reproducible statistical study of identical
penalized least-squares full-trend reconstructions produced by
three factorizations: SVD of the difference matrix, symmetric
eigendecomposition of its normal product, and banded Cholesky.
It is an experimental protocol, not an assertion that one backend
is universally superior.

Experimental design
-------------------

The methods receive exactly the same synthetic data, order, target
difference mean, and sequence of penalty parameters for each workload.
For every independent data seed, the experiment collects multiple
paired randomized-order timing blocks. Correctness checks are run
before timings and abort the study when solvers disagree.

The **primary outcome** is elapsed wall-clock time for constructing
one solver and reconstructing M full trends from the same data.
Secondary outcomes (reported descriptively) are setup-only,
prepared batched fits, and the amortized prepared single-fit time.
All measurements are saved in nanoseconds.

Averaging technical repetitions as independent observations would
be pseudoreplication. Instead, for each method and independently
generated seed, compute the median over timing blocks.
For method A compared with B, let T(A,s) and T(B,s) denote
the seedwise medians:

.. math::

   L_s = \log\left(\frac{T(A,s)}{T(B,s)}\right),
   \qquad
   \widehat R_{A/B} =
       \exp\left(\frac1K\sum_{s=1}^K L_s\right).

Values above 1 favor method B; values below 1 favor method A.
A ratio of 2 means B used half the time on the geometric-mean scale
for these measured workloads.

Inference and limitations
-------------------------

The primary two-sided null hypothesis is that the expected
paired log ratio equals zero. The analysis uses a sign-flip
randomization test on the mean log ratio: exact enumeration for
up to 16 independent seeds, otherwise deterministic Monte Carlo
randomization with a plus-one correction.

This test assumes sign-exchangeability or symmetry of paired log
differences under its null. Holm step-down multiplicity adjustment
at alpha=0.05 covers **all three algorithm pairs across all declared
workloads**. The pipeline reports only descriptive timing statistics,
not additional hypothesis tests, for secondary outcomes.

Pointwise 95% intervals for the geometric mean time ratio are
obtained by paired bootstrap over independent data seeds, **not**
timing blocks. These intervals are not simultaneous; Holm-adjusted
p-values, rather than pointwise interval exclusion, are the
multiplicity-corrected decisions. With fewer than five independent
data seeds, no inferential p-values are reported.

A significant p-value cannot establish a globally fastest algorithm.
Results apply to the chosen dataset distribution, computer, runtime
libraries and measurement session. For publication, rerun on different
machines, record BLAS threads and version metadata, verify numerical
accuracy, and report absolute effects as well as ratios.

Local runs
----------

Install in the existing conda environment:

.. code-block:: console

   conda activate trendestimation
   python -m pip install -e . threadpoolctl matplotlib

Smoke test the file exports:

.. code-block:: console

   python benchmarks/formal_solver_study.py --preset smoke --seeds 3 --repeats 2 --output-dir build/solver-study-smoke
   python benchmarks/analyze_formal_solver_study.py --input-dir build/solver-study-smoke

Pilot statistical study:

.. code-block:: console

   python benchmarks/formal_solver_study.py --preset quick --seeds 20 --repeats 5 --threads 1 --output-dir paper/benchmarks/solver_study_runs/pilot-01
   python benchmarks/analyze_formal_solver_study.py --input-dir paper/benchmarks/solver_study_runs/pilot-01 --bootstrap 10000 --permutations 50000

Extended experiment (deliberately heavyweight):

.. code-block:: console

   python benchmarks/formal_solver_study.py --preset full --seeds 20 --repeats 7 --threads 1 --output-dir paper/benchmarks/solver_study_runs/full-01
   python benchmarks/analyze_formal_solver_study.py --input-dir paper/benchmarks/solver_study_runs/full-01 --bootstrap 10000 --permutations 50000

The existing case grids are defined in
benchmarks/compare_solver_backends.py. Large dense SVD benchmarks
may require considerable compute; they are never launched during
ordinary CI or documentation builds.

A manual GitHub Actions workflow at
.github/workflows/formal-solver-study.yml creates downloadable
artifacts retained for 90 days. With its optional archive checkbox,
it additionally stores data permanently on an isolated results-only
Git branch, not on the in-progress Marp presentation branch.

Outputs
-------

Raw files:

* raw_measurements.csv: one row per method, independent seed and timing block.
* numerical_accuracy.csv: maximum deviation from SVD per matched dataset.
* study_metadata.json: exact design, Git revision, CPU/BLAS metadata and seeds.

Analysis outputs:

* analysis/timing_summary.csv: per-method median, quartiles and means.
* analysis/paired_comparisons.csv: speedup effect, pointwise interval,
  exact/Monte-Carlo p, Holm-adjusted p and uncertainty flags.
* analysis/results.md: reproducible scientific report and caveats.
* analysis/paper_solver_timings.tex: reviewable LaTeX timing table.
* analysis/paper_solver_speedups.tex: reviewable LaTeX speedup/p-value table.
* analysis/full_fit_*.svg, .png, .pdf: Marp and paper-ready plots.
* analysis/analysis_manifest.json: input SHA-256 provenance and analysis settings.

Archive a run deliberately before incorporating its numerical claims
into the paper or Marp. The current presentation branch is untouched.

See :doc:`solver_backends` for the algorithms and
:doc:`benchmarks` for the earlier comparison.
