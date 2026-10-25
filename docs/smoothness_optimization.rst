.. _smoothness-optimization:

Smoothing-parameter optimization
================================

This guide explains finite-difference penalized least squares,
normalized smoothness, ordinary cross-validation, numerical
optimization and inversion. For an intuitive first introduction to
why the index :math:`S\in[0,1]` can replace :math:`\lambda` as a
search coordinate, see :doc:`smoothness_coordinate`. Examples use deterministic synthetic
data, not live downloads. The examples below use the merged public CV-optimization and
smoothness-inversion APIs. They distinguish exact algebraic identities
from numerical optimization, which is not globally certified.

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

Selecting in penalty or normalized smoothness coordinates
-------------------------------------------------------------

The selector can search in penalty (lambda) or in the normalized
smoothness coordinate S between zero and one. It changes only
**where candidates are sampled and refined**: the original CV,
GCV, AICc, BIC and conditional Gaussian MLE scores stay unchanged.

Let Lambda denote the inverse of S. Then the selection problem can
be written as

.. math::

   \widehat s=\arg\min_{s\in[0,1]}C(\Lambda(s);\mu),
   \qquad
   \widehat\lambda=\Lambda(\widehat s).

For a fixed numerical reference mean, the chain rule is

.. math::
   :label: score-s-derivative

   \frac{d\,C(\Lambda(s);\mu)}{ds}
     =\frac{dC/d\log\lambda}{dS/d\log\lambda},
   \qquad
   \frac{dS}{d\log\lambda}
     =\frac1{n-d}\sum_{j=1}^{n-d}
        \frac{\lambda\delta_j}{(1+\lambda\delta_j)^2}>0.

For classical fixed-mean LOOCV the library uses this **analytical
chain-rule derivative** to refine stationary candidates directly
in smoothness. A combined uniform and logit-spaced grid explores
both the center and the tails. The previous log-penalty optimizer
remains the default.

.. code-block:: python

   import numpy as np
   from trendestimation import TrendSmoother, select_lambda

   t = np.arange(35, dtype=float)
   y = np.sin(t / 6) + np.random.default_rng(24).normal(0, 0.2, t.size)
   solver = TrendSmoother(len(y), order=2)

   by_lambda = select_lambda(solver, y, criterion="cv",
                             search_space="lambda", mu=0.1)
   by_s = select_lambda(solver, y, criterion="cv",
                        search_space="smoothness", mu=0.1)

   print("Penalty search:", by_lambda.lambda_, by_lambda.smoothness)
   print("Smoothness search:", by_s.lambda_, by_s.smoothness)

   # Candidate grids are interpreted in the selected coordinate.
   s_grid = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
   tested = select_lambda(solver, y, criterion="gcv",
                          search_space="smoothness", grid=s_grid)
   print(tested.search_grid)  # Values in S, including endpoints.
   print(tested.grid)         # Matching lambda values, including infinity.
   print(tested.scores)       # Original GCV scores in the same order.

For other criteria, including MLE, the smoothness-coordinate default
is a numerical S grid: only CV has analytical derivative guidance.
Explicit grids preserve input order and duplicates. The returned
**lambda_** is always the selected penalty and **smoothness** its
normalized index. The legacy **grid** attribute still contains the
evaluated penalties, while **search_grid** contains coordinates
in the selected search space; both align with **scores**.

Exact endpoints: S=0 maps to lambda=0 and S=1 maps to infinite
penalty. CV and MLE retain undefined values at their zero-penalty
boundary. Extreme interior S values may require penalties outside
float64 range.

.. warning::

   Bounded search is **not automatically faster**: every interior
   smoothness value requires numerical inversion. The denominator
   dS/dlog(lambda) approaches zero near the endpoints. Finite S
   grids and logarithmic lambda grids can find different minima;
   no finite scan certifies global optimality. This option does
   not jointly estimate lambda and mu.

For the full proof and the deferred joint-MLE direction see
https://github.com/heri-espino/trendestimation/blob/main/notes/smoothness_parameterization.md.

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

Analytical derivatives of classical CV
--------------------------------------

For fixed numeric :math:`\mu`, put :math:`z=y-p` and
:math:`Q=D_d^\top D_d`. Differentiating
:math:`(I+\lambda Q)H_\lambda=I` gives

.. math::
   :label: derivative-hat

   H_\lambda'=-H_\lambda QH_\lambda.

Because :math:`r=(I-H_\lambda)z` and
:math:`h_i=(H_\lambda)_{ii}`, it follows that

