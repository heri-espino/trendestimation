# Parameter selection in normalized smoothness coordinates

## 1. Question and setting

**Question.** Can we search over a bounded, interpretable smoothness index
\(s\in[0,1]\), rather than directly over the PLS penalty
\(\lambda\in[0,\infty]\), without changing the mathematical estimator or
its selection criteria?

This note describes a **reparameterization of established finite-difference
penalized least squares**, not a new statistical smoothing criterion. It
underlies the optional \`search_space="smoothness"\` parameter of
\`trendestimation.select_lambda\`. The default \`"lambda"\` space is
unchanged.

For \(n\) equally spaced observations, integer \(0\le d<n\), fixed
numerical difference mean \(\mu\), and \(\lambda\ge0\), define

\[
\widehat\tau_{\lambda,\mu}
=\arg\min_{\tau\in\mathbb R^n}
\left\{\|y-\tau\|_2^2+
\lambda\|D_d\tau-\mu{\bf1}\|_2^2\right\}.
\]

Let \(Q_d=D_d^\top D_d\), \(r=n-d\), and let
\(\delta_1,\ldots,\delta_r>0\) be its positive eigenvalues
(\(d=0\) gives \(Q_0=I_n\)). The \(d\) other eigenvalues are zero
when \(d\ge1\). Write
\(H_\lambda=(I+\lambda Q_d)^{-1}\).

## 2. The normalized coordinate and its derivative

The fixed-\(\mu\) effective degrees of freedom and normalized
trace-based smoothness are

\[
\nu(\lambda)=\operatorname{tr}(H_\lambda)
=d+\sum_{j=1}^{r}\frac1{1+\lambda\delta_j},
\quad
S(\lambda)=\frac{n-\nu(\lambda)}{r}
=\frac1r\sum_{j=1}^{r}
\frac{\lambda\delta_j}{1+\lambda\delta_j}.
\]

**Proposition (monotone bijection).** Provided all the \(r\) penalized
eigenvalues are positive, \(S\) is continuous and strictly increasing
on \([0,\infty)\), with \(S(0)=0\) and
\(\lim_{\lambda\to\infty}S(\lambda)=1\).

**Proof.** For every finite \(\lambda\ge0\),

\[
S'(\lambda)=\frac1r
\sum_{j=1}^{r}\frac{\delta_j}{(1+\lambda\delta_j)^2}>0.
\]

Each summand is continuous and increases from zero to one as a
contribution to \(S\), proving the assertions. Thus the extended
inverse \(\Lambda(s)=S^{-1}(s)\) exists for \(s\in(0,1)\) and is
defined by \(\Lambda(0)=0,\ \Lambda(1)=\infty\). \(\square\)

The log-penalty derivative, which is numerically useful, is

\[
\frac{dS}{d\log\lambda}
=\lambda S'(\lambda)
=\frac1r\sum_{j=1}^{r}
\frac{\lambda\delta_j}{(1+\lambda\delta_j)^2}>0
\quad(\lambda>0).
\]

For \(d>0\), Guerrero's original scale \(S_G=1-\nu/n\) has maximum
\(r/n<1\); **all smoothness-space searches here use the normalized
scale \(S\)**, not \(S_G\).

## 3. Reparameterizing any existing criterion

Let \(C(\lambda;\mu)\) be an existing *fixed-\(\mu\)* score: CV, GCV,
AICc, BIC, or the Gaussian marginal profile-likelihood score conditional
on \(\mu\). Define

\[
\widetilde C(s;\mu)=C(\Lambda(s);\mu),\qquad s\in[0,1].
\]

Then **the set of global minimum penalties is the same** under either
coordinate, when both optimizations search the same complete domain:

\[
\arg\min_{s\in[0,1]}\widetilde C(s;\mu)
=S\!\left(\arg\min_{\lambda\in[0,\infty]}C(\lambda;\mu)\right).
\]

The equality is set-valued if there are ties; an undefined score
(e.g. LOOCV or MLE exactly at \(\lambda=0\)) must remain excluded, not
silently assigned a finite value. Reparameterization alone does **not**
prove faster execution, better statistical accuracy, uniqueness of the
optimum, or global convergence of a finite numerical search.

An important practical distinction: equal numerical \(\lambda\) across
different \(d\) does not mean equal smoothness. Equal \(s\) means the same
*normalized conditional trace index*, not identical fitted geometry.

## 4. Chain rule and CV derivative

For any differentiable criterion on the interior, the inverse-function
theorem yields

\[
\boxed{\frac{d\widetilde C}{ds}
=\frac{C'(\lambda)}{S'(\lambda)}
=\frac{dC/d\log\lambda}{dS/d\log\lambda},
\qquad\lambda=\Lambda(s).}
\]

Thus interior stationary points correspond exactly: the denominator is
strictly positive. For classical fixed-\(\mu\) LOOCV, the library already
computes \(d\,\mathrm{CV}/d\log\lambda\) analytically, avoiding
finite differences of the objective. The smoothness-space derivative
uses the displayed quotient. Numerically, solving for sign changes
can equally use the original log-penalty derivative because multiplying
by a strictly positive factor does not change its zeros.

The derivative transformation can become poorly conditioned near
\(s=0\) or \(s=1\). In particular,
\(dS/d\log\lambda\to0\) at both extremes; the code must not divide
by zero or assume that a bounded domain guarantees good conditioning.

## 5. The Gaussian profile-likelihood research direction

For the separately derived *joint* Gaussian profile proposal
(not implemented by this change), let
\(p^{(1)}_t=\binom{t}{d}\),
\(z_j=v_j^\top y\), \(b_j=v_j^\top p^{(1)}\), and
\(w_j(\lambda)=\lambda\delta_j/(1+\lambda\delta_j)\).
The conditional closed-form mean is

\[
\widehat\mu(\lambda)
=\frac{\sum_j w_j(\lambda)b_jz_j}
{\sum_j w_j(\lambda)b_j^2}.
\]

Its hypothetical joint profiled objective can also be written

\[
\widehat s
=\arg\min_{s\in(0,1)}
J\big(\Lambda(s),\widehat\mu(\Lambda(s))\big),
\qquad
\widehat\lambda=\Lambda(\widehat s).
\]

The envelope theorem applies to an interior, uniquely selected
conditional optimum and differentiable likelihood:
\(J_{\rm prof}'(\lambda)
=\partial_\lambda J(\lambda,\widehat\mu(\lambda))\).
This is **not** how the current public \`select_lambda\` estimates
\(\mu\): it continues to use a fixed numeric mean, or the established
observed-difference plug-in for conditional MLE. In particular, this
change does **not** add joint \((\lambda,\mu)\) optimization.

## 6. Numerical design and boundary cases

- Preserve \`search_space="lambda"\` as the default to maintain the
  existing penalty grid and default analytical CV behavior.
- When \`search_space="smoothness"\`, interpret an explicit
  \`grid\` as *normalized smoothness* values in \([0,1]\);
  preserve input order and duplicates. Internally invert each via
  \`TrendSmoother.lambda_for_smoothness\`, then evaluate the **same**
  score in penalty coordinates. \`SelectionResult.grid\` continues
  to store the evaluated penalties for backward compatibility;
  \`search_grid\` records the actual grid in the requested coordinate.
- The default smoothness grid spans the bounded interval and includes
  both exact endpoints. For CV, the analytical search scans interior
  values, isolates sign changes and refines candidate minima; the
  endpoints are always evaluated too. This is not proof of global
  optimality for arbitrary pathological score functions.
- Exact \(s=0\) and \(s=1\) correspond to \(\lambda=0\) and
  \(\lambda=\infty\). CV and MLE retain their original treatment
  of inadmissible zero-penalty scores.
- Very extreme interior \(s\) can require a penalty outside float64.
  The inverse explicitly reports this rather than falsely returning
  an endpoint.
- Conditional smoothness and EDF assume \(\mu\) fixed. The
  \`mu="data"\` plug-in is not the same as re-estimating the mean for
  every omitted observation.

## 7. Reproducibility checks

Compare equal candidate grids under both representations:
\`grid_lambda=[0, 1, 10, inf]\` against
\`grid_s=[S(0), S(1), S(10), S(inf)]\`. Penalties and
scores should coincide within inversion tolerance, including
boundaries, repeated points, and a nonzero fixed \(\mu\).
For CV test independent finite-difference derivatives in
the \(s\) coordinate, multiple stationary minima, deterministic
results, and limiting cases. Validate \`mle\` with
\`mu="data"\` **only as a conditional plug-in**, and test
invalid smoothness targets independently from negative penalties.

## 8. References and scope

- Whittaker (1923), graduation and penalized differences.
- Guerrero (2007, 2008), difference penalties and attained smoothness.
- Cortés-Toto, Guerrero, and Reyes (2017), classical selection criteria.
- Biessy (2026), modern likelihood interpretations of
  Whittaker–Henderson smoothing.

This is a mathematical/reproducibility note, not a claim of
improved measured runtimes or forecast skill. The separate Springer
*Computational Statistics* manuscript keeps its bounded, fixed-mean
computational focus unless an independently justified paper revision
is made.
