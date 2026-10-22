Numerical methods for penalty selection
=======================================

Two different numerical problems
--------------------------------

**Problem A — invert a prescribed smoothness:** Given
:math:`s\in(0,1)`, find the unique root

.. math::

   F(\lambda)=S(\lambda)-s=0.

This is a **monotone scalar root** problem. A bracketed
solver converges reliably when the signs at its endpoints differ.

**Problem B — select smoothness by a statistical criterion:**
Given :math:`C`, solve

.. math::

   \lambda^*=\underset{\lambda\ge0}{\operatorname{argmin}}
       \,C(\lambda),\qquad S^*=S(\lambda^*).

An interior stationary candidate satisfies
:math:`C'(\lambda)=0`. Unlike problem A,
:math:`C'` need not be monotone. Several stationary
points may exist; one local root finder alone does not
guarantee the global minimum.

Grid and derivative-guided CV
-----------------------------

The existing ``method="grid"`` scores **121 geometric**
finite penalties scaled to the positive spectrum, plus the
exact :math:`\lambda=\infty` candidate. It chooses the
lowest *evaluated* criterion value.

The new ``criterion="cv", method="auto"`` evaluates
**97 initial log-spaced penalties** over a broad spectrally
scaled domain, refines sampled sign changes of the analytical
CV derivative, examines sampled score valleys, checks
boundary candidates, and selects the smallest resulting CV
score. This is **not globally certified**: sufficiently narrow
features can be missed by any finite exploratory scan.

For GCV, AICc, BIC and marginal MLE, ``method="auto"``
retains grid selection. Passing ``grid=`` explicitly
under ``method="auto"`` retains grid-only semantics.

.. code-block:: python

   derivative_choice = select_lambda(
       smoother, y, criterion="cv", mu=0.0, method="auto"
   )
   grid_choice = select_lambda(
       smoother, y, criterion="cv", mu=0.0, method="grid"
   )

Root-finding methods for smoothness inversion
---------------------------------------------

For a general positive spectrum, invert smoothness in
:math:`x=\log\lambda`, using

.. math::

   S(e^x)=\frac1r\sum_{j=1}^r
      \frac{1}{1+\exp[-(x+\log\delta_j)]}.

For :math:`u_j(x)=[1+\exp[-(x+\log\delta_j)]]^{-1}`,

.. math::

   \frac{dS(e^x)}{dx}
      =\frac1r\sum_{j=1}^r u_j(x)(1-u_j(x))>0.

A stable implementation evaluates the logistic quantities
using log-space expressions, tracks the smaller smoothness
tail :math:`\min(S,1-S)`, and checks reconstruction error.

.. list-table::
   :header-rows: 1
   :widths: 24 37 39

   * - Method
     - Main idea
     - Limitation
   * - Brent (``brentq``)
     - Interpolation with sign-preserving bracketing
     - Requires a valid bracket
   * - Newton (``newton``)
     - :math:`x_{k+1}=x_k-F(x_k)/F'(x_k)`
     - Needs a derivative and safeguarded steps
   * - Secant (``secant``)
     - Approximate slope from successive values
     - Can stagnate without safeguards
   * - Bisection (``bisect``)
     - Repeatedly halve a sign-changing bracket
     - Often requires more iterations
   * - Automatic (``auto``)
     - Brent for general spectra; exact scalar inverse when valid
     - Robustness, not universal speed, is prioritized

Here :math:`F(x)=S(e^x)-s`. Newton and secant are
**safeguarded** by the spectral bracket in the library.
The original Guerrero target uses the same method after
accounting for its range :math:`[0,(n-d)/n]`.

.. code-block:: python

   lam_b = smoother.lambda_for_smoothness(
       0.8, method="brentq"
   )
   lam_n = smoother.lambda_for_smoothness(
       0.8, method="newton", tol=1e-12
   )
   lam_s = smoother.lambda_for_smoothness(
       0.8, method="secant"
   )
   lam_i = smoother.lambda_for_smoothness(
       0.8, method="bisect"
   )

Exact endpoints are :math:`S=0\leftrightarrow\lambda=0`
and :math:`S=1\leftrightarrow\lambda=\infty`.
No numerical root search is needed there.

When all positive eigenvalues are identical to
:math:`\delta`, the analytical inverse is

.. math::

   \lambda(s)=\frac{s}{\delta(1-s)}.

Complexity and parameterization
-------------------------------

After an :math:`O(n^3)` full SVD, evaluations of
smoothness, EDF, their spectral derivatives, and
RSS-based criteria take :math:`O(n)` per penalty.
The exact classical CV score also uses the eigenvectors,
generally costing :math:`O(n^2)` per penalty.

A uniform grid in :math:`S\in[0,1]` is interpretable
but requires mapping its points back to penalties.
A grid in :math:`\log\lambda` instead explores many
orders of magnitude directly. Neither finite grid
guarantees the global optimum.

The reparameterization identity

.. math::

   \frac{dC}{dS}=\frac{C'(\lambda)}{S'(\lambda)}

preserves interior stationary candidates because
:math:`S'(\lambda)>0`; it does **not** remove
the underlying penalty dependence of the smoother.

For worked numerical examples and visualizations, see
:doc:`../smoothness_optimization`.
