# Experiment007 theoretical note — what is mu='data'?

This note derives three distinct interpretations of the reference mean
of finite differences. It accompanies the actual observed-mu
Experiment007 benchmark and is **not** a production API redesign.

Let y in R^n be observed, tau in R^n latent, d>=1, m=n-d,
D=D_d in R^{m*n}, Q=D.T D, b=D.T 1_m and
A=I+lambda Q. For a fixed scalar mu:

    tau_hat(mu) = A^-1 (y + lambda*b*mu).

## 1. Fixed numeric mu

For a prescribed constant mu, the conditional smoothing matrix is
H=A^-1, with EDF_cond=tr(H) and normalized smoothness

    S_cond=(n-tr(H))/(n-d) in [0,1].

These are the existing library conventions. They do NOT account for
the degrees of freedom consumed when the mean is estimated from y.

## 2. Plug-in observed-difference mean, mu='data'

The actual public library computes

    mu_hat_data = mean(D*y) = (b.T*y)/m.

For y=tau_true+epsilon with E[epsilon]=0 and deterministic tau_true,

    E[mu_hat_data] = mean(D*tau_true).

The unknown true-trend mean remains an **oracle quantity** in synthetic
experiments; it cannot be directly calculated on real observations.
The Experiment007 benchmark recomputes mu_hat_data independently for
every series and never supplies oracle mu_true to a competitor.

### Telescoping and endpoint-noise amplification

Write delta as the forward-difference operator. Since
delta^d = delta(delta^(d-1)),

    sum_{t=0}^{m-1} (delta^d y)_t
      = (delta^(d-1) y)_m - (delta^(d-1) y)_0.

Thus the plug-in mean depends ONLY on the first d and last d
observations; interior differences telescope away.

Under independent homoskedastic noise Var(epsilon_t)=sigma^2,
and n>=2*d (so the two endpoint blocks do not overlap),

    Var(mu_hat_data - mu_true)
      = (2*sigma^2/(n-d)^2) * binom(2*d-2,d-1).

The coefficient multiplying sigma^2/(n-d)^2 is:
d=1:2; d=2:4; d=3:12; d=4:40; d=5:140; d=6:504.

Consequently, for comparable m, the d=6 plug-in mean can have
roughly 252 times the noise VARIANCE of the d=1 plug-in mean
(about 15.87 times the standard deviation). This is a theoretical
iid-noise statement; AR/noise heteroskedasticity changes the variance.
It is a real issue for the proposed "all d and mu!=0" research agenda.

### The actual data-dependent fitted smoother

Substitution gives

    tau_hat_data = K_lambda*y,
    K_lambda = H + (lambda/m) * (H*b)*b.T.

K is a (generally NON-symmetric) linear operator, because
H*b and b are not necessarily parallel. Its Jacobian/trace is

    EDF_data(lambda)
      = tr(H) + (lambda/m)*b.T*H*b.

For lambda->infinity the trace tends to d+1 (assuming n>d+1),
not d, because the estimated mean introduces one more
unpenalized limiting polynomial degree. In contrast
EDF_cond(infinity)=d.

This means the existing S_cond still provides an interpretable,
mu-independent **conditional penalty coordinate**, but it is not
the effective normalized degrees-of-freedom reduction of the
complete y->tau_hat_data procedure. A new data-derived smoothness
normalization requires a separate, explicitly defined theory.

Crucially, classical leave-one-out PRESS corrections based on fixed
mu must not be called exact leave-one-out re-estimation of mu_data;
the refitting rule for the empirical mean must be specified first.

## 3. Jointly optimized mean of the ESTIMATED trend differences

If the intended definition is literally

    mu_joint = mean(D*tau_hat)

and mu is optimized JOINTLY with tau, then the objective is

    min_{tau,mu} ||y-tau||^2 + lambda*||D*tau-mu*1||^2.

For fixed tau, minimizing in mu yields
mu_hat(tau)=1.T D*tau/m. Define the centering projector

    P=I_m - 1_m*1_m.T/m.

Profiling mu out produces the DIFFERENT PLS problem

    min_tau ||y-tau||^2+lambda||P D*tau||^2.

Thus its penalty is Q_joint = D.T P D, with
nullity d+1 (assuming n>=d+2), whereas the original Q=D.T D
has nullity d. Its original conditional smoothness normalization
(n-tr H)/(n-d) should NOT be imported unchanged. This model
could be important future research, but it is not what
mu='data' currently implements.

## Numerical experiments and decisions

The previous guard "d<=4 -> Cholesky, d>=5 -> SVD" was a
conservative experimental numerical safeguard from small, fixed-mu
cases, not an optimized general rule. Actual performance depends
on n,d,S,number of independent series, number of S candidates,
amplitude, mean policy, error tolerance, and cache/memory.

The first Experiment007 results are available at:
results/experiment007-selfhosted-41510249404.
They show observed-mu crossovers vary by n,d,scale and reuse,
with incomplete reliability of non-spectral methods at high d.
A twelve-seed follow-up counterbalances method order and repeats
cold timing. No automatic method selection should be adopted
based on two seeds or on an SVD-proxy accuracy check.

The correct next scientific question is whether to retain
mu_data as a practical estimate of mean(D*tau_true), or to
formally adopt the jointly optimized mu model. They should not
be silently conflated or presented as identical theoretical models.
