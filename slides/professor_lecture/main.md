---
marp: true
theme: trend-lecture
size: 16:9
math: mathjax
html: true
paginate: true
header: "trendestimation · professor research lecture"
footer: "UDLAP · mathematical foundations, computation, evidence & open questions"
title: "Trend estimation by penalized least squares"
author: "Heriberto Espino-Montelongo"
---

<!-- _class: lead -->
# Trend estimation by penalized least squares

## Theory · numerical computation · selection criteria · open problems

Heriberto Espino-Montelongo · Daniela Cortés-Toto  
Universidad de las Américas Puebla

*Extended research-lecture notebook for discussion with the professor.*

---

<!-- _class: compact -->
# What the full lecture investigates

**A mathematical and computational research notebook — intentionally extensive.**

1. Motivation and the established PLS estimator.
2. Arbitrary finite-difference orders and reference means.
3. Affine solution, polynomial nullspace, SVD and cost.
4. Effective degrees of freedom and normalized smoothness.
5. Searching over penalty lambda or bounded smoothness S.
6. CV, GCV, AICc, BIC, Gaussian MLE and a deferred joint mean.
7. Fair runtime benchmarks, numerical conditioning and scientific examples.
8. What is new, what is known, and where research can continue.

**Legend:** established theory · implemented methods · tested numerical claims · future research.

---

<!-- _class: chapter -->
# I. Why estimate a trend?

## From noisy observations to a structured, interpretable signal

---

<!-- _class: fig -->
# Observed data versus latent signal

![width:1030px](figures/01_signal.svg)

*Deterministic synthetic data; truth is known only because the example is simulated.*

---

<!-- _class: math -->
# The fundamental observation model

$$y_t=\tau_t+\varepsilon_t,\qquad t=0,\ldots,n-1.$$

- $y_t$: observation.
- $\tau_t$: smooth latent component that we want to estimate.
- $\varepsilon_t$: remainder, not necessarily white noise.

**Our paper studies historical trend extraction, not demonstrated forecasting skill.**

---

<!-- _class: fig -->
# Fidelity to observations

![width:1030px](figures/02_fidelity.svg)

*Squared vertical discrepancies contribute to the data-fidelity term.*

---

<!-- _class: fig -->
# Why we also penalize roughness

![width:1030px](figures/03_penalty.svg)

*The penalty is evaluated on differences of the FITTED series, not observations.*

---

<!-- _class: math -->
# The single mathematical object behind this project

$$\boxed{
\widehat\tau_{\lambda,\mu}
=\arg\min_{\tau\in\mathbb R^n}
\left\{\|y-\tau\|^2+\lambda\|D_d\tau-\mu\mathbf1\|^2\right\}.
}$$

**Hyperparameters:** order $d$, reference mean $\mu$, penalty $\lambda\ge0$.

At $\lambda=0$ the model interpolates. As $\lambda\to\infty$ it approaches the affine difference constraint.

**This PLS family is established theory; the library is not claiming to invent it.**

---

<!-- _class: fig -->
# How the penalty alters the trend

![width:1030px](figures/04_lambda_sweep.svg)

*Same synthetic series; multiple positive penalties.*

---

<!-- _class: compact -->
# Historical contributions and attribution

| Work | Established idea |
| --- | --- |
| Whittaker | Graduation using penalized differences |
| Guerrero | Reference differences and controlled smoothness |
| Cortés-Toto et al. | CV, GCV, AICc, BIC comparisons for PLS |
| Whittaker–Henderson literature | Banded computation, likelihood interpretation |
| Our project | Integrated implementation, analytical derivatives, safe numerical inversion, $S$ search, reproducibility |

**Arbitrary order $d$, nonzero $\mu$, polynomial nullspaces and spectral PLS are not individually new.**

---

<!-- _class: chapter -->
# II. Understanding difference operators

## What does the penalty actually enforce?

---

<!-- _class: math -->
# First difference operator

$$D_1\tau=
(\tau_1-\tau_0,\tau_2-\tau_1,\ldots)^\top.$$

