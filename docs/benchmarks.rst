Computation and benchmarking
============================

The ``trendestimation`` package uses the singular-value decomposition of
the finite-difference matrix. Spectral reuse is valuable when evaluating many
candidate penalty parameters, but a dense SVD is not always the fastest
method for a single full-trend fit.

Computational cost model
------------------------

Let ``n`` be series length, ``d`` finite-difference order, and ``M``
the number of candidate smoothing penalties.

.. list-table::
   :header-rows: 1
   :widths: 52 28

   * - Operation
     - Approximate complexity
   * - Full spectral factorization
     - :math:`\mathcal{O}(n^3)`
   * - Store one dense spectral basis
     - :math:`\mathcal{O}(n^2)` memory
   * - Conditional EDF or spectral smoothness
     - :math:`\mathcal{O}(n)` per penalty
   * - GCV, AICc, BIC after one projection
     - :math:`\mathcal{O}(n)` per penalty
   * - Reconstruct a full fitted trend
     - :math:`\mathcal{O}(n^2)` per penalty
   * - Full diagonal leverage CV after one projection
     - :math:`\mathcal{O}(n^2)` per penalty

The :math:`\mathcal{O}(n)` criterion evaluations assume the eigensystem and projections have
already been computed. Dense spectral setup is explicitly included in the
benchmark timing, and actual complexity can depend on library and hardware.

The benchmark notebook
----------------------

See :doc:`notebooks/07-computational-benchmarks` for an executable
comparison against an independently implemented **banded** solver.
The banded penalty is assembled directly, without first materializing a
dense matrix.

The notebook records setup and repeated-fit timing separately, numerical
parity, theoretical dense eigenvector memory, CPU and software metadata.
Small examples run automatically in documentation builds; longer experiments
should be repeated manually on a designated reference computer.

Energy and electricity cost
---------------------------

Total system energy requires direct power measurement or an explicit
assumption. For assumed average active power `P` (watts), elapsed wall
time `t` (seconds), and electricity tariff `c` (MXN/kWh),

.. math::

   E_{\mathrm{kWh}} = \frac{P t}{3{,}600{,}000},
   \qquad
   C_{\mathrm{MXN}} = c E_{\mathrm{kWh}}.

The runner accepts ``--watts`` and ``--mxn-per-kwh`` together.
The reported amount is an *assumption-based estimate* rather than a
measured energy or cloud-compute charge. No unmeasured cost is imputed.

Reproduce (on your own computer)
--------------------------------

.. code-block:: console

   python scripts/run_notebooks.py --fast --fail-fast
   python scripts/run_notebooks.py --watts 80 --mxn-per-kwh 2.0

The numeric values 80 and 2.0 above are **illustrative inputs**, not
estimates of the reader's actual power consumption or tariff.
