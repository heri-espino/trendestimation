.. _smoothness-coordinate:

Smoothness S versus penalty lambda
==================================

**One trend estimator, two ways to choose its smoothing.**

In penalized least-squares (PLS) smoothing, the penalty
:math:`\lambda\geq0` determines how strongly we constrain the
differences of a fitted trend. Its numerical scale depends on the
difference order. The normalized smoothness index
:math:`s=S(\lambda)\in[0,1]` expresses the **same choice**
on a bounded, more interpretable scale.

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Penalty coordinate — :math:`\lambda`
      :class-card: sd-border-0

      :math:`\lambda\in[0,\infty]`

      The traditional penalty strength. It appears in the PLS
      objective and the linear system.

   .. grid-item-card:: Smoothness coordinate — :math:`s`
      :class-card: sd-border-0

      :math:`s=S(\lambda)\in[0,1]`

      The normalized loss of conditional effective degrees of
      freedom in the :math:`n-d` penalized directions.

**Both options are implemented.** Setting
``search_space="smoothness"`` changes the search coordinate,
**not the estimator or the underlying CV, GCV, AICc, BIC,
or conditional Gaussian MLE score**.

.. contents:: On this page
   :local:
   :depth: 2

Start from the same estimator
-----------------------------

For equally spaced observations :math:`y\in\mathbb{R}^n`,
difference order :math:`0\le d<n` and a fixed
reference-difference mean :math:`\mu`, estimate

.. math::
   :label: smooth-coordinate-pls

   \widehat{\tau}_{\lambda,\mu}
   =\arg\min_{\tau\in\mathbb{R}^n}
   \left\{\|y-\tau\|_2^2+
   \lambda\|D_d\tau-\mu\mathbf{1}\|_2^2\right\}.

The penalty pulls :math:`d`-th forward differences toward
:math:`\mu`; it does not automatically force a constant trend.
For :math:`d=2` and :math:`\mu=0`, the exact infinite-penalty
limit is a straight line. If :math:`d=2` and :math:`\mu\ne0`,
the limiting trend is quadratic, with the prescribed second
difference.

For fixed numerical :math:`\mu`, the smoothing matrix is

.. math::

   H_\lambda=(I+\lambda D_d^\top D_d)^{-1}.

This is an existing PLS family, **not a newly introduced
statistical objective**. We change how we represent and
search its smoothing level.

An interpretable scale
----------------------

Let :math:`r=n-d` and let :math:`\delta_1,\ldots,\delta_r>0`
be the positive eigenvalues of :math:`D_d^\top D_d`.
The normalized trace-based index is

.. math::
   :label: smooth-coordinate-index

   \boxed{
   S(\lambda)=\frac{n-\operatorname{tr}(H_\lambda)}{n-d}
   =\frac{1}{r}\sum_{j=1}^r
     \frac{\lambda\delta_j}{1+\lambda\delta_j}
   }.

Its endpoints have precise meanings:

- :math:`S(0)=0`: no penalty and the observations are fitted exactly.
- :math:`S(\infty)=1`: the constrained polynomial limiting fit.
- :math:`0<S(\lambda)<1`: an intermediate level of smoothing.

The central interpretation follows immediately. Let
:math:`\nu(\lambda)=\operatorname{tr}(H_\lambda)` denote the
**conditional effective degrees of freedom (EDF)**. Then

.. math::
   :label: smooth-coordinate-edf

   \boxed{\nu(\lambda)=n-(n-d)S(\lambda).}

For :math:`n=100`, :math:`d=2`, and :math:`s=0.8`, this
means :math:`\nu=100-98(0.8)=21.6`. Thus :math:`s` describes
the fraction of the *penalizable degrees of freedom* suppressed,
**not** an 80% forecast confidence level, 80% noise removal,
or a probability.

.. note::

   Equal :math:`s` values across difference orders correspond
   to equal **normalized conditional trace smoothness**,
   not identical fitted curvature, geometries, or forecast
   accuracy. If :math:`\mu` is estimated from the data,
   fixed-mean EDF does not automatically describe the entire
   data-adaptive procedure.

Why optimize in S?
------------------

The derivative is strictly positive at finite
:math:`\lambda\ge0`:

.. math::
   :label: smooth-coordinate-derivative

   S'(\lambda)=\frac{1}{n-d}\sum_{j=1}^{n-d}
   \frac{\delta_j}{(1+\lambda\delta_j)^2}>0.

Hence :math:`S` is continuous and strictly increasing.
Every interior target :math:`s\in(0,1)` corresponds to exactly
one penalty :math:`\Lambda(s)=S^{-1}(s)`, with
:math:`\Lambda(0)=0` and :math:`\Lambda(1)=\infty`.