When $d=1$ and $\mu=0$, large $\lambda$ discourages changes between adjacent levels.

$$\lim_{\lambda\to\infty}\widehat\tau_{\lambda,0}
=\text{best constant fit.}$$

---

<!-- _class: fig -->
# Visualizing first differences

![width:1030px](figures/09_diff_d1.svg)

*First differences measure consecutive level changes.*

---

<!-- _class: math -->
# Second differences measure curvature

$$
(D_2\tau)_t=\tau_{t+2}-2\tau_{t+1}+\tau_t.
$$

$$
D_2=\begin{pmatrix}
1&-2&1&0&\cdots\\
0&1&-2&1&\cdots\\
\vdots&&\ddots&&
\end{pmatrix}.
$$

A large centered second-difference penalty gives a **linear** limiting fit.

---

<!-- _class: fig -->
# Visualizing second differences

![width:1030px](figures/10_diff_d2.svg)

*Second differences detect local changes of slope.*

---

<!-- _class: math -->
# Any admissible integer difference order

$$
\boxed{
(D_d\tau)_t=\sum_{k=0}^d(-1)^{d-k}\binom{d}{k}\tau_{t+k}.
}
$$

Examples: $D_1=(-1,1)$; $D_2=(1,-2,1)$; $D_3=(-1,3,-3,1)$.

The implementation also handles $d=0$, for which $D_0=I_n$.

**Numerical admissibility and floating-point reliability are different statements.**

---

<!-- _class: fig -->
# Third differences

![width:1030px](figures/11_diff_d3.svg)

*Third differences react to variation in curvature.*

---

<!-- _class: fig -->
# Higher-order binomial stencils

![width:1030px](figures/13_stencils.svg)

*Large coefficients contribute to high-order numerical conditioning problems.*

---

<!-- _class: fig -->
# A sparse banded difference operator

![width:1030px](figures/12_matrix_D.svg)

*Its structure is why banded linear solvers are strong baselines.*

---

<!-- _class: math -->
# Proof: why exactly d zero eigenvalues?

For $1\le d<n$, $D_d$ has $n-d$ independent rows:

$$\operatorname{rank}(D_d)=n-d.$$

Let $Q_d=D_d^\top D_d$. Since

$$x^\top Q_dx=\|D_dx\|^2,$$

we have $\ker Q_d=\ker D_d$. Consequently,

$$\boxed{\dim\ker Q_d=d.}$$

The result is exact algebra; numerical rank thresholds are a separate matter.

---

<!-- _class: fig -->
# What is in the nullspace?

![width:1030px](figures/14_kernel.svg)

*The basis 1, t, ..., t^(d-1) is annihilated by d-th differences.*

---

<!-- _class: fig -->
# Zero-mean infinite-penalty limits

![width:1030px](figures/15_polynomial_limit.svg)

*Constant for d=1, linear for d=2, quadratic for d=3.*

---

<!-- _class: math -->
# The nonzero mean difference is important

At infinite penalty,

$$\boxed{D_d\tau=\mu\mathbf1.}$$

With zero-based indices one particular solution is

$$p_t=\mu\binom td,\qquad D_dp=\mu\mathbf1.$$

Every limiting curve has form

$$\tau=p+q,\quad q\in\ker D_d.$$

Thus $\mu\ne0$ allows a **degree-d** polynomial component, instead of only degree at most $d-1$. This property is established, but computationally useful.

---

<!-- _class: fig -->
# Change the reference mean, keep order and penalty

![width:1030px](figures/06_mu_sweep.svg)

*The reference shifts the affine trend estimate.*

---

<!-- _class: fig -->
# The affine infinite-penalty limit for nonzero mu

![width:1030px](figures/07_affine_limit.svg)

*Degree-d particular solution plus the d-dimensional nullspace.*

---

<!-- _class: compact -->
# Fixed mu, empirical plug-in, and future joint estimation

