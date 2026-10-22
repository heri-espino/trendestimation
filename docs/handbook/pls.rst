Penalized least squares and spectral structure
================================================

Model and normal equations
--------------------------

For :math:\`0\le d<n\`, penalized least squares estimates the trend by

.. math::

   \widehat{\tau}_{\lambda,\mu}
   =\underset{\tau\in\mathbb R^n}{\operatorname{argmin}}
    \bigl\{\|y-\tau\|_2^2+
    \lambda\|D_d\tau-\mu\mathbf1\|_2^2\bigr\}.

The forward-difference operator is

.. math::

   (D_d\tau)_t
   =\sum_{k=0}^{d}(-1)^{d-k}\binom{d}{k}\tau_{t+k},
   \qquad t=0,\ldots,n-d-1.

Differentiating the quadratic objective in :math:\`\tau\` gives

.. math::

   (I+\lambda Q)\widehat{\tau}_{\lambda,\mu}
   =y+\lambda\mu D_d^\top\mathbf1,
   \qquad Q=D_d^\top D_d.

The matrix :math:\`I+\lambda Q\` is positive definite for every
finite :math:\`\lambda\ge0\`; therefore the fitted trend is unique.

Affine closed-form solution
---------------------------

Select any :math:\`p_\mu\` satisfying
:math:\`D_dp_\mu=\mu\mathbf1\`. In zero-based time indexing, a
particular choice is :math:\`(p_\mu)_t=\mu\binom{t}{d}\` for
:math:\`d\ge1\`; for :math:\`d=0\`, use
:math:\`p_\mu=\mu\mathbf1\`.

.. math::

   \boxed{\widehat{\tau}_{\lambda,\mu}
     =p_\mu+H_\lambda(y-p_\mu)},
   \qquad H_\lambda=(I+\lambda Q)^{-1}.

The affine reference is held fixed when using the standard
hat-matrix formulas. The data-driven option \`\`mu="data"\`\` uses
:math:\`\overline{D_dy}\` and changes the unconditional influence
of each observation.

Rank, nullspace, and limiting trend
-----------------------------------

For :math:\`d\ge1\`, :math:\`\operatorname{rank}(D_d)=n-d\`.
Consequently,

.. math::

   \ker Q=\ker D_d
   =\operatorname{span}\{1,t,\ldots,t^{d-1}\},
   \qquad \dim\ker Q=d.

Thus :math:\`Q\` has exactly :math:\`d\` zero eigenvalues
in exact arithmetic. A full eigendecomposition
:math:\`Q=V\operatorname{diag}(\delta_1,\ldots,\delta_n)V^\top\`
yields

.. math::

   H_\lambda
   =V\operatorname{diag}
    \left(\frac{1}{1+\lambda\delta_j}\right)V^\top.

At :math:\`\lambda=0\`, :math:\`\widehat{\tau}=y\`.
At :math:\`\lambda=\infty\`, the exact limiting solution is the
least-squares projection onto the affine space
:math:\`\{\tau:D_d\tau=\mu\mathbf1\}\`.
For :math:\`\mu=0\`, this is a polynomial fit of degree at most
:math:\`d-1\`; for nonzero :math:\`\mu\`, it has a fixed
degree-:math:\`d\` particular component.

Implementation notes
--------------------

- \`\`difference_matrix(n, order=d)\`\` constructs the penalty operator.
- \`\`TrendSmoother(n, order=d).fit(y, lambda_=..., mu=...)\`\` fits
  the trend.
- Full SVD preprocessing costs :math:\`O(n^3)\` time and
  :math:\`O(n^2)\` memory; repeated full trend reconstruction is
  :math:\`O(n^2)\`. For isolated fits at large :math:\`n\`,
  banded solvers may be preferable.

See :doc:\`smoothness\` for the trace and index, and
:doc:\`../mathematics\` for the longer discussion.
