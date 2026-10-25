Gaussian marginal likelihood and variance components
====================================================

Stochastic interpretation of the penalty
----------------------------------------

The MLE criterion uses **additional Gaussian assumptions**.
For fixed :math:`\mu`, consider the independent latent and
observation noise components:

.. math::

   y=\tau+\varepsilon,\qquad
   \varepsilon\sim N(0,\sigma_\varepsilon^2 I),\qquad
   D_d\tau-\mu\mathbf1\sim N(0,\sigma_\eta^2 I).

The precision ratio corresponding to the PLS penalty is

.. math::

   \boxed{\lambda
      =\frac{\sigma_\varepsilon^2}{\sigma_\eta^2}}.

This interpretation is **not** required to use the deterministic
PLS fit; it is used for the Gaussian likelihood estimates.

Marginal spectral likelihood
----------------------------

Let :math:`r=n-d`, :math:`z_j` be coordinates of
:math:`y-p_\mu` in the positive-penalty eigenspace, and
:math:`\delta_j>0` its eigenvalues. After eliminating
unpenalized polynomial coordinates as nuisance effects,
the marginal variances are

.. math::

   \operatorname{Var}(z_j\mid\lambda,\sigma_\varepsilon^2)
    =\sigma_\varepsilon^2 c_j(\lambda),\qquad
   c_j(\lambda)=1+\frac{1}{\lambda\delta_j}.

For fixed positive :math:`\lambda`, profile the observation variance:

.. math::

   \widehat\sigma_\varepsilon^2(\lambda)
    =\frac1r\sum_{j=1}^{r}\frac{z_j^2}{c_j(\lambda)}.

The package minimizes twice the negative **profiled marginal
log-likelihood**, up to constants independent of the penalty:

.. math::

   \boxed{
   L_{\mathrm{profile}}(\lambda)
   =r\log\left(\frac1r\sum_{j=1}^{r}
       \frac{z_j^2}{c_j(\lambda)}\right)
       +\sum_{j=1}^{r}\log c_j(\lambda)
   }.

It is this **MLE score**, rather than residual MSE, that is minimized.
See :doc:`derivatives` for its analytical derivative.

Variance components
-------------------

The estimated latent difference variance is

.. math::

   \widehat\sigma_\eta^2(\lambda)
     =\frac{\widehat\sigma_\varepsilon^2(\lambda)}{\lambda}.

At :math:`\lambda=\infty` the implementation uses the
limiting zero latent-difference variance. These are not the
empirical variance of the fitted trend, forecast-error
variance, or prediction intervals.

.. code-block:: python

   choice = select_lambda(
       smoother, y, criterion="mle", mu=0.0
   )
   parts = estimate_variance_components(
       smoother, y, lambda_=choice.lambda_, mu=0.0
   )
   print(parts.observation_variance, parts.difference_variance)


Estimating the reference-difference mean
----------------------------------------

There are **two distinct estimates** of :math:`\mu` in the
research framework. The public ``mu="data"`` option uses
Guerrero's empirical mean of observed differences:

.. math::

   \boxed{\widehat\mu_G
     =\frac{1}{n-d}\mathbf1^\top D_dy
     =\operatorname{mean}(D_dy)}.

This is a **plug-in reference mean**. In particular, for
:math:`d>0` it is generally not the arithmetic mean of
the raw observations :math:`y`.

Conditional generalized least-squares profile for :math:`\mu`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following analytical estimator is derived in the research
manuscript (``paper/sections/likelihood_mu.tex``), but is
**not currently exposed by the Python package as a joint-MLE API**.

Assume :math:`1\le d<n` and finite :math:`\lambda>0`.
Define the unit-reference vector
:math:`p^{(1)}_t=\binom{t}{d}`, indexed from
:math:`t=0,\ldots,n-1`, so that
:math:`D_dp^{(1)}=\mathbf1`. Let
:math:`v_j` be the positive-penalty eigenvectors
of :math:`Q=D_d^\top D_d` and write

.. math::

   z_j^{(0)}=v_j^\top y,\qquad
   b_j=v_j^\top p^{(1)},\qquad
   w_j(\lambda)=\frac{1}{c_j(\lambda)}
     =\frac{\lambda\delta_j}{1+\lambda\delta_j}.

Here :math:`z_j^{(0)}` is the coordinate of the **raw**
observations, unlike the fixed-mean coordinates
:math:`z_j(\mu)=v_j^\top(y-\mu p^{(1)})
=z_j^{(0)}-b_j\mu` used in the preceding sections.

For fixed :math:`\lambda`, the relevant weighted residual sum
of squares is

