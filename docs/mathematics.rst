Mathematics and computational scope
===================================

Let :math:`y\in\mathbb R^n`, :math:`0\le d<n`,
:math:`D_d\in\mathbb R^{(n-d)\times n}` denote order-d forward
differences and :math:`\lambda\ge 0`. For scalar :math:`\mu`,

.. math::

   \widehat\tau=\arg\min_\tau
   \left\{\|y-\tau\|_2^2
   +\lambda\|D_d\tau-\mu\mathbf{1}\|_2^2\right\}.

Choose a particular solution p satisfying
:math:`D_dp=\mu\mathbf{1}`.
For d>=1, choose :math:`p_t=\mu\binom{t}{d}` with t=0,...,n-1.
For d=0 use the constant reference p=mu*1.

.. math::

   \widehat\tau=p+H_\lambda(y-p),\qquad
   H_\lambda=(I+\lambda D_d^\top D_d)^{-1}.

If :math:`D_d^\top D_d=V\operatorname{diag}(\delta_j)V^\top`,

.. math::

   \widehat\tau=p+V\operatorname{diag}
   \left(\frac{1}{1+\lambda\delta_j}\right)V^\top(y-p).

For integer 1<=d<n, the penalty has exactly d zero eigenvalues
**in exact arithmetic**; for d=0, none. The full SVD of D_d provides
the positive spectrum and explicit d-dimensional nullspace. At infinite
penalty the code evaluates the limiting nullspace projection, rather than
approximating it by an arbitrary huge finite lambda.

The Guerrero and normalized trace-based smoothness indices are

.. math::

   S_G=1-\frac{\operatorname{tr}H_\lambda}{n},
   \qquad S=\frac{n-\operatorname{tr}H_\lambda}{n-d}.

Both, and the reported EDF, condition on a fixed mu. When mu is
estimated from observations they are not automatically the complete
effective degrees of freedom of the data-dependent procedure.



Gaussian marginal maximum likelihood
------------------------------------

The ``mle`` criterion chooses a smoothing parameter by maximizing the
Gaussian marginal likelihood rather than minimizing the penalized
least-squares objective itself. For a fixed reference mean ``mu``, the
positive-penalty spectral coordinates of ``y-p(mu)`` are denoted by
:math:`z_j`, with penalty eigenvalues :math:`\delta_j>0`. On the
:math:`r=n-d` positive coordinates we posit independent latent trend
noise of variance :math:`\sigma^2/(\lambda\delta_j)` and observation
noise of variance :math:`\sigma^2`. The implied marginal variances
are :math:`\sigma^2 c_j(\lambda)`, where

.. math::

   c_j(\lambda) = 1 + \frac{1}{\lambda\delta_j},\qquad
   \widehat\sigma^2(\lambda) =
   \frac{1}{r}\sum_{j=1}^{r}\frac{z_j^2}{c_j(\lambda)}.

After profiling the nuisance observation variance, the implementation
minimizes twice the negative marginal log-likelihood, excluding terms
independent of :math:`\lambda`:

.. math::

   L_{\mathrm{profile}}(\lambda) =
      r\log\left[\frac{1}{r}\sum_{j=1}^r
                  \frac{z_j^2}{c_j(\lambda)}\right]
      +\sum_{j=1}^r\log c_j(\lambda).

The remaining :math:`d` coordinates form the unpenalized polynomial
nullspace, treated as nuisance trend coordinates (REML-style
likelihood). This choice is motivated by the Gaussian marginal
likelihood of Biessy (2026, Section 5.3), but differs by profiling the
unknown observation variance. It assumes Gaussian noise and a latent
Gaussian difference penalty; it is *not* a distribution-free selection
method. The prior is improper at :math:`\lambda=0`, which is not
considered an admissible MLE candidate, whereas the
:math:`\lambda\rightarrow\infty` limit is computed exactly.

In order zero, the variance components are confounded when observation
variance is profiled out. The implementation therefore rejects MLE
selection for :math:`d=0` or fewer than two positive-penalty coordinates.
Very low or exactly zero positive-subspace residual energy can also
lead to a degenerate likelihood.

The alternative ``mu="data"`` estimates the reference level by the
arithmetic mean of :math:`D_d y`, the observed differences of order
:math:`d`. This plug-in is passed to the MLE score *as fixed* and
is not jointly optimized with the variance components. Classical
``cv``, ``gcv``, ``aicc``, and ``bic`` still require fixed numeric
reference means because their usual degrees-of-freedom and ordinary
LOOCV formulas omit plug-in-mean re-estimation.

Computational costs
-------------------

Full SVD requires O(n^3) time and O(n^2) memory. With projections
precomputed, EDF, smoothness, and GCV/AICc/BIC scores take O(n)
operations per lambda. Full trend reconstruction and exact diagonal
leverage CV scoring take O(n^2). Compare fairly with structured
banded Cholesky algorithms rather than only naive dense inverses.
Numerical conditioning becomes delicate for high difference orders.