| Mean | Meaning | Status |
| --- | --- | --- |
| $\mu=0$ | Centered penalty | Implemented |
| Numeric $\mu\ne0$ | Prespecified mean differences | Implemented |
| $\mu=\operatorname{mean}(D_dy)$ | Observed-difference plug-in | Implemented in fitting and conditional MLE |
| $\widehat\mu(\lambda)$ | Conditional likelihood-optimal mean | Derived, joint method not released |

**Data-derived mu is not automatically a joint maximum-likelihood estimate.**

---

<!-- _class: chapter -->
# III. Deriving the affine estimator

## From the quadratic problem to a reusable matrix

---

<!-- _class: math -->
# Eliminate the reference mean from the penalty

Take $p$ with $D_dp=\mu\mathbf1$ and set $x=\tau-p$.

$$
\widehat x=\arg\min_x
\left\{\|(y-p)-x\|^2+\lambda\|D_dx\|^2\right\}.
$$

The remaining penalty is centered around zero. The shift $p$ is explicitly known.

---

<!-- _class: math -->
# Differentiate the quadratic

With $Q_d=D_d^\top D_d$,

$$
\nabla_x=-2(y-p-x)+2\lambda Q_dx.
$$

Setting $\nabla_x=0$:

$$(I+\lambda Q_d)\widehat x=y-p.$$

Therefore,

$$
\boxed{\widehat\tau_{\lambda,\mu}=p+H_\lambda(y-p),\quad
H_\lambda=(I+\lambda Q_d)^{-1}.}
$$

---

<!-- _class: math -->
# Derivative of the smoothing matrix

From $(I+\lambda Q_d)H_\lambda=I$,

$$Q_dH_\lambda+(I+\lambda Q_d)H_\lambda'=0.$$

Hence

