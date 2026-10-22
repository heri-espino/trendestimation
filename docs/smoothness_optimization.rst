.. _smoothness-optimization:

Smoothing-parameter optimization
================================

This guide explains finite-difference penalized least squares,
normalized smoothness, ordinary cross-validation, numerical
optimization and inversion. Examples use deterministic synthetic
data, not live downloads. Methods under development by other agents
are identified as **theory**, not publicly implemented APIs.

.. contents:: Contents
   :local:
   :depth: 2

Model and notation
------------------

Let :math:`y\in\mathbb R^n` be observations at equally spaced times;
:math:`D_d\in\mathbb R^{(n-d)\times n}` is the forward difference
operator of order :math:`0\le d<n`, :math:`\mu` is a reference
mean for order-:math:`d` differences, and :math:`\lambda\ge0`
is the penalization strength. The fitted trend minimizes

.. math::
   :label: pls-objective

   \widehat\tau_\lambda
   =\arg\min_{\tau\in\mathbb R^n}
      \left\{\|y-\tau\|_2^2+
      \lambda\|D_d\tau-\mu\mathbf 1\|_2^2\right\}.

For example, :math:`(D_2\tau)_t=\tau_{t+2}-2\tau_{t+1}+\tau_t`.
At :math:`\lambda=0` the trend equals the observations. Increasing
:math:`\lambda` penalizes deviations of differences from
:math:`\mu`. At the exact :math:`\lambda=\infty` limit, the
trend is the least-squares projection onto the affine constraint
:math:`D_d\tau=\mu\mathbf1`. For :math:`d\ge1`, this is a
degree-at-most-:math:`d` polynomial, with the leading difference
controlled by :math:`\mu` (degree at most :math:`d-1` if
:math:`\mu=0`).

For **fixed numeric** :math:`\mu`, choose a vector :math:`p`
satisfying :math:`D_dp=\mu\mathbf1`, and let
:math:`Q=D_d^\top D_d`. Differentiating the objective gives

.. math::

   \widehat\tau_\lambda=p+H_\lambda(y-p),
   \qquad H_\lambda=(I+\lambda Q)^{-1}.

The symmetric matrix :math:`H_\lambda` is the **hat matrix** or
**linear smoothing matrix**. Its trace is the conditional
**effective degrees of freedom (EDF)**. For :math:`d\ge1`,
the matrix :math:`D_d` has rank :math:`n-d` and nullity
:math:`d`, so :math:`Q` has exactly :math:`d` zero eigenvalues
and :math:`n-d` positive ones. No spectral shrinkage is applied
in the polynomial nullspace.

.. important::

   The package interprets `mu="data"` as
   :math:`\mu=\operatorname{mean}(D_dy)`, not generally
   :math:`\operatorname{mean}(y)`. Ordinary CV, GCV, AICc and
   BIC in the public selector require **fixed numeric** `mu`.
   With estimated `mu`, the usual hat-matrix formula is not
   exact leave-one-out re-estimation. The displayed EDF also
   conditions on `mu`.

Normalized smoothness and Guerrero's index
------------------------------------------

Let :math:`r=n-d` and :math:`\delta_1,\ldots,\delta_r>0`
be the positive eigenvalues of :math:`Q`. The normalized
smoothness index is

.. math::
   :label: s-function

   S(\lambda)
   =\frac{n-\operatorname{tr}(H_\lambda)}{n-d}
   =\frac1r\sum_{j=1}^r
    \frac{\lambda\delta_j}{1+\lambda\delta_j}.

Its exact derivative is

.. math::
   :label: s-derivative

   S'(\lambda)=\frac1r\sum_{j=1}^r
        \frac{\delta_j}{(1+\lambda\delta_j)^2}>0.

Every term is positive at finite :math:`\lambda\ge0`.
Consequently, :math:`S` is continuous and strictly increasing,
with :math:`S(0)=0` and :math:`S(\infty)=1`.
The ranges differ: :math:`S\in[0,1]` is an interpretable
**coordinate**, whereas :math:`\lambda\in[0,\infty]` is the
actual penalty. A target of :math:`S=0.8` is **not**
80% forecast confidence or interval coverage.

Guerrero's (2007) original index instead divides by :math:`n`:

.. math::

   S_G(\lambda)=1-\frac{\operatorname{tr}(H_\lambda)}n
   =\frac{n-d}{n}S(\lambda)
   \in[0,(n-d)/n].

Use `smoother.smoothness(lambda_)` for normalized
smoothness and `smoother.smoothness(lambda_, normalized=False)`
for the original denominator. For :math:`d>0`, the original
index cannot reach 1.

Because :math:`S` is strictly increasing, the continuous
optimization problem is invariant under reparameterization:

.. math::

   \arg\min_{\lambda\in[0,\infty]} C(\lambda)
   \longleftrightarrow
   \arg\min_{s\in[0,1]} C(S^{-1}(s)).

Finite **uniform smoothness** and **log-penalty** grids
sample different sets, however. Their discretized minima
can differ even though the exact optimum does not.

Classical leave-one-out cross-validation
----------------------------------------

To evaluate ordinary LOOCV, remove one observation from the
data-fidelity term, refit with the same difference penalty and
fixed :math:`\mu`, predict the omitted value, and average
squared prediction errors. Let
:math:`r=(I-H_\lambda)(y-p)` be **training residuals**,
:math:`h_i=(H_\lambda)_{ii}` the **leverage**, and
:math:`e_i^{(-i)}` the held-out prediction error.
The exact linear-smoother shortcut is

.. math::
   :label: loo

   e_i^{(-i)}
    =y_i-\widehat y_i^{(-i)}
    =\frac{r_i}{1-h_i},
   \qquad
   \mathrm{CV}(\lambda)=\frac1n
        \sum_{i=1}^n\left(\frac{r_i}{1-h_i}\right)^2.

This avoids :math:`n` explicit refits. The identity assumes
the penalty operator, its boundary convention, numeric reference
mean and :math:`\lambda` remain fixed in deletion refits.
The division becomes undefined at zero leverage denominator;
near-zero denominators cause numerical instability.

The **training residual** has seen its own observation;
a **LOO residual** has not. For :math:`m` common errors,

.. math::

   \mathrm{MSE}=\frac1m\sum_{i=1}^m e_i^2,
   \qquad
   \mathrm{RMSE}=\sqrt{\mathrm{MSE}}.

Their rankings coincide for the same set of errors, but MSE
has squared units and RMSE has the data's units.

.. warning::

   LOOCV is **not chronological**: other observations retained
   during fitting can be later than the one omitted.
   Rolling-origin or expanding-window **time-series
   cross-validation** trains only on information available at a
   given date and scores forecasts at horizon :math:`h`.
   The package's `criterion="cv"` is ordinary in-sample LOO,
   not forecast-horizon selection.
