# Exact fit-versus-continuation decomposition for \(d=3\)

**Status:** Mathematical derivation for the *actual* strategy in \`run_case.py::continuation\`. This is a useful exact algebraic identity under a fixed selected smoothing penalty, **not** evidence of forecast benefit or a historically novel theorem.

## Assumptions and notation

- \(y\in\mathbb R^n\): observed **training** longitudinal positions, equally spaced.
- \(D=D_3\), \(\lambda\ge0\), \(H=(I+\lambda D^\top D)^{-1}\).
- \(q_i=\binom{i}{3}\) for \(i=0,\ldots,n-1\), so \(Dq=\mathbf1\), and \(q_f\) is the same polynomial evaluated at future integer indices \(i=n,\ldots,n+h-1\).
- \(\mu\): a scalar treated as fixed **during the fit**. It may have been estimated from training \(y\) beforehand.
- \(L:\mathbb R^n\rightarrow\mathbb R^h\): the **linear** map formed by fitting a degree-2 polynomial to the final \(k=25\) points of its argument and extrapolating that polynomial to the next \(h\) times. This map has no access to future observed \(y\). The actual code uses \`numpy.polynomial.Polynomial.fit(...,deg=2)\` and a fixed window.

The conditional PLS fit is

\[
\widehat\tau_\mu
=\mu q+H(y-\mu q)
=Hy+\mu(I-H)q.
\tag{1}
\]

For **any** historical fitted trend \(z\), define a continuation with reference \(\nu\) by

\[
\mathcal E_\nu(z)=L(z-\nu q)+\nu q_f
=Lz+\nu(q_f-Lq).
\tag{2}
\]

The current implementation always sets the continuation reference \(\nu=\mu\) used in the fit. **For diagnosis only**, they can be varied independently.

## Proposition — what actually changes the forecast

Combining (1) and (2),

\[
\boxed{
F_{\mu,\nu}(y)
=\mathcal E_\nu(\widehat\tau_\mu)
=LHy+\mu L(I-H)q+\nu(q_f-Lq).
}
\tag{3}
\]

In particular,

\[
\boxed{
F_{\mu,\mu}(y)=LHy+\mu(q_f-LHq).
}
\tag{4}
\]

Subtract the zero-reference forecast:

\[
F_{\mu,\mu}(y)-F_{0,0}(y)
=\underbrace{\mu L(I-H)q}_{\text{historical smoothing effect}}
+\underbrace{\mu(q_f-Lq)}_{\text{continuation reference effect}}.
\tag{5}
\]

This is an **exact additive decomposition for fixed \(S\), \(\lambda\), the same linear map \(L\), the same input \(y\), and a single fixed numerical \(\mu\)**. A 2×2 counterfactual experiment can identify both components directly.

### Four controlled cells

| Fitting reference | Continuation reference | Mathematical output | Status in current code |
| --- | --- | --- | --- |
| 0 | 0 | \(F_{0,0}=LHy\) | Implemented |
| \(\mu\) | 0 | \(F_{\mu,0}=LHy+\mu L(I-H)q\) | **Proposed diagnostic** |
| 0 | \(\mu\) | \(F_{0,\mu}=LHy+\mu(q_f-Lq)\) | **Proposed diagnostic** |
| \(\mu\) | \(\mu\) | \(F_{\mu,\mu}=LHy+\mu(q_f-LHq)\) | Implemented |

**Do not describe the crossed counterfactual cells as physical forecasting models by default**; they are attribution controls. For fixed \(S\), the two effects add exactly and the arithmetic 2×2 interaction is zero. If an independently selected \(S\) or \(\mu\) changes across the four cells, that statement no longer holds without adjustment.

The exact formula also shows that at **\(S=0\)**, \(H=I\): the historical smoothing effect is zero, yet a nonzero continuation \(\mu\) can still alter the extrapolation. This is a critical control for an apparent forecasting improvement that has **nothing** to do with improved smoothing.

At the **infinite-smoothing limit**, the historical fit lies in the affine space \(D\tau=\mu\mathbf1\), and the continuation reproduces the corresponding quadratic-plus-cubic polynomial exactly (up to floating-point rounding) whenever the local fitting window has at least three distinct times.

## What changes when \(\widehat\mu=c^\top y\)

The full forecast map for the *training-only raw mean* is linear in \(y\) conditional on \(\lambda\):

\[
F_{\widehat\mu,\widehat\mu}(y)
=\left\{LH+(q_f-LHq)c^\top\right\}y,\quad
c^\top=\frac{\mathbf1^\top D}{n-3}.
\tag{6}
\]

The plug-in fit map itself is \(H+(I-H)qc^\top\) and its full effective degrees of freedom are **not** \(\mathrm{tr}(H)\). If \(\mu\) is instead estimated with robust regression, the map need not be linear, and the same simple Jacobian formula is not valid.

**Interpretational limit:** The equality above assumes **fixed \(\lambda\)**. In the actual archived pilot the chosen \(\lambda\) comes from a selector which may depend on \(\mu\); matching the numerical \(S\) across counterfactual conditions is required to isolate effects. This is a new analysis design, not an attempt to replace the existing stored predictions.

## Minimal reproducibility tests for a future implementation

1. Verify \(D_3q=\mathbf1\) for \(n=80\) and \(q_i=\binom i3\).
2. For several fixed \(S\), \(\mu\in\{0,\pm 10^{-3}\}\), and deterministic \(y\), check (1) against the normal equations and (4) against the existing \`continuation\`.
3. Check the 2×2 additivity: \(F_{\mu,\mu}-F_{\mu,0}-F_{0,\mu}+F_{0,0}\approx0\) with a scale-aware float64 tolerance.
4. Check \(S=0\) (fitting effect 0) and \(S=1\) (exact polynomial continuation), including near-boundary \(S\approx1\).
5. Preserve actual raw/estimated \(\mu\), selected \(S\), code SHA, and all four forecasts; compare against recorded future positions **only after** parameters have been chosen on training data.

Do not label these mathematical checks as results of experiment001 unless the tests and their recorded outputs have actually been run and archived.
