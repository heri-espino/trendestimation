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

Computational costs
-------------------

Full SVD requires O(n^3) time and O(n^2) memory. With projections
precomputed, EDF, smoothness, and GCV/AICc/BIC scores take O(n)
operations per lambda. Full trend reconstruction and exact diagonal
leverage CV scoring take O(n^2). Compare fairly with structured
banded Cholesky algorithms rather than only naive dense inverses.
Numerical conditioning becomes delicate for high difference orders.