.. math::

   r'=H_\lambda QH_\lambda z,\qquad
   h_i'=-(H_\lambda QH_\lambda)_{ii}.

The quotient rule applied to :eq:`loo` gives

.. math::
   :label: derivative-loo

   \frac{d e_i^{(-i)}}{d\lambda}
    =\frac{r_i'(1-h_i)+r_i h_i'}{(1-h_i)^2},
   \qquad
   \frac{d\,\mathrm{CV}}{d\lambda}
    =\frac2n\sum_{i=1}^n e_i^{(-i)}
         \frac{d e_i^{(-i)}}{d\lambda}.

For log-penalty :math:`u=\log\lambda`,
:math:`d\mathrm{CV}(e^u)/du=\lambda\,\mathrm{CV}'(\lambda)`.
An interior differentiable minimum has zero derivative,
but a stationary point may be a local maximum or a
non-global minimum. **Analytical score evaluation or
differentiation is not an analytical minimizer.**

.. note::

   The public `trendestimation.criteria.cv_derivative` evaluates the
   analytical derivative for positive penalties and **fixed numeric**
   `mu`. For `criterion="cv"`, `select_lambda(..., method="auto")`
   uses a broad log-penalty scan and derivative-based refinement.
   `method="grid"` retains the established finite candidate search.
   The automatic derivative search checks multiple candidate minima
   but **does not certify the global minimum**.

Competing selection criteria
----------------------------

Let :math:`\mathrm{RSS}=\|r\|_2^2` and
:math:`k=\operatorname{tr}(H_\lambda)`.
The implemented scores use **smaller is better**.
AICc and BIC have alternative conventions in the literature;
the table records the library's current formulas.

.. list-table:: Supported classical selectors and Gaussian MLE
   :header-rows: 1
   :widths: 15 40 45

   * - Criterion
     - Score
     - Statistical meaning
   * - `cv`
     - :math:`n^{-1}\sum_i(r_i/(1-h_i))^2`
     - Exact classical LOO for fixed numeric :math:`\mu`
   * - `gcv`
     - :math:`(\mathrm{RSS}/n)/(1-k/n)^2`
     - Substitutes average leverage for pointwise leverage
   * - `aicc`
     - :math:`\log(\mathrm{RSS}/n)+(2k+1)/(n-k-2)`
     - Small-sample correction; undefined if :math:`n-k-2\le0`
   * - `bic`
     - :math:`\log(\mathrm{RSS}/n)+k\log(n)/n`
     - Complexity penalty increasing with sample size
   * - `mle`
     - Profiled Gaussian marginal negative log-likelihood
     - Uses latent Gaussian differences, not CV or direct
       minimization of the penalized least-squares loss

In the Gaussian **marginal MLE**, let :math:`w_j` denote
the coordinates of :math:`y-p` in the positive-penalty
eigenvectors, and define :math:`c_j(\lambda)=1+1/(\lambda\delta_j)`. With independent Gaussian
observation errors of variance :math:`\sigma_\varepsilon^2`,
Gaussian latent differences of variance
:math:`\sigma_\eta^2`, and
:math:`\lambda=\sigma_\varepsilon^2/\sigma_\eta^2`,
the profiled score (up to constants) is

.. math::

   L_{\mathrm{profile}}(\lambda)
    =r\log\left(\frac1r\sum_{j=1}^r
                 \frac{w_j^2}{c_j(\lambda)}\right)
     +\sum_{j=1}^r\log c_j(\lambda).

The unpenalized polynomial coordinates are treated as
nuisance components (REML-style). MLE rejects
:math:`\lambda=0` (improper latent prior) and structurally
unidentified cases :math:`d=0` or :math:`r<2`.
Unlike the classical criteria, it accepts `mu="data"`,
but **conditions** on the observed-difference mean:
this is not joint maximum likelihood over :math:`\mu`.
See :doc:`mathematics` and :doc:`api/variances`.

Numerical optimization and global minima
----------------------------------------

The default depends on the criterion. For **classical CV**,
`select_lambda(..., criterion="cv", method="auto")` evaluates
97 log-spaced seed penalties spanning the positive eigenvalue
transition scales, refines sampled derivative sign changes with
Brent's bracketed root finder, and compares original CV scores,
candidate valleys and boundary limits. This is a heuristic
multi-start search, **not a proof of global optimality**.

For `method="grid"`, the established default evaluates
**121 geometric penalties** plus the exact :math:`\lambda=\infty`
limit. GCV, AICc, BIC, and MLE continue to use grid selection
under `method="auto"`. An explicitly provided `grid=` also
selects exclusively among its supplied candidate penalties.

