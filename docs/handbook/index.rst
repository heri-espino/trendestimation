Mathematical handbook
=====================

A compact, section-by-section reference for the mathematical results
**implemented in** ``trendestimation``. Each page states the formulas,
their assumptions, boundary behavior, and the corresponding software entry
points. This handbook is designed for lookup; for worked examples see
:doc:`../smoothness_optimization`, and for theoretical background see
:doc:`../mathematics`.

**Scope:** finite-difference penalized least squares (PLS), fixed-reference
classical leave-one-out CV, GCV, AICc, BIC, Gaussian marginal likelihood,
and numerical parameter selection. **Not** forecast-horizon CV, rolling
forecast evaluation, or joint likelihood estimation of the reference mean.

.. toctree::
   :maxdepth: 2
   :caption: Mathematical results

   pls
   smoothness
   criteria
   derivatives
   likelihood
   numerical_methods

Quick formula index
-------------------

.. list-table::
   :header-rows: 1
   :widths: 27 45 28

   * - Mathematical object
     - Defining identity
     - Section
   * - PLS smoother
     - :math:`H_\lambda=(I+\lambda D_d^\top D_d)^{-1}`
     - :doc:`pls`
   * - Effective degrees of freedom
     - :math:`\nu(\lambda)=\operatorname{tr}H_\lambda`
     - :doc:`smoothness`
   * - Guerrero's smoothness
     - :math:`S_G(\lambda)=1-\nu(\lambda)/n`
     - :doc:`smoothness`
   * - Normalized smoothness
     - :math:`S(\lambda)=(n-\nu(\lambda))/(n-d)`
     - :doc:`smoothness`
   * - Classical leave-one-out CV
     - :math:`\mathrm{CV}=n^{-1}\sum_i[r_i/(1-h_{ii})]^2`
     - :doc:`criteria`
   * - GCV
     - :math:`\mathrm{GCV}=(\mathrm{RSS}/n)/(1-\nu/n)^2`
     - :doc:`criteria`
   * - AICc / BIC
     - Log-residual error plus an EDF-based penalty
     - :doc:`criteria`
   * - CV derivatives
     - Exact quotient rule, not finite differences
     - :doc:`derivatives`
   * - Marginal Gaussian MLE
     - Profiled likelihood and variance components
     - :doc:`likelihood`
   * - Root solving
     - :math:`S(\lambda)-s=0`, or :math:`\mathrm{CV}'(\lambda)=0`
     - :doc:`numerical_methods`

Notation and conventions
------------------------

Throughout, :math:`y\in\mathbb R^n` is an equally spaced series,
:math:`d\in\{0,\ldots,n-1\}` is the difference order, :math:`D_d`
is the forward-difference matrix, :math:`Q=D_d^\top D_d`,
:math:`\mu` is a fixed numerical target for the :math:`d`-th
differences, and :math:`\lambda\in[0,\infty]` is the penalty.

Write :math:`r=n-d` for the rank, :math:`\delta_1,\ldots,\delta_r>0`
for the positive eigenvalues of :math:`Q`, and
:math:`\nu(\lambda)` for the **conditional** effective degrees of
freedom. The special case :math:`d=0` has :math:`D_0=I` and no
polynomial nullspace. Limiting formulas at :math:`\lambda=\infty`
are understood exactly, not as overflow-prone finite approximations.

This is a concise reference to established PLS theory and the explicit
criterion conventions in this package, **not a novelty claim**. See
:doc:`../references` for Guerrero (2007, 2008),
Cortés-Toto et al. (2017), Weinert (2007), and Biessy (2026).
