# Mathematical annotations — third-difference mean, units, evidence

**Status:** Independent algebraic deductions for Paper C, checked against the exact estimator in the current repository. These are *our deductions*, not claims made by Fan, Marczak, Cao, Zhu or Tang.

## 1. Model and physical interpretation

For sample length $n>3$, equispaced sampling interval $\Delta t$, position in meters and forward-difference operator $D_3$:

$$
\widehat\tau_{\lambda,\mu}
=\underset{\tau}{\operatorname*{arg\,min}}\;
\|y-\tau\|_2^2+\lambda\|D_3\tau-\mu\mathbf1\|_2^2 .
$$

The discrete third derivative proxy is $j_i=(D_3\tau)_i/(\Delta t)^3$, so the penalty is

$$
\lambda(\Delta t)^6\sum_{i=1}^{n-3}
\left(j_i-\frac{\mu}{(\Delta t)^3}\right)^2.
$$

Consequently $j_{\rm ref}=\mu/(\Delta t)^3$ has physical units m/s³. $\mu=0$ shrinks toward zero jerk; $\mu\ne0$ shrinks toward a **constant nonzero reference jerk**. “Minimum jerk” (center zero) and “minimum departure from reference jerk” (center nonzero) are not the same physical hypothesis.

The unconstrained quadratic problem has the unique finite-$\lambda$ solution

$$
\widehat\tau_{\lambda,\mu}
=H_\lambda y+\lambda\mu H_\lambda D_3^\top\mathbf1,
\quad
H_\lambda=(I+\lambda D_3^\top D_3)^{-1}.
$$

It does **not** constrain measured velocity, acceleration, or jerk to any physical interval.

## 2. Exact affine equivalence and limiting trend

Set $p_{\mu,i}=\mu\binom{i-1}{3}$, for $i=1,\ldots,n$, so that $D_3p_\mu=\mu\mathbf1$. Then

$$
\widehat\tau_{\lambda,\mu}
=p_\mu+H_\lambda(y-p_\mu).
$$

This is exactly zero-reference Whittaker–Henderson smoothing applied to $y-p_\mu$, followed by restoring $p_\mu$. It is a useful model representation but not a new smoothing family.

At maximal conditional smoothing ($\lambda\to\infty$):
- $\mu=0$: $D_3\tau=0$, so the limiting fit is **quadratic** (degree at most 2).
- fixed $\mu\ne0$: $D_3\tau=\mu\mathbf1$, so the limiting fit is generally **cubic** (degree 3).

For equal $n,d,\lambda$, the difference between the two fits is

$$
\widehat\tau_{\lambda,\mu}-\widehat\tau_{\lambda,0}
=\mu(I-H_\lambda)p_1,\qquad
D_3p_1=\mathbf1.
$$

Thus a forecast difference may arise from both the fitted historical trend and the explicit cubic term in its local continuation.

## 3. Critical endpoint identity of the training-derived mean

Our current code uses $\widehat\mu=\operatorname{mean}(D_3y)$. Because the third difference is the first difference of the second difference, the sum telescopes:

$$
\boxed{
\widehat\mu
=\frac1{n-3}\sum_{i=1}^{n-3}(D_3y)_i
=\frac{(D_2y)_{n-2}-(D_2y)_1}{n-3}.
}
$$

**Therefore the average of all third differences only depends on six boundary position values (for $n\ge6$)**, not on the interior of the trajectory. A statistical argument saying “averaging 77 third differences makes this stable” is misleading: the terms are heavily dependent and cancel algebraically.

If $y=x+\varepsilon$ with **independent, identically distributed** zero-mean position errors of variance $\sigma^2$ and $n\ge6$, the two endpoint second differences are disjoint, each has error variance $6\sigma^2$. Hence

$$
\operatorname{Var}(\widehat\mu)=\frac{12\sigma^2}{(n-3)^2},
\qquad
\operatorname{Var}(\widehat j_{\rm ref})
=\frac{12\sigma^2}{(n-3)^2(\Delta t)^6}.
$$

This is a *conditional toy noise model*. NGSIM camera tracking errors may be temporally correlated and systematic; it is **not** an estimated error variance for these observations.

At $n=80$, the estimator divides a difference of endpoint accelerations by 77; at $\Delta t=0.1$ seconds, converting to physical jerk multiplies by $1000$. Report the resulting reference-jerk distribution and sensitivity to perturbations of the first and final three positions.

## 4. Data-dependent effective degrees of freedom

For a **fixed** numeric $\mu$, the data derivative of the smoother is $H_\lambda$ and conditional EDF is $\operatorname{tr}(H_\lambda)$. But plug-in $\widehat\mu=c^\top y$ with
$c^\top=\mathbf1^\top D_3/(n-3)$ changes the map to

$$
\widehat\tau=
\{H_\lambda+(I-H_\lambda)p_1c^\top\}y.
$$

The full Jacobian (hat matrix) thus includes a **rank-one correction**; its trace is generally not the fixed-$\mu$ trace. Standard CV computed while freezing the estimated mean is **conditional** and does not reproduce truly re-estimated leave-one-out fits. Mention this explicitly in results, criteria comparisons and future inference.

The normalized smoothness coordinate $S_d(\lambda)$ itself depends only on the penalty spectrum, and is therefore still the same for a fixed $(n,d,\lambda)$; interpreting it as the data-adaptive procedure's effective degrees of freedom requires the correction above.

## 5. How to evaluate jerk correctly

1. In **synthetic** position trajectories, construct known $x(t)$, acceleration and $j(t)$, then add documented observation errors. Evaluate historical **jerk RMSE in m/s³**, position RMSE in meters and future position RMSE separately.
2. In **real NGSIM**, there is no independent jerk truth in the current archive. Report plausibility diagnostics (threshold exceedance, jerk sign changes, acceleration variability), but never claim that smaller jerk amplitude proves smaller *jerk estimation error*.
3. Hold every forecast timestamp strictly after the training cutoff and fit any $\mu$, scaler or selector using training data alone.
4. Evaluate zero-reference, plug-in reference, robust reference and at least one external physically constrained competitor with the **same time grids, physical units and held-out vehicles**.

These steps distinguish physical correctness, parameter interpretability, predictive usefulness and computational efficiency. They are not interchangeable claims.
