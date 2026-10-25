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
