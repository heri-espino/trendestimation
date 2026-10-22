Selection criteria: CV, GCV, AICc, and BIC
============================================

Shared notation and domain
--------------------------

Fix the reference mean :math:`\mu` numerically and write
:math:`p=p_\mu`, :math:`z=y-p`, :math:`H=H_\lambda`,
:math:`\widehat\tau=p+Hz`. Define

.. math::

   e=y-\widehat\tau=(I-H)z,\quad
   R=\mathrm{RSS}=\|e\|_2^2,\quad
   h_i=H_{ii},\quad
   \nu=\operatorname{tr}(H).

All implemented scores are **minimized**. These are classical
**in-sample** selection criteria, not rolling-origin forecast-horizon
cross-validation. Unless otherwise specified, :math:`\lambda\ge0`
and :math:`\mu` is held fixed across candidate penalties.

Ordinary leave-one-out CV
-------------------------

Remove observation :math:`i` from the *data-fidelity term*
while keeping the original grid, difference penalty and fixed
:math:`\mu`. If :math:`h_i<1`, the leave-one-out residual is

.. math::

   e_i^{(-i)}=y_i-\widehat\tau_i^{(-i)}
      =\frac{e_i}{1-h_i}.

Thus **one fitted smoother**, together with the hat-matrix
diagonal, provides the exact LOOCV score without :math:`n`
separate refits:

.. math::

   \boxed{\mathrm{CV}(\lambda)
       =\frac1n\sum_{i=1}^n
          \left(\frac{e_i}{1-h_i}\right)^2}.

The reported score is **MSE**, not RMSE. Nevertheless
:math:`\sqrt{\mathrm{CV}}` has the same minimizer.
At :math:`\lambda=0`, :math:`H=I` and the displayed
LOOCV formula is undefined (zero denominators); this is
not an ordinary zero-error CV result. For :math:`\lambda>0`,
stable small-penalty evaluation can cancel common factors.

Generalized cross-validation
----------------------------

GCV replaces observation-specific leverages by their average
:math:`\nu/n`:

.. math::

   \boxed{\mathrm{GCV}(\lambda)
        =\frac{R/n}{(1-\nu/n)^2}
        =\frac{nR}{(n-\nu)^2}}.

It is inexpensive after spectral preprocessing because it
requires only :math:`R` and :math:`\nu`.
It is undefined if :math:`n-\nu=0`; it is not the same
as exact LOOCV when individual leverages differ.

Corrected Akaike information criterion
--------------------------------------

The library's precise **AICc score convention** is

.. math::

   \boxed{\mathrm{AICc}(\lambda)
      =\log(R/n)+\frac{2\nu+1}{n-\nu-2}}.

It combines a log residual-error term and a finite-sample
complexity correction. Here it is defined only when
:math:`R>0` and :math:`n-\nu-2>0`.
Other AICc conventions exist; this page documents the
**implemented** one (as used for the Cortés-Toto comparison).

Bayesian information criterion
------------------------------

The library's **BIC score convention** is

.. math::

   \boxed{\mathrm{BIC}(\lambda)
      =\log(R/n)+\frac{\nu\log n}{n}}.

The penalty is linear in effective degrees of freedom, with
coefficient :math:`\log(n)/n`. This score is undefined
for :math:`R=0`. The near-interpolating boundary can
give extreme log-residual behavior; an interior optimum
is not guaranteed.

Criterion summary
-----------------

.. list-table::
   :header-rows: 1
   :widths: 16 36 48

   * - Criterion
     - Main idea
     - Principal limitation
   * - CV
     - Exact omitted-observation residuals
     - Requires a fixed hat matrix under deletion;
       no chronological holdout
   * - GCV
     - Residual error divided by squared average leverage correction
     - Replaces heterogeneous leverages by their mean
   * - AICc
     - Log RSS plus small-sample EDF correction
     - Undefined for insufficient residual degrees of freedom
   * - BIC
     - Log RSS plus sample-size-dependent EDF penalty
     - Can favor near-interpolation under this score convention
   * - MLE
     - Gaussian marginal profile likelihood
     - Requires a stochastic variance-component model;
       see :doc:`likelihood`

The closed-form *criterion scores* do not imply a closed-form
optimum :math:`\arg\min_\lambda C(\lambda)`. Consult
:doc:`derivatives` and :doc:`numerical_methods`.

Use ``score_lambda(smoother, y, lambda_=..., criterion=..., mu=...)``
to evaluate a chosen criterion and ``select_lambda(...)`` to
select a penalty. Classical CV/GCV/AICc/BIC require **numeric**
:math:`\mu`; their fixed-mean formulas do not cover
foldwise estimation of ``mu="data"``.
