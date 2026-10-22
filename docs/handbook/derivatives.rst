Analytical derivatives of selection criteria
=============================================

Matrix and spectral identities
------------------------------

For a fixed numeric reference mean :math:`\mu`, set
:math:`z=y-p_\mu`, :math:`Q=D_d^\top D_d` and
:math:`H=(I+\lambda Q)^{-1}`. Differentiating an inverse gives

.. math::

   \boxed{H'(\lambda)=-H Q H}.

Let :math:`\alpha_j=1/(1+\lambda\delta_j)` and
:math:`q_j=1-\alpha_j`, for the positive penalty eigenvalues.
Then

.. math::

   \alpha_j'=-\frac{\delta_j}{(1+\lambda\delta_j)^2},
   \qquad
   q_j'=\frac{\delta_j}{(1+\lambda\delta_j)^2},
   \qquad \nu'=\sum_j\alpha_j'.

If :math:`z_j` denotes the coordinates of :math:`y-p_\mu`
in the positive-eigenvalue basis, the following scalar sums
are exact:

.. math::

   R=\sum_{j=1}^{n-d}q_j^2 z_j^2,\qquad
   R'=2\sum_{j=1}^{n-d}q_j q_j' z_j^2.

These common derivatives make GCV, AICc and BIC inexpensive
to differentiate **after** eigenbasis preprocessing.

Exact derivative of classical CV
--------------------------------

Put :math:`r_i=e_i` (training residual) and
:math:`b_i=1-h_i` (leave-one-out denominator). From the
matrix inverse identity,

.. math::

   r'=HQH z,\qquad
   h_i'=-(HQH)_{ii},\qquad
   b_i'=(HQH)_{ii}.

Writing :math:`u_i=r_i/b_i` gives the quotient rule

.. math::

   u_i'=\frac{r_i'b_i-r_i b_i'}{b_i^2},
   \qquad
   \boxed{\mathrm{CV}'(\lambda)
     =\frac{2}{n}\sum_{i=1}^n u_i u_i'}.

It holds whenever :math:`\lambda>0` and all denominators
are defined. In the repository, the implementation exploits
the cached positive-eigenvalue basis and cancels common
small-:math:`\lambda` factors rather than taking differences
of nearly equal numbers. No finite-difference approximation
is used in the production derivative.

.. code-block:: python

   from trendestimation.criteria import cv_derivative

   slope = cv_derivative(smoother, y, lambda_=lam, mu=0.0)

Derivatives of GCV, AICc and BIC
-------------------------------

For :math:`R>0` and admissible denominators, differentiate
the **exact score conventions used in the package**:

.. math::

   \begin{aligned}
   \mathrm{GCV}'(\lambda)
     &=\mathrm{GCV}(\lambda)
       \left[\frac{R'}{R}+\frac{2\nu'}{n-\nu}\right],\\[3pt]
   \mathrm{AICc}'(\lambda)
     &=\frac{R'}{R}
        +\frac{(2n-3)\nu'}{(n-\nu-2)^2},\\[3pt]
   \mathrm{BIC}'(\lambda)
     &=\frac{R'}{R}+\frac{\log n}{n}\nu'.
   \end{aligned}

These identities follow by the product/quotient rules, with
:math:`R` and :math:`\nu` defined in :doc:`criteria`.
They are **mathematical formulas**, not claims that the
public selector uses derivative optimization for GCV, AICc,
or BIC: it currently uses a grid for those criteria.

Derivative of the Gaussian marginal score
-----------------------------------------

For :math:`\lambda>0`, define the positive-coordinate
weights and weighted sum

.. math::

   w_j(\lambda)=\frac{\lambda\delta_j}{1+\lambda\delta_j},
   \qquad
   T(\lambda)=\sum_{j=1}^{n-d} w_j z_j^2.

The implemented profiled Gaussian score is
:math:`L=r\log(T/r)-\sum_j\log w_j`, with :math:`r=n-d`.
Consequently, whenever :math:`T>0`,

.. math::

   \boxed{L'(\lambda)
      =r\,\frac{T'}{T}
       -\sum_{j=1}^{r}\frac{w_j'}{w_j}},
   \qquad
   T'=\sum_{j=1}^r w_j' z_j^2.

The corresponding MLE selector **currently uses grid
optimization**, not this derivative; see :doc:`likelihood`.

Changing variables from penalty to smoothness
---------------------------------------------

For :math:`s=S(\lambda)` and any differentiable
criterion :math:`C`,

.. math::

   \frac{d\,C(\lambda(s))}{ds}
      =\frac{C'(\lambda)}{S'(\lambda)}.

Since :math:`S'(\lambda)>0` at finite positive penalties,
**interior stationary points** are preserved by the change
of variable. One still needs :math:`\lambda(s)` to evaluate
the existing PLS criterion in smoothness coordinates.

A zero of :math:`C'(\lambda)` need not be a minimum or
global optimum. Inspect the criterion values at stationary
candidates **and** admissible boundaries.
