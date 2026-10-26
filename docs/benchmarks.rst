Computation and benchmarking
============================

For four AwesomeFigures charts, including CV/GCV/AICc/BIC and
conditional Gaussian MLE selection in S/lambda coordinates,
see :doc:`mle_coordinate_figures`.

A reproducible three-way comparison of SVD, dense eigen-decomposition
and direct banded Cholesky is described in :doc:`solver_backends`.

The ``TrendSmoother`` and ``select_lambda`` interfaces use the
singular-value decomposition of the finite-difference matrix to supply
EDF, smoothness and criterion selection. Trend-only ``fit_penalized``
and ``PreparedPLSSolver`` now default to genuine *banded Cholesky*.
Spectral reuse is valuable when evaluating many candidate penalty
parameters, but a dense SVD is not always the fastest method for
full trend reconstruction.

For a measured six-backend comparison including *actual GCV grid search*,
fixed mu=0 or 0.15, multiple difference orders, and repeated-series
reuse, see :doc:`grid_reuse_selection`. The associated executed notebook
is :doc:`notebooks/13-grid-search-repeated-solvers-orders`.
These times include method-specific EDF work, which must not be omitted
when comparing criterion selection pipelines.

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


How spectral reuse removes repeated work
----------------------------------------

For a series :math:`y\in\mathbb R^n`, difference order :math:`d`,
fixed numeric reference mean :math:`\mu`, and
:math:`Q=D_d^\top D_d`, choose :math:`p_\mu` satisfying
:math:`D_dp_\mu=\mu\mathbf1`. With :math:`z=y-p_\mu`,
the penalized least-squares solution is

.. math::

   \widehat\tau_\lambda
   =p_\mu+(I+\lambda Q)^{-1}z.

A straightforward dense implementation solves a new
:math:`n\times n` linear system for **every** penalty. This requires
approximately :math:`\mathcal{O}(n^3)` operations per candidate,
assuming general dense factorization. Forming the inverse explicitly
is unnecessary and usually less numerically appropriate than solving
the system; the naive benchmarks below use ``numpy.linalg.solve``.

The package instead computes a **full SVD** of :math:`D_d` once.
Its right singular vectors diagonalize :math:`Q`:

.. math::

   Q=U\operatorname{diag}(\delta_1,\ldots,\delta_n)U^\top,
   \qquad
   \widehat\tau_\lambda
    =p_\mu+U\left[
      \frac{U^\top z}{1+\lambda\delta}
      \right].

The last :math:`d` penalty eigenvalues vanish. The expensive basis
:math:`U` is **independent of** :math:`\lambda`, so changing the
smoothing parameter changes only :math:`n` scalar attenuation weights.
The package stores :math:`U`, the eigenvalues, and
:math:`U\odot U` for diagonal-leverage computations.

There are four distinct computational savings:

1. **Full fitted trend:** Multiply by the cached basis to reconstruct
   :math:`\widehat\tau_\lambda` in
   :math:`\mathcal{O}(n^2)`, instead of solving another
   :math:`\mathcal{O}(n^3)` dense system. A direct
   ``smoother.fit`` call also projects the data, costing
   :math:`\mathcal{O}(n^2)` per call.
2. **Smoothness and EDF:** Only the eigenvalues matter:

   .. math::

      \operatorname{edf}(\lambda)
        =\sum_{j=1}^n\frac{1}{1+\lambda\delta_j},
      \qquad
      S(\lambda)=\frac1{n-d}\sum_{j=1}^{n-d}
        \frac{\lambda\delta_j}{1+\lambda\delta_j}.

   Thus each evaluation is :math:`\mathcal{O}(n)`. The smoothness
   inversion solver evaluates short spectral sums in
   :math:`x=\log\lambda`, using numerically stable smaller-tail
   calculations; :math:`k` evaluations cost
   :math:`\mathcal{O}(kn)` after the decomposition.
3. **GCV/AICc/BIC/MLE:** Project :math:`c=U^\top z` once and
   use Parseval's identity to compute

   .. math::

      \operatorname{RSS}(\lambda)
        =\sum_{j=1}^n
           \left(\frac{\lambda\delta_j}
           {1+\lambda\delta_j}\right)^2c_j^2.

   The cached candidate loop in ``select_lambda`` evaluates
   residual- and EDF-based criteria in
   :math:`\mathcal{O}(n)` per penalty. The Gaussian marginal MLE
   also uses spectral sums. A standalone ``score_lambda``
   call recomputes the data projection, so its total cost
   is :math:`\mathcal{O}(n^2)`.
4. **Exact classical LOOCV:** Literally leaving out and refitting each
   of :math:`n` observations would require :math:`n` dense solves
   for every candidate penalty:
   :math:`\mathcal{O}(n^4)` per penalty. Instead, for the positive
   eigenpairs :math:`U_+,\delta_+` and
   :math:`w_j=\lambda\delta_j/(1+\lambda\delta_j)`,

   .. math::

      e_i^{(-i)}
      =\frac{[U_+(w\odot c_+)]_i}
             {[(U_+\odot U_+)w]_i},
      \qquad
      \operatorname{CV}(\lambda)=
         \frac1n\sum_i(e_i^{(-i)})^2.

   The numerator and denominator each require a matrix-vector
   product: :math:`\mathcal{O}(n(n-d))`, at most
   :math:`\mathcal{O}(n^2)`. The analytical CV derivative
   reuses similar products without forming dense inverses or
   finite-difference gradients.

