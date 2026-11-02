# Theorem and claim audit — direct spectral-weight theory paper

Scope: exact unweighted quadratic PLS on equally indexed forward
differences, integer 1<=d<n, full row rank r=n-d, fixed s and
either fixed mu or the explicitly defined empirical plug-in.

## Verified derivations

- Rank(D_d)=n-d: first n-d columns triangular with diagonal (-1)^d.
  Nullspace dimension d, basis discrete polynomial degree <d.
- p_mu[i]=mu*binom(i-1,d) obeys D_d p_mu=mu*1.
- Positive definite normal equations for every finite lambda.
  H=(I+lambda D.T D)^-1 and affine fixed-mu result.
- Thin SVD U Sigma V.T, positive sigma. Spectral coefficients
  w=lambda*delta/(1+lambda*delta), H=I-V diag(w) V.T.
  Conditional EDF=tr H=n-sum_j w_j.
- Normalized s=(sum w_j)/(n-d) maps [0,infty] bijectively to [0,1].
- Odds characterization: w/(1-w)/delta is a common positive scalar
  iff the weights correspond to a single quadratic penalty.
- Direct weight representation w_j=expit(x+log(delta_j/delta_star)).
  Unique real root mean(w)=s with bracket
  logit(s)-max(alpha) <= x <= logit(s)-min(alpha).
  x=log(lambda)+log(delta_star) in exact arithmetic.
- Shift-free trend y-V[w*(V.T y) - mu*(w/sigma)*(U.T 1)].
  At s=1 this is the Euclidean projection onto D tau=mu*1;
  at s=0 the fit equals y.
- For s in (0,1), let b_j=w_j(1-w_j), B=mean(b).
  d w_j/ds=b_j/B, 0<b_j/B<=r.
  Norm bound ||tau_s-tau_t||<=r |s-t| ||c_mu||.
- G'(x)=s(1-s)-Var_j(w_j) and dx/ds=1/G'(x).
  Scalar inverse remains poorly conditioned at endpoints.
- With mu_hat=(1/r) 1.T D y, let g=D.T 1/r and
  b_s=V diag(w/sigma) U.T 1. Full linear map is
  T_s=(I-V diag(w)V.T)+b_s g.T.
  trace T_s=n-rs+(1/r) sum_j w_j (U.T 1)_j^2.
  Since ||U.T 1||^2=r, correction in [0,1].
  At s=1 full-data EDF=d+1 (vs conditional d).
  For r=1 and plug-in mu=Dy, objective is minimized
  by tau=y for all s; EDF=n.
- For approximate scalar x, s_tilde=mean(w(x));
  computed trend is exact tau(s_tilde) in exact arithmetic,
  hence ||error||<=r |s_tilde-s| ||c_mu||.

## Conditions NOT established

1. Stability of computed singular vectors/eigenvalues at d=5/6
   and extreme n, beyond existing finite tests.
2. Runtime superiority versus a stable cached log-lambda implementation.
3. Independent multiprecision verification of all weight-inversion
   implementations and full end-to-end adaptive selection.
4. Generality to irregular grids, weighted regression, or l1 penalties.
5. Unconditional EDF when s is estimated adaptively from y.
6. Novelty relative to all older degrees-of-freedom-controlled
   spline and constrained spectral filtering algorithms.

## Source provenance

- main branch src/trendestimation/smoothness_weights.py and tests/
  test_spectral_smoothness_weights.py.
- notes/direct_spectral_weights.md and notes/
  smoothness_parameterization.md.
- paper/csda-spectral-smoothness/ and
  paper/csda-computational-costs/ theoretical sections.
- User-provided original PDFs of Guerrero 2007, Cortes-Toto 2017,
  Weinert 2007, and Biessy 2026 were inspected locally, but
  are not copied to this public repository.
- Original R stats::smooth.spline documentation explicitly accepts df,
  desired equivalent degrees of freedom; cited as prior art.

All results are proved in the new manuscript's .tex sources.