.. list-table:: Methods and trade-offs
   :header-rows: 1
   :widths: 27 35 38

   * - Method
     - Benefit
     - Risk
   * - Logarithmic penalty grid
     - Spans many penalty orders of magnitude
     - Can miss a narrow minimum; add :math:`0,\infty`
   * - Uniform smoothness grid
     - Uniformly covers the bounded :math:`S` coordinate
     - Uneven penalty-space resolution
   * - Analytical CV derivative
     - Finds candidate stationary points efficiently
     - Roots are not necessarily global minima
   * - Local numerical refinement
     - Increases precision near a promising candidate
     - Only local unless extra assumptions hold
   * - Multiple candidate basins
     - Compare objective values after refining each basin
     - A finite scan cannot rigorously exclude missed basins
   * - Boundary evaluation
     - Considers exact :math:`\lambda=0,\infty` limits
     - Some criteria are undefined there

A defensible workflow scans a broad log-penalty range,
locates low-score basins and derivative sign changes,
refines multiple candidates, evaluates **objective values**
at refined points and admissible boundaries, and repeats
after enlarging the interval. Report the numerical tolerance.
Simply solving :math:`\mathrm{CV}'(\lambda)=0` does
**not** establish a global minimum.

Smoothness inversion: Brent, Newton, secant
-------------------------------------------

Given :math:`s\in(0,1)`, define
:math:`F(\lambda)=S(\lambda)-s`. Equation
:eq:`s-derivative` proves the root is unique.
The public `TrendSmoother.lambda_for_smoothness` implements
`method="auto"` (Brent for a general spectrum),
`"brentq"`, safeguarded `"newton"`, safeguarded `"secant"`,
and `"bisect"` (alias `"bisection"`). It solves in
:math:`x=\log\lambda`, using a stable spectral evaluation,
rather than taking unguarded steps in :math:`\lambda`.

* **Brent:** bracket-preserving and robust, with no analytical
  derivative required.
* **Newton–Raphson:** uses the analytical log-penalty derivative,
  retaining a valid bracket to safeguard out-of-range steps.
* **Secant:** estimates a slope from function evaluations and
  uses a bracket safeguard.
* **Bisection:** robust reference solver, generally requiring
  more evaluations.
* **Analytical inversion:** when all positive eigenvalues are
  identical (including `d=0`) or there is only one positive
  eigenvalue, the solver uses the exact scalar formula.

The `tol` and `maxiter` keywords control convergence;
unsupported inputs or unsuccessful solutions raise exceptions.
Endpoint inversion is exact:
:math:`s=0\mapsto\lambda=0` and
:math:`s=1\mapsto\lambda=\infty`.
With `normalized=False`, the upper valid target is
:math:`(n-d)/n`. The default prioritizes reliable convergence,
**not a universal guarantee of fastest runtime**.


Runnable Python: default CV, legacy grid, GCV
------------------------------------------------

All snippets use seeded synthetic values and the merged public APIs.
To install the source and documentation dependencies, run
`python -m pip install -e ".[docs,plot]"`.
Classical `criterion="cv"` defaults to derivative-guided
refinement, while `criterion="gcv"` uses the legacy grid by default.

.. code-block:: python

   import numpy as np
   from trendestimation import TrendSmoother, select_lambda

   rng = np.random.default_rng(2026)
   t = np.arange(60, dtype=float)
   y = (0.035 * t + 0.7 * np.sin(t / 8.0)
        + 0.35 * np.cos(t / 17.0)
        + rng.normal(0.0, 0.33, len(t)))
   smoother = TrendSmoother(len(y), order=2)

   default_cv = select_lambda(
       smoother, y, criterion="cv", mu=0.0
   )
   grid_cv = select_lambda(
       smoother, y, criterion="cv", mu=0.0, method="grid"
   )
   custom_grid = np.r_[np.geomspace(1e-4, 1e5, 180), np.inf]
   custom_cv = select_lambda(
       smoother, y, criterion="cv", mu=0.0, grid=custom_grid
   )
   gcv = select_lambda(
       smoother, y, criterion="gcv", mu=0.0
   )
   for selected in (default_cv, grid_cv, custom_cv, gcv):
       print(selected.criterion, selected.lambda_,
             selected.smoothness, selected.score)

   trend = smoother.fit(
       y, lambda_=default_cv.lambda_, mu=0.0
   ).trend