This exact LOO identity assumes a **fixed numeric** :math:`\mu`,
unchanged difference operator and time grid, and positive penalty.
Omitting observation :math:`i` removes its **data-fitting weight**;
it does not remove time index :math:`i` and change the penalty matrix.
The interpolating limit :math:`\lambda=0` has undefined LOO refits.
This is **not rolling-origin, future-horizon forecast validation**.

Naive dense versus spectral: full complexity comparison
-------------------------------------------------------

The table assumes low fixed :math:`d`, :math:`n-d=\Theta(n)`,
:math:`K` candidate penalties and **dense** computations. Spectral
setup is **not free**: the full SVD costs
:math:`\mathcal{O}(n^3)` time and
:math:`\mathcal{O}(n^2)` storage.

.. list-table::
   :header-rows: 1
   :widths: 34 33 33

   * - Task
     - Naive dense method
     - Cached spectrum
   * - Fit one trend
     - :math:`\mathcal{O}(n^3)`
     - :math:`\mathcal{O}(n^2)` after SVD
   * - Fit :math:`K` trends
     - :math:`\mathcal{O}(Kn^3)`
     - :math:`\mathcal{O}(n^3+Kn^2)` including setup
   * - EDF / normalized smoothness
     - :math:`\mathcal{O}(n^3)` if forming dense hat
     - :math:`\mathcal{O}(n)`
   * - :math:`K` GCV / AICc / BIC / MLE evaluations
     - :math:`\mathcal{O}(Kn^3)` with dense hats
     - :math:`\mathcal{O}(n^3+Kn)` plus projection
   * - :math:`K` exact classical CV scores
     - :math:`\mathcal{O}(Kn^4)` with :math:`n` refits
     - :math:`\mathcal{O}(n^3+Kn^2)` including setup
   * - Smoothness inversion, :math:`k` scalar evaluations
     - :math:`\mathcal{O}(kn^3)` if forming dense hats
     - :math:`\mathcal{O}(n^3+kn)` including setup

The speed benefit becomes more useful as the same
``TrendSmoother(n, order=d)`` is reused. For a single fit or short
series, its initial full SVD can outweigh any subsequent savings.
The automatic derivative-based CV selector examines 97 initial
log-spaced candidates plus refinements; it does **not** necessarily
run faster than the default 121-point legacy grid on every input.

Benchmark: actual naive refits against the public API
-----------------------------------------------------

The source below is a seeded, **manually run** timing benchmark.
For each :math:`n=20,32,48` it compares identical positive penalty
grids, fixed ``mu=0.0``, and second differences:

* **Naive exact CV:** Solve a new weighted
  :math:`(W_i+\lambda Q)\tau=W_iy` system for each omitted
  observation and each penalty, preserving the original time grid.
* **Naive GCV:** Compute the full dense hat matrix from
  :math:`(I+\lambda Q)H=I` at each penalty and measure RSS and trace.
* **Optimized counterparts:** ``select_lambda`` with a
  fixed explicit ``grid=`` and ``method="grid"``, so the
  *criterion and candidates are identical*.

It **asserts numerical agreement** of the scored candidates before
timing them. Each result reports separately: the initial SVD time,
median time for all grid candidates, the naive-to-spectral ratio,
and the largest absolute difference in criterion scores. Timings
are machine-dependent; no universal speedup factor is claimed.

.. code-block:: console

   python -m pip install -e '.[docs,plot]'
   python docs/examples/naive_vs_spectral.py
   python docs/examples/naive_vs_spectral.py --repeats 5 --csv build/naive-vs-spectral.csv

.. literalinclude:: examples/naive_vs_spectral.py
   :language: python
   :caption: Executable comparison of dense naive refits and spectral selection
   :linenos:

.. note::

   The script runs only when requested; neither a Sphinx build
   nor automatic CI executes the expensive
   :math:`\mathcal{O}(n^4)` reference loop. Add the reported SVD
   setup to spectral grid time for a *one-off* end-to-end comparison.
   Hardware, threading, array size and warm-up can reverse speed
   rankings on very small examples.

Why a banded comparison is also essential
-----------------------------------------

The normal-equation matrix :math:`Q=D_d^\top D_d` is **banded**,
with half-bandwidth :math:`d`. A well-implemented banded
Cholesky solve can achieve approximately
:math:`\mathcal{O}(nd^2)` time and
:math:`\mathcal{O}(nd)` storage per penalty. For small fixed
:math:`d` and one fit, it may outperform the dense SVD by a
large margin. The full hat-matrix *diagonal* required for exact
LOOCV is a separate computational problem.

The existing :doc:`notebooks/07-computational-benchmarks` notebook
provides an independent **banded** comparison. The public
``TrendSmoother`` implementation currently uses **dense SVD**,
not banded Cholesky; comparing only to intentionally naive dense
refits must not be interpreted as superiority over all methods.

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
