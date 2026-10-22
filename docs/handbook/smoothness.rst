Effective degrees of freedom and smoothness
=============================================

Spectral attenuation and EDF
----------------------------

Let the :math:`r=n-d` strictly positive penalty eigenvalues
be :math:`\delta_j`. For :math:`\lambda\ge0`, define

.. math::

   \alpha_j(\lambda)=\frac{1}{1+\lambda\delta_j},
   \qquad q_j(\lambda)=1-\alpha_j(\lambda)
           =\frac{\lambda\delta_j}{1+\lambda\delta_j}.

The unpenalized :math:`d` directions have attenuation 1.
The **conditional effective degrees of freedom** are

.. math::

   \nu(\lambda)=\operatorname{tr}(H_\lambda)
          =d+\sum_{j=1}^{r}\alpha_j(\lambda).

As :math:`\lambda` moves from zero to infinity,
:math:`\nu(\lambda)` decreases from :math:`n` to :math:`d`
(for :math:`d=0`, to zero).

Original Guerrero index and normalized index
--------------------------------------------

The original trace-based index is

.. math::

   \boxed{S_G(\lambda)=1-\frac{\nu(\lambda)}{n}
      =\frac1n\sum_{j=1}^r q_j(\lambda)},
   \qquad 0\le S_G\le\frac{n-d}{n}.

The package also reports a **normalized** index on the unit interval,

.. math::

   \boxed{S(\lambda)=\frac{n-\nu(\lambda)}{n-d}
          =\frac1r\sum_{j=1}^r q_j(\lambda)},
   \qquad S\in[0,1].

Thus :math:`S_G=(n-d)S/n`. This is an exact change of
normalization; **it does not assert equivalence of the geometries
of different difference orders**.

Analytical derivatives and inverse map
--------------------------------------

For finite penalties,

.. math::

   \begin{aligned}
   \nu'(\lambda)
     &=-\sum_{j=1}^r
       \frac{\delta_j}{(1+\lambda\delta_j)^2},\\
   S_G'(\lambda)
     &=\frac1n\sum_{j=1}^r
       \frac{\delta_j}{(1+\lambda\delta_j)^2},\\
   S'(\lambda)
     &=\frac1r\sum_{j=1}^r
       \frac{\delta_j}{(1+\lambda\delta_j)^2}>0,\\
   S''(\lambda)
     &=-\frac2r\sum_{j=1}^r
       \frac{\delta_j^2}{(1+\lambda\delta_j)^3}<0.
   \end{aligned}

Hence :math:`S` is strictly increasing and concave as a function
of :math:`\lambda`; every target :math:`s\in(0,1)` has
exactly one positive solution to :math:`S(\lambda)=s`.

.. math::

   S(0)=0,\quad S(\infty)=1,\quad
   S_G(\infty)=\frac{n-d}{n}.

For special spectra with identical positive eigenvalues
:math:`\delta_j=\delta`, the inverse is explicit:

.. math::

   \lambda(s)=\frac{s}{\delta(1-s)}.

For a general spectrum the inverse requires scalar numerical
root-finding; see :doc:`numerical_methods`.

API
---

.. code-block:: python

   smoother = TrendSmoother(n, order=d)
   S = smoother.smoothness(lam)
   S_guerrero = smoother.smoothness(lam, normalized=False)
   edf = smoother.degrees_of_freedom(lam)
   lam_recovered = smoother.lambda_for_smoothness(S, method="auto")

All these degrees of freedom are **conditional on fixed** :math:`\mu`.
If ``mu="data"`` is estimated from the same observations, the
complete fitted-value sensitivity is not described solely by
:math:`\operatorname{tr}(H_\lambda)`.