Notice that `select_lambda` returns the selected penalty
in `lambda_` and its score in `score`, while `scores`
and `grid` contain the evaluated candidates. An explicit `grid=` preserves user-defined candidates and
always selects among those candidates only under `method="auto"`.
The derivative can be evaluated independently:

.. code-block:: python

   from trendestimation.criteria import cv_derivative

   gradient = cv_derivative(
       smoother, y, lambda_=default_cv.lambda_, mu=0.0
   )
   print("d CV / d lambda:", gradient)

At an **interior** stationary minimum, this derivative should
approach zero. At a boundary optimum, it need not do so.

Runnable Python: numerical root-finder comparison
--------------------------------------------------

All the following methods are provided directly by
`TrendSmoother.lambda_for_smoothness`; they share the same
mathematical smoothness definition and reproduce the same target
within numerical tolerance.

.. code-block:: python

   import numpy as np
   from trendestimation import TrendSmoother

   smoother = TrendSmoother(60, order=2)
   target = 0.75
   methods = ("auto", "brentq", "newton", "secant", "bisect")
   roots = {
       name: smoother.lambda_for_smoothness(
           target, method=name, tol=1e-12, maxiter=200
       )
       for name in methods
   }
   for name, root in roots.items():
       print(name, root, abs(smoother.smoothness(root) - target))
       assert root > 0 and abs(smoother.smoothness(root) - target) < 1e-9

   original = smoother.smoothness(roots["auto"], normalized=False)
   restored = smoother.lambda_for_smoothness(
       original, normalized=False, method="newton"
   )
   assert np.isclose(restored, roots["auto"], rtol=1e-9)
   assert smoother.lambda_for_smoothness(0.0) == 0.0
   assert np.isinf(smoother.lambda_for_smoothness(1.0))

The most efficient method depends on the spectral distribution,
target smoothness and requested tolerance. A benchmark script in
`benchmarks/smoothness_root_solvers.py` compares iterations,
evaluations and measured time without including the one-time SVD.

Visual demonstration: smoothness versus CV MSE
-----------------------------------------------

The following figure uses 60 synthetic observations, difference
order 2, fixed `mu=0` and seed 2026. The graph shows 49
normalized smoothness candidates and highlights five of them.
**Smaller CV MSE is better** for this in-sample score.

.. figure:: _static/figures/smoothness-cv.svg
   :alt: A blue line of leave-one-out MSE against normalized smoothness decreases towards a minimum near 0.90 and rises sharply at high smoothness. Five candidate values from 0.15 to 0.90 are labelled.
   :width: 100%
   :align: center

   **Synthetic classical LOOCV example.** The five highlighted
   candidates are :math:`S=0.15,0.35,0.55,0.75,0.90`.
   Minimum displayed MSE occurs near :math:`S=0.90`.
   The shape is data-dependent and not a forecast result.

Run `python docs/examples/smoothness_optimization.py` to
regenerate the figure, inspect the selected penalty values,
compare default CV with GCV and review the candidate table.
The script writes only to `docs/_static/figures/` when
explicitly invoked (not as part of automatic documentation builds).

.. literalinclude:: examples/smoothness_optimization.py
   :language: python
   :caption: Generate the validation-error-versus-smoothness plot
   :linenos:

Scientific scope, limitations and sources
-----------------------------------------

Analytical LOO formulae require fixed numeric :math:`\mu`,
unchanged differencing conventions, and a fixed linear
smoother for each :math:`\lambda`. Search tolerances,
conditioning, excluded boundary solutions and the extent
of the scanned domain affect numerical results. An MLE
criterion is meaningful only under its assumed stochastic
model. Do not conflate in-sample smoothness selection
with selection for future forecast horizons.

For a detailed explanation of the computation cost and a runnable
naive-dense versus cached-spectral comparison, see :doc:`benchmarks`.

See :doc:`mathematics` for the complete mathematical
conventions, :doc:`api/selection` for current signatures,
:doc:`quickstart` for an introductory workflow and
:doc:`references` for the full bibliography.

* Guerrero (2007), *Time series smoothing by penalized least squares*:
  https://doi.org/10.1016/j.spl.2007.03.006
* Cortés-Toto, Guerrero and Reyes (2017), *Trend smoothness achieved
  by penalized least squares with the smoothing parameter chosen
  by optimality criteria*: https://doi.org/10.1080/03610918.2015.1005236
* Weinert (2007), *Efficient computation for Whittaker–Henderson smoothing*:
  https://doi.org/10.1016/j.csda.2006.11.038
* Biessy (2026), *Whittaker–Henderson smoothing revisited*:
  https://doi.org/10.1017/asb.2025.10061
