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
