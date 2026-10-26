Grid search and solver reuse: measured comparisons
===================================================

The fastest numerical backend depends on the task. A full fitted trend at
a known penalty and a GCV search are different computational workloads.

.. list-table:: Public API defaults by task
   :header-rows: 1
   :widths: 29 33 38

   * - Task
     - Default
     - Why
   * - Fit a trend only
     - ``fit_penalized`` and ``PreparedPLSSolver``: banded Cholesky
     - Efficient banded full-trend reconstruction without extra EDF work
   * - Select by CV/GCV/AICc/BIC
     - ``TrendSmoother`` with ``select_lambda``: spectral SVD
     - Spectral EDF, RSS and leverage formulas are reusable across candidates
   * - Fit with EDF and smoothness metadata
     - ``TrendSmoother.fit`` and ``fit_trend``: spectral SVD
     - Exact conditional EDF and normalized smoothness are reported

Each method minimizes the same PLS objective. Banded Cholesky is a
fit-only default based on measured workloads, not a universal winner.

Measured GCV comparison
-----------------------

The six solver methods (fresh dense, cached dense, SVD, general banded,
dense Cholesky, banded Cholesky) were compared on **actual GCV candidate
searches**. End-to-end times include method setup and calculation of
both a fitted trend and the effective degrees of freedom needed for GCV.
The separate fit-only experiment does not pay the same EDF cost.

The recorded GitHub-hosted Linux quick run used Python 3.11.17,
NumPy 2.4.6, SciPy 1.17.1, one BLAS thread, three repetitions,
n=48, M=11 log-spaced positive finite penalties, R=1 independent
series and fixed :math:`\mu=0`.

.. list-table:: End-to-end GCV time, milliseconds
   :header-rows: 1
   :widths: 21 26 30 23

   * - Order d
     - Spectral SVD
     - Banded Cholesky
     - Fastest here
   * - 1
     - 0.630
     - 1.205
     - SVD
   * - 2
     - 0.622
     - 1.287
     - SVD
   * - 3
     - 0.628
     - 1.336
     - SVD
   * - 4
     - 0.630
     - 1.421
     - SVD

For four independently seeded series, n=48, d=2, M=11,
fixed :math:`\mu=0` and the same log-penalty grid:

.. list-table:: Cost of reusing the same candidate grid
   :header-rows: 1
   :widths: 36 21 21 22

   * - Method
     - Cold (ms)
     - Warm (ms)
     - Cold/warm
   * - Spectral SVD
     - 2.451
     - 0.888
     - 2.76
   * - Banded Cholesky
     - 5.167
     - 1.830
     - 2.82
   * - General banded
     - 6.275
     - 3.234
     - 1.94
   * - Dense Cholesky
     - 3.436
     - 1.507
     - 2.28

Warm processing caches work across *independent series that revisit the
same candidate penalties*. It does not imply that one Cholesky
factorization can be reused at a different penalty. The higher order
of differencing can widen the band and affect conditioning.

Coordinate grids and the nonzero reference mean
------------------------------------------------

The companion experiment also measures fixed :math:`\mu=0.15`,
orders 1--4 (up to 5 in the full preset), candidate counts M=5/11
(up to 21), independent series counts R=1/4 (up to 10), and
**log-lambda versus mapped uniform normalized-S grids**.

These coordinate grids share the same finite penalty endpoints and
candidate count, but not necessarily the same interior candidates or
finite-grid optimum. Smoothness inversion cost is measured separately
and **excluded from the method-specific durations**; include that
cost when comparing full workflows. Exact S=0 and S=1 are supported by
other library functionality, but omitted from the finite-factorization
timing range.

For a fixed numeric :math:`\mu`, the normal-equation right hand side
changes but the smoothing matrix and its EDF do not. Selection
criteria can nevertheless select different penalties when :math:`\mu`
changes.

Limitations and reproducibility
--------------------------------

All numbers above are descriptive results from one hosted runner and
one seeded design with repeated timing blocks. They are not
multi-machine evidence of the universally fastest method, and
classical GCV is not an out-of-sample forecasting criterion.

The actual source records and hardware metadata are archived in
``paper/benchmarks/grid_reuse_reference/``. Study output from the
user's Windows 11 VM has **not** been uploaded to GitHub and is
not represented as this Linux-runner evidence.

The executed figures, including variation by difference order and
reference mean, are in
:doc:`notebooks/13-grid-search-repeated-solvers-orders`.
The six-solver full-fit benchmark is in
:doc:`notebooks/12-six-solvers-cholesky-nonzero-mu`.

To reproduce the full experiment in Windows PowerShell:

.. code-block:: powershell

   conda activate trendestimation
   python paper/benchmarks/grid_reuse_study.py --preset full --repeats 7

Local CSV files are written to ``paper/benchmarks/results/grid_reuse/``.
See also :doc:`benchmarks` and :doc:`solver_backends`.
