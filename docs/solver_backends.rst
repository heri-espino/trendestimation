SVD, eigendecomposition, and banded Cholesky backends
=====================================================

Three methods, one trend
------------------------

The package offers three full-trend reconstruction backends:

* ``svd``: full singular-value decomposition of the difference matrix.
* ``eigh``: symmetric eigendecomposition of the dense normal-product matrix.
* ``cholesky``: directly assembled banded penalty and banded Cholesky
  factorization at each positive finite penalty.

All methods solve the same penalized least-squares objective:

.. math::

   \widehat{\tau}_{\lambda,\mu}
    =\arg\min_\tau\{\|y-\tau\|^2+
       \lambda\|D_d\tau-\mu\mathbf1\|^2\}.

Given :math:`D_d=U\Sigma V^\top`, the spectral identity is

.. math::

   Q=D_d^\top D_d=V\Sigma^\top\Sigma V^\top.

SVD and ``eigh`` yield the same solution in exact arithmetic.
Numerically, forming :math:`Q` squares the nonzero-subspace condition
number and can make very small eigenvalues difficult to recover.
The banded system :math:`I+\lambda Q` is positive definite for
finite :math:`\lambda\ge0`; direct banded Cholesky uses
:math:`O(nd)` persistent penalty storage.

Backend selection
-----------------

.. code-block:: python

   import numpy as np
   from trendestimation import PreparedPLSSolver, fit_penalized

   t = np.arange(80)
   y = np.sin(t / 8) + 0.02 * t

   a = fit_penalized(y, order=2, lambda_=30., method="svd")
   b = fit_penalized(y, order=2, lambda_=30., method="eigh")
   c = fit_penalized(y, order=2, lambda_=30., method="cholesky")
   assert np.allclose(a, b, atol=1e-7)
   assert np.allclose(a, c, atol=1e-7)

   prepared = PreparedPLSSolver(len(y), order=2, method="cholesky")
   multiple_trends = prepared.fit_many(y, [1., 10., 100.])

The convenience function returns a 1-D array. The reusable class
also returns a 1-D trend from ``.fit`` and an array of trends
from ``.fit_many``. All methods support numeric fixed ``mu`` and
``mu="data"``, :math:`\lambda=0` and
:math:`\lambda=\infty`. The spectral backends reuse the observation
projection within ``.fit_many``; Cholesky refactorizes for
each positive penalty.

**API distinction:** the original ``TrendSmoother`` and
``fit_trend`` interfaces continue to provide a structured
``FitResult``, smoothness, EDF and criterion selection based on
SVD. The alternative backend interface computes **only the fitted
trend**, without silently performing expensive spectral work.
Cholesky does not automatically yield exact LOOCV leverages or EDF.
The **fit-only default method is now** ``cholesky`` (banded Cholesky),
informed by comparative full-trend runtime measurements. This is not
a universal speed guarantee. The spectral SVD remains the default for
``TrendSmoother``, ``fit_trend``, and ``select_lambda``: exact EDF,
normalized smoothness and CV/GCV/AICc/BIC/MLE scoring require additional
diagnostics that a single banded Cholesky fit does not supply.

For an automatic fit-only backend and an explicit equivalent spectral
fit, respectively:

.. code-block:: python

   fit_auto = fit_penalized(y, lambda_=30., order=2, mu=0.15)
   fit_svd = fit_penalized(y, lambda_=30., order=2, mu=0.15,
                           method="svd")
   assert np.allclose(fit_auto, fit_svd, atol=2e-7)

These two interfaces return only the trend, not a ``FitResult``.

Matched experimental comparison
-------------------------------

For :math:`M` fitted curves of length :math:`n`, with
fixed small difference order :math:`d`:

.. list-table::
   :header-rows: 1
   :widths: 26 33 41

   * - Backend
     - Setup
     - :math:`M` full trends
   * - SVD of :math:`D_d`
     - :math:`O(n^3)` and :math:`O(n^2)` storage
     - :math:`O(Mn^2)` with cached projection
   * - Dense ``eigh(Q)``
     - :math:`O(n^3)` and :math:`O(n^2)` storage
     - :math:`O(Mn^2)` with cached projection
   * - Banded Cholesky
     - :math:`O(nd^2)` assembly and :math:`O(nd)` storage
     - :math:`O(Mnd^2)` factorization plus solves

Run the independent manual benchmark:

.. code-block:: console

   python benchmarks/compare_solver_backends.py --preset smoke --repeats 3
   python benchmarks/compare_solver_backends.py --preset quick --repeats 5 --threads 1 --output build/solver-backends.json
   python benchmarks/compare_solver_backends.py --preset full --repeats 7 --threads 1 --output build/solver-backends-full.json

It compares identical data and candidate penalties for all methods
and verifies agreement before collecting time measurements.
It separates setup, one fit, repeated fits, batched fits, and
end-to-end setup plus batched fits. It reports medians, stored-array
bytes, library and BLAS metadata. Figures or claimed speedups must
come from these verified machine-specific outputs, not assumptions.

The separate six-method benchmarks include true GCV searches over
candidate grids at both fixed mu=0 and mu=0.15, with different orders
and repeated series. The :doc:`grid_reuse_selection` page reports
measured host timings and explains why SVD can win for GCV even when
banded Cholesky wins for multiple full trend fits.
No solver is universally fastest for every workload.

For a formal repeated-block experiment with paired hypothesis tests,
Holm correction and paper/Marp output, see
:doc:`benchmark_statistical_protocol`.

See :doc:`benchmarks` for the existing banded comparison, and
:doc:`handbook/pls` for the PLS mathematical theory.