.. math::

   T(\lambda,\mu)=\sum_{j=1}^{n-d}
       w_j(\lambda)(z_j^{(0)}-b_j\mu)^2.

Differentiation with respect to :math:`\mu` yields

.. math::

   \frac{\partial T}{\partial\mu}
       =-2\sum_j w_jb_j(z_j^{(0)}-b_j\mu),\qquad
   \frac{\partial^2 T}{\partial\mu^2}
       =2\sum_j w_j b_j^2>0.

The last inequality follows because
:math:`D_dp^{(1)}=\mathbf1`, hence the positive-eigenvalue
projection of :math:`p^{(1)}` is not zero.
Setting the first derivative to zero gives the unique
conditional **weighted least-squares estimator**:

.. math::

   \boxed{\widehat\mu(\lambda)
       =\frac{\sum_{j=1}^{n-d}
            w_j(\lambda)b_j z_j^{(0)}}
            {\sum_{j=1}^{n-d}w_j(\lambda)b_j^2}}.

For fixed :math:`\lambda`, this also minimizes the PLS
objective *jointly over the fitted trend and* :math:`\mu`
after the trend has been eliminated. Its equality with the
conditional likelihood minimizer follows because the
profiled Gaussian score is increasing in :math:`T`
when :math:`T>0`.

Connection to Guerrero's empirical mean
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As :math:`\lambda\downarrow0`,
:math:`w_j(\lambda)/\lambda\to\delta_j`.
Since :math:`Q=D_d^\top D_d`,

.. math::

   \begin{aligned}
   \lim_{\lambda\downarrow0}\widehat\mu(\lambda)
   &=\frac{(p^{(1)})^\top Qy}
           {(p^{(1)})^\top Qp^{(1)}}\\
   &=\frac{(D_dp^{(1)})^\top D_dy}
           {\|D_dp^{(1)}\|^2}\\
   &=\frac{\mathbf1^\top D_dy}{n-d}
   =\widehat\mu_G.
   \end{aligned}

Thus the empirical mean of the observed differences is
**the small-penalty limit of the conditional estimator**,
not in general the conditional estimator at a positive penalty.

Concentrated likelihood for :math:`(\lambda,\mu)`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Allowing :math:`\mu` to vary, the profiled Gaussian
negative log-likelihood (up to constants) becomes

.. math::

   J(\lambda;\mu)
      =(n-d)\log\left(\frac{T(\lambda,\mu)}{n-d}\right)
       +\sum_{j=1}^{n-d}\log c_j(\lambda).

Insert the conditional optimum :math:`\widehat\mu(\lambda)`
to obtain a one-dimensional concentrated objective:

.. math::

   J_{\mathrm{conc}}(\lambda)
     =J(\lambda;\widehat\mu(\lambda)),\qquad
   \widehat\lambda\in\underset{\lambda>0}{\operatorname{argmin}}
                    \,J_{\mathrm{conc}}(\lambda),\qquad
   \widehat\mu=\widehat\mu(\widehat\lambda).

If the optimum is finite, its corresponding profiled
variance components would be

.. math::

   \widehat\sigma_\varepsilon^2
    =\frac{T(\widehat\lambda,\widehat\mu)}{n-d},
   \qquad
   \widehat\sigma_\eta^2
    =\frac{\widehat\sigma_\varepsilon^2}{\widehat\lambda}.

These are **conditional/profile likelihood equations**, not
claims of a publicly implemented joint estimator. Numerical
optimization over :math:`\lambda` and identifiability must
still be assessed; the result is not a closed-form joint solution.
Profiling an additional mean parameter does not automatically
make these variance estimates unbiased.

Estimating :math:`\mu` from the same observations changes
the data-to-fitted-trend operator. Accordingly the fixed-mean
effective degrees of freedom :math:`\operatorname{tr}(H_\lambda)`
and the usual fixed-mean LOOCV denominators cannot simply
be reused as though :math:`\mu` were known. For the present
public API, see :doc:`../api/selection`.

Assumptions and identifiability
-------------------------------

- The nullspace is an unpenalized nuisance (REML-style elimination).
- The penalty prior is improper at :math:`\lambda=0`,
  which the implemented MLE score rejects.
- The implementation requires :math:`d\ge1`, :math:`r\ge2`
  and positive weighted spectral energy.
- The option ``mu="data"`` means
  :math:`\mu=\overline{D_dy}` as a **conditional plug-in**,
  not a joint MLE of :math:`\mu` and :math:`\lambda`.
- The current public MLE selector uses a candidate grid, not
  analytical derivative-based optimization.

See :doc:`../mathematics`, :doc:`../api/variances`,
and Biessy (2026) in :doc:`../references`.