$$\boxed{H_\lambda'=-H_\lambda Q_dH_\lambda.}$$

This exact matrix identity is central to gradients of leverage, residuals and CV.

---

<!-- _class: compact -->
# Meaning of H and its trace

For fixed numeric $\mu$,

$$\widehat\tau=p+H_\lambda(y-p).$$

- $H_\lambda$ is symmetric and positive definite at finite $\lambda$.
- Eigenvalues lie in $(0,1]$.
- Diagonal $h_{ii}$ gives the observation-space leverage.
- Trace $\nu(\lambda)$ is the **conditional effective degrees of freedom**.

If $\mu$ depends on the data, the full fitted-value sensitivity changes.

---

<!-- _class: fig -->
# Weak and strong hat matrices

<div class="pair"><img src="figures/19_hat_weak.svg" alt="small lambda smoothing matrix"/><img src="figures/20_hat_strong.svg" alt="large lambda smoothing matrix"/></div>

*Observation-space H is generally dense, while the spectral attenuation matrix is diagonal.*

---

<!-- _class: chapter -->
# IV. Spectral computation

## The value of precomputing once and reusing many times

---

<!-- _class: math -->
# Diagonalize the penalty

$$D_d=U\Sigma V^\top,\qquad
Q_d=V\operatorname{diag}(\delta_j)V^\top.$$

Then

$$
\boxed{
H_\lambda=V\operatorname{diag}\left(
\frac{1}{1+\lambda\delta_j}\right)V^\top.
}
$$

The eigenvectors do not change when $\lambda$ changes.

---

<!-- _class: fig -->
# The positive penalty spectrum

![width:1030px](figures/17_eigen_spectrum.svg)

*Positive eigenvalues δ_j for a seeded order-two example.*

---

<!-- _class: fig -->
# Attenuation of different spectral modes

![width:1030px](figures/18_attenuation.svg)

*Each mode is multiplied by 1/(1+lambda δ_j).*

---

<!-- _class: math -->
# One projection, many candidate penalties

Compute $c=V^\top(y-p)$ once.

Then

$$
\boxed{
\widehat\tau_{\lambda,\mu}=
p+V\operatorname{diag}(\alpha_j(\lambda))c,
\quad\alpha_j(\lambda)=\frac{1}{1+\lambda\delta_j}.
}
$$

The costly eigensystem is reusable, but reconstructing a full fitted curve still takes matrix–vector operations.

---

<!-- _class: compact -->
# Cost accounting matters

| Computational task | Leading arithmetic cost |
| --- | --- |
| Full SVD setup | $O(n^3)$ |
| Eigenvector storage | $O(n^2)$ |
| Single transformed data projection | $O(n^2)$ |
| Scalar trace / smoothness / spectral GCV | $O(n)$ per candidate |
| Full trend reconstruction | $O(n^2)$ per candidate |
| Pointwise LOOCV leverage | Typically $O(n^2)$ per candidate |

Cost is **not** identical to elapsed wall-clock time.

---

<!-- _class: math -->
# Two cheap scalar identities

For positive-mode coordinates $c_j$ and attenuation $\alpha_j$:

$$
\boxed{\nu(\lambda)
=d+\sum_{j=1}^{n-d}\alpha_j(\lambda).}
$$

$$
\boxed{
\operatorname{RSS}(\lambda)
=\sum_{j=1}^{n-d}(1-\alpha_j(\lambda))^2 c_j^2.
}
$$

These are the inputs for effective degrees of freedom and several classical scalar scores.

---

<!-- _class: fig -->
# Full fitted curves are not scalar trace queries

![width:1030px](figures/44_trace_vs_fit.svg)

*Illustrative arithmetic growth, not measured benchmark times.*

---

<!-- _class: fig -->
# Trace and residual energy as scalar spectral summaries

![width:1030px](figures/29_rss_edf.svg)

*The functions are computed from a reused spectral basis.*

---

<!-- _class: chapter -->
# V. Effective degrees of freedom

## A trace-based interpretation of smoothing intensity

---

<!-- _class: math -->
# What are effective degrees of freedom?

For fixed numerical $\mu$,

$$
\boxed{\nu(\lambda)=\operatorname{tr}(H_\lambda)
=d+\sum_{j=1}^{n-d}\frac{1}{1+\lambda\delta_j}.}
$$

With $d\ge1$, $\nu(0)=n$ and $\nu(\infty)=d$.

For $d=0$, the limiting EDF is zero.

**A data-estimated $\mu$ alters the full fitted-value sensitivity.**

---

<!-- _class: fig -->
# EDF falls with the penalty

![width:1030px](figures/21_edf.svg)

*The infinite-penalty EDF equals d, the unpenalized dimension.*

---

<!-- _class: math -->
# Guerrero's original smoothness index

$$
\boxed{
S_G(\lambda)=1-\frac{\nu(\lambda)}{n}.
}
$$

For order $d>0$, its range is

$$0\le S_G(\lambda)\le\frac{n-d}{n}.$$

Therefore the original denominator-$n$ index **does not reach one** in general.

---

<!-- _class: math -->
# Our normalized smoothness coordinate

$$
\boxed{
S(\lambda)=\frac{n-\nu(\lambda)}{n-d}
=\frac{1}{n-d}\sum_{j=1}^{n-d}
\frac{\lambda\delta_j}{1+\lambda\delta_j}.
}
$$

Now $S(0)=0$ and $S(\infty)=1$.

**Meaning:** average spectral shrinkage in the penalized directions.  
**Not:** confidence, probability of correctness, or forecast accuracy.

---

<!-- _class: fig -->
# A monotone index with exact endpoints

![width:1030px](figures/22_smoothness.svg)

*S ranges from zero to one.*

---

<!-- _class: fig -->
# Original Guerrero smoothness versus normalized smoothness

![width:1030px](figures/23_two_s_indices.svg)

*S_G=(n-d)S/n; the distinction matters when d>0.*

---

<!-- _class: fig -->
# Different d values induce different lambda-to-S maps

![width:1030px](figures/24_s_by_order.svg)

*Equal numerical penalties can yield very different shrinkage.*

---

<!-- _class: fig -->
# Equal S does not make geometries identical

![width:1030px](figures/05_order_comparison.svg)

*A common trace index does not imply identical fits across orders.*

---

<!-- _class: math -->
# Prove the monotone inverse exists

For every finite $\lambda\ge0$,

$$
\boxed{
S'(\lambda)=\frac{1}{n-d}
\sum_{j=1}^{n-d}
\frac{\delta_j}{(1+\lambda\delta_j)^2}>0.}
$$

Every summand is positive on the resolved positive spectrum, so S is strictly increasing and continuous.

Define $\Lambda(s)=S^{-1}(s)$ on $0<s<1$ and extend with $\Lambda(0)=0$, $\Lambda(1)=\infty$.

---

<!-- _class: fig -->
# The first derivative remains positive

![width:1030px](figures/25_s_derivative.svg)

*The derivative is positive but becomes small for very large lambda.*

---

<!-- _class: fig -->
# Derivative with respect to log(lambda)

![width:1030px](figures/26_log_s_derivative.svg)

*Small slopes near both extremes matter for optimization conditioning.*

---

<!-- _class: chapter -->
# VI. Select lambda or select S

## A bounded coordinate for the same statistical problem

---

<!-- _class: math -->
# Reparameterize a criterion without changing it

Let $C(\lambda;\mu)$ denote an existing criterion evaluated at fixed $\mu$.

Write $\Lambda=S^{-1}$ and $\widetilde C(s;\mu)=C(\Lambda(s);\mu)$.

$$
\boxed{
\widehat s\in\arg\min_{s\in[0,1]}\widetilde C(s;\mu),
\quad
\widehat\lambda=\Lambda(\widehat s).
}
$$

Exact global minimizers correspond under this monotone map (ties and undefined endpoints must be treated carefully).

This is **not a newly invented selection criterion**.

---

<!-- _class: fig -->
# Inverse smoothness: bounded S, unbounded penalty

![width:1030px](figures/27_inverse.svg)

*The numerical inverse may cover many orders of magnitude.*

---

<!-- _class: fig -->
# Equal steps in S are uneven in lambda

![width:1030px](figures/28_s_grid.svg)

*A uniform S grid and a log-lambda grid are not the same candidate set.*

---

<!-- _class: fig -->
# The CV objective on the penalty scale

![width:1030px](figures/30_cv_lambda.svg)

*Ordinary fixed-mu LOOCV score as a function of lambda.*

---

<!-- _class: fig -->
# The SAME CV score in the smoothness coordinate

![width:1030px](figures/31_cv_s.svg)

*The statistical score has not been modified.*

---

<!-- _class: fig -->
# The optimum corresponds under S and lambda

![width:1030px](figures/32_cv_minimum.svg)

*Finite candidate grids may still find different local minima.*

---

<!-- _class: math -->
# The chain rule gives the exact derivative

Since $s=S(\lambda)$ and $S'>0$,

$$\frac{d\lambda}{ds}=\frac{1}{S'(\lambda)}.$$

Therefore,

$$
\boxed{
\frac{d\widetilde C}{ds}
=\frac{C'(\lambda)}{S'(\lambda)}
=\frac{dC/d\log\lambda}{dS/d\log\lambda}.
}
$$

Interior derivative zeros occur at the same fitted trends.  
**Near S=0 or S=1 the denominator can be tiny.**

---

<!-- _class: math -->
# The stable log-penalty derivative of S

$$
\boxed{
\frac{dS}{d\log\lambda}
=\frac{1}{n-d}
\sum_{j=1}^{n-d}
\frac{\lambda\delta_j}{(1+\lambda\delta_j)^2}>0.
}
$$

Classical CV already has an analytical derivative in the library.

For S-based CV search, evaluate the chain-rule quotient and compare multiple stationary candidates and exact boundaries.

**Neither numerical search is globally certified.**

---

<!-- _class: small -->
# What the public selector supports

| Argument | Meaning |
| --- | --- |
| search_space="lambda" | Original default, search penalties |
| search_space="smoothness" | Search normalized S in [0,1] |
| criterion="cv", method="auto" | Analytical multi-candidate derivative search |
| GCV/AICc/BIC/MLE, method="auto" | Grid search in chosen coordinate |
| Explicit grid | Interpreted in chosen coordinate |
| Result grid | Always the evaluated lambda values |
| Result search_grid | Values in requested search coordinate |

---

<!-- _class: code -->
# Try both coordinates in Python

~~~python
from trendestimation import TrendSmoother, select_lambda
solver = TrendSmoother(len(y), order=2)

default = select_lambda(
    solver, y, criterion="cv", mu=0.0,
    search_space="lambda",
)
bounded = select_lambda(
    solver, y, criterion="cv", mu=0.0,
    search_space="smoothness",
)

print(default.lambda_, default.smoothness)
print(bounded.lambda_, bounded.smoothness)
~~~

---

<!-- _class: code -->
# Explicit grid of normalized smoothness levels

~~~python
selected = select_lambda(
    solver, y, criterion="gcv", mu=0.0,
    search_space="smoothness",
    grid=[0, .25, .50, .75, 1],
)

selected.lambda_       # fitted penalty
selected.smoothness    # achieved normalized index
selected.grid          # evaluated penalties
selected.search_grid   # input S coordinates
selected.scores        # unchanged criterion values
~~~

---

<!-- _class: compact -->
# Why a bounded interval is not automatically faster

- Each interior S requires solving S(lambda)=s.
- Several scalar spectral evaluations can be needed per inverse.
- The chain-rule derivative can become sensitive in the tails.
- Uniform S and log-lambda grids cover **different finite candidates**.
- More optimizer evaluations can erase the advantages of an interpretable coordinate.

**No actual end-to-end runtime improvement has been established for optimizing over S.**

---

<!-- _class: chapter -->
# VII. Statistical selection criteria

## What gets minimized and how its derivative arises

---

<!-- _class: math -->
# Ordinary leave-one-out CV

Let $e=y-\widehat\tau$, $h_{ii}=(H_\lambda)_{ii}$ with **fixed numeric $\mu$**.

$$
\boxed{
\mathrm{CV}(\lambda)=
\frac1n\sum_i\left(\frac{e_i}{1-h_{ii}}\right)^2.
}
$$

At lambda=0, $H=I$ and the shortcut has zero denominators.

This is **not chronological or rolling-origin forecast validation**.

---

<!-- _class: fig -->
# The leverage of each observation

![width:1030px](figures/35_leverage.svg)

*GCV replaces individual leverages by their mean.*

---

<!-- _class: fig -->
# Training residuals vs leave-one-out residuals

![width:1030px](figures/36_loo_residuals.svg)

*e_i^(-i)=e_i/(1-h_ii), provided mu and the penalty are fixed.*

---

<!-- _class: math -->
# Analytical derivative of classical CV

Set $a_i=e_i$ and $b_i=1-h_{ii}$. From $H'=-HQH$,

$$a'=HQH(y-p),\qquad b_i'=(HQH)_{ii}.$$

Then

$$
\boxed{
\mathrm{CV}'(\lambda)=\frac2n
\sum_i \frac{a_i}{b_i}
\frac{a_i'b_i-a_ib_i'}{b_i^2}.
}
$$

**This is an analytical derivative, not a closed-form optimal lambda.**

---

<!-- _class: math -->
# GCV, AICc, BIC: implemented conventions

With $R=\mathrm{RSS}$ and $\nu=\operatorname{tr}(H_\lambda)$:

$$
\boxed{\mathrm{GCV}=\frac{R/n}{(1-\nu/n)^2}.}
$$

$$
\boxed{\mathrm{AICc}=\log(R/n)+\frac{2\nu+1}{n-\nu-2}.}
$$

$$
\boxed{\mathrm{BIC}=\log(R/n)+\frac{\nu\log n}{n}.}
$$

Admissible domains matter; AICc conventions vary across the literature.

---

<!-- _class: fig -->
# All four scores as functions of lambda

![width:1030px](figures/33_criteria.svg)

*Profiles centered and rescaled only for the plot. Real selection uses original units.*

---

<!-- _class: fig -->
# Different criteria yield different in-sample trends

![width:1030px](figures/34_selected_trends.svg)

*A single seeded example does not establish an overall ranking.*

---

<!-- _class: fig -->
# LOOCV versus chronological holdout

![width:1030px](figures/37_chronological_split.svg)

*Future-horizon forecasting requires a different experimental design.*

---

<!-- _class: chapter -->
# VIII. Gaussian marginal likelihood

## Conditional MLE is implemented; joint mu profiling is future work

---

<!-- _class: math -->
# The Gaussian stochastic model

$$
y=\tau+\varepsilon,\qquad
\varepsilon\sim N(0,\sigma_\varepsilon^2 I).
$$

$$
D_d\tau-\mu\mathbf1\sim N(0,\sigma_\eta^2 I),
\qquad
\boxed{\lambda=\frac{\sigma_\varepsilon^2}{\sigma_\eta^2}.}
$$

This is a **model-based interpretation**, not a property of arbitrary distributions.

The unpenalized polynomial coordinates are treated as nuisance trend components.

---

<!-- _class: math -->
# Conditional Gaussian marginal likelihood

Set $r=n-d$, $w_j(\lambda)=\lambda\delta_j/(1+\lambda\delta_j)$ and $z_j=v_j^\top(y-p_\mu)$.

The profile score, up to constants, is

$$
\boxed{
L(\lambda;\mu)=
r\log\left(\frac1r\sum_{j=1}^r w_jz_j^2\right)
-\sum_{j=1}^r\log w_j.
}
$$

It profiles observation variance and selects $\lambda$ for fixed or plug-in $\mu$.

---

<!-- _class: fig -->
# Conditional marginal-likelihood score

![width:1030px](figures/38_mle_profile.svg)

*Gaussian model-based score, not cross-validation.*

---

<!-- _class: math -->
# The analytical conditional likelihood mean

Let $p_t^{(1)}=\binom td$, $z_j=v_j^\top y$ and $b_j=v_j^\top p^{(1)}$.

For fixed positive $\lambda$,

$$
\boxed{
\widehat\mu(\lambda)=
\frac{\sum_jw_j(\lambda)b_jz_j}
{\sum_jw_j(\lambda)b_j^2}.
}
$$

A nonzero denominator follows from the positive-subspace model assumptions.

**This formula is retained as a deferred research result, not a validated joint API.**

---

<!-- _class: fig -->
# The optimal conditional mean can depend on lambda

![width:1030px](figures/39_mu_profile.svg)

*Derived profile formula; no joint numerical optimizer is claimed.*

---

<!-- _class: math -->
# A future scalar optimization of both lambda and mu

Rather than optimizing two variables numerically, insert the conditional optimum into the likelihood:

$$
\boxed{
\widehat\lambda=
\arg\min_{\lambda>0}J(\lambda;\widehat\mu(\lambda)).
}
$$

**Open problems:** identifiability, boundary optima, numerical stability, inference and a fair comparison against conditional MLE.

This extension is not yet experimentally validated in the library.

---

<!-- _class: fig -->
# Visualize the analytical joint-likelihood surface

![width:1030px](figures/40_joint_mle_surface.svg)

*Analytical schematic based on derived formula, not a released joint estimator.*

---

<!-- _class: math -->
# Joint profiling could also use bounded S

With $\Lambda(s)=S^{-1}(s)$,

$$
\boxed{
\widehat s_{\mathrm{joint}}=
\arg\min_{0<s<1}
J\big(\Lambda(s);\widehat\mu(\Lambda(s))\big).
}
$$

Then $\widehat\lambda_{\mathrm{joint}}=\Lambda(\widehat s_{\mathrm{joint}})$.

This **changes coordinates only**; the joint estimation problem still requires implementation and validation.

---

<!-- _class: compact -->
# What is currently implemented versus future

| Functionality | Research status |
| --- | --- |
| Fixed mu PLS fitting | Implemented |
| Observed-difference mu plug-in | Implemented |
| Conditional Gaussian MLE | Implemented |
| Conditional MLE search in S | Implemented |
| Analytical $\widehat\mu(\lambda)$ | Mathematical derivation |
| Joint $(\lambda,\mu)$ solver | Not yet implemented |
| Confidence intervals for joint estimates | Not yet validated |