For an existing criterion :math:`C(\lambda;\mu)` with
fixed :math:`\mu`, define

.. math::
   :label: smooth-coordinate-selection

   \widetilde C(s;\mu)=C(\Lambda(s);\mu),
   \qquad
   \widehat s\in\arg\min_{s\in[0,1]}\widetilde C(s;\mu),
   \qquad
   \widehat\lambda=\Lambda(\widehat s).

The *ideal* global minimizers map into one another when
both searches use equivalent admissible domains. Boundary
scores that are undefined at :math:`\lambda=0`, such as
ordinary CV and conditional Gaussian MLE, remain undefined.

The chain rule gives the derivative in :math:`s`:

.. math::
   :label: smooth-coordinate-score-derivative

   \boxed{\frac{d\widetilde C}{ds}
   =\frac{dC/d\log\lambda}{dS/d\log\lambda}},
   \qquad \lambda=\Lambda(s).

The library uses this analytical transformation for
**fixed-mean classical CV** when
``criterion="cv", search_space="smoothness"``.
Other criteria evaluate candidate grids. A bounded numerical
search is not by itself a proof of global optimality.

Use both coordinates in Python
------------------------------

The public API supports both choices without changing the
definition of the criterion.

.. code-block:: python

   import numpy as np
   from trendestimation import TrendSmoother, select_lambda

   rng = np.random.default_rng(24)
   t = np.arange(60, dtype=float)
   y = 0.04 * t + np.sin(t / 7) + rng.normal(0, 0.2, t.size)

   smoother = TrendSmoother(len(y), order=2)

   by_lambda = select_lambda(
       smoother, y, criterion="cv", mu=0.0,
       search_space="lambda",
   )
   by_s = select_lambda(
       smoother, y, criterion="cv", mu=0.0,
       search_space="smoothness",
   )

   print("Penalty search:", by_lambda.lambda_, by_lambda.smoothness)
   print("Smoothness search:", by_s.lambda_, by_s.smoothness)

   # Or prescribe a normalized smoothing level directly.
   target_s = 0.8
   penalty = smoother.lambda_for_smoothness(target_s)
   fit = smoother.fit(y, lambda_=penalty, mu=0.0)
   print("Recovered S:", fit.smoothness)

The returned ``SelectionResult`` includes
``lambda_``, ``smoothness`` and ``score``.
It also includes ``grid`` (the actual penalty values) and
``search_grid`` (the searched coordinate); both align with
``scores``. When passing an explicit ``grid``, its entries
are penalties in lambda mode and normalized smoothness
targets in S mode.

A useful equivalence check maps *the same candidate
penalties* to their smoothness indices:

.. code-block:: python

   penalties = np.array([0.1, 1.0, 10.0, np.inf])
   s_candidates = np.array([
       smoother.smoothness(lam) for lam in penalties
   ])
   original = select_lambda(
       smoother, y, criterion="gcv", mu=0.0,
       search_space="lambda", grid=penalties,
   )
   transformed = select_lambda(
       smoother, y, criterion="gcv", mu=0.0,
       search_space="smoothness", grid=s_candidates,
   )
   np.testing.assert_allclose(
       original.scores, transformed.scores,
       rtol=1e-9, atol=1e-9,
   )

The scores are the same mathematical criterion.
Default lambda and S searches need not return exactly the
same candidate because they explore different finite grids
and numerical refinements.

Numerical limits and further reading
------------------------------------

- **Inversion is not free.** An interior target :math:`s`
  requires solving for :math:`\log\lambda` using the
  spectral representation before evaluating the score.
- **Endpoint conditioning matters.** Near :math:`s=0`
  and :math:`s=1`, :math:`dS/d\log\lambda` approaches
  zero. Extremely close interior targets may exceed
  float64 penalty limits.
- **Reference means have distinct semantics.** Classical
  CV/GCV/AICc/BIC require a fixed numeric :math:`\mu`.
  Only the conditional MLE selector permits
  ``mu="data"``; that does not jointly optimize
  :math:`(\lambda,\mu)`.
- **This is in-sample smoothing.** Classical LOOCV is
  not rolling-origin or horizon-specific forecast validation.
  No speed advantage for S optimization is claimed without
  direct end-to-end timing comparisons.

For the full CV derivation, additional root solvers and
numerical safeguards, see :doc:`smoothness_optimization`.
For the PLS model and reference differences, see
:doc:`mathematics`. For API signatures, consult
:doc:`api/selection` and :doc:`api/core`.
