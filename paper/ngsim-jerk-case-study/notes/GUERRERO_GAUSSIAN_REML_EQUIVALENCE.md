# Guerrero's PLS variance ratio and the exact fixed-mean Gaussian REML identity

**Status:** Mathematical verification of the existing implementation, **not a new estimator, an independent simulation, or an additional numerical result**. Updated 2026-11-09 following the author's clarification. This note must be read before interpreting Paper C Experiment004 or Experiment005 MLE comparisons.

## Primary source and provenance

Victor M. Guerrero (2007), "Time series smoothing by penalized least squares", *Statistics & Probability Letters* **77**:1225–1234, DOI [10.1016/j.spl.2007.03.006](https://doi.org/10.1016/j.spl.2007.03.006).

The author supplied the full article, including handwritten instructional annotations. The primary article's Eq. (3) and Eqs. (6)–(7) specify a linear second-moment model, Proposition 1, Eq. (12), defines the PLS solution, and Eq. (17) specifies the **observed-difference sample-mean reference** when the true mean is unknown. The author chooses a smoothing index in Sec. 3. **Guerrero does not require Gaussian distributions in this derivation, nor does that article itself give the Gaussian REML optimization below.** The restricted likelihood arises after strengthening the second-moment assumptions to Gaussian independent disturbances. Attribute the original variance-ratio PLS interpretation to Guerrero, the following Gaussian likelihood derivation to its statistical extension.

## Model and known/fixed reference mean

Let n > d ≥ 1, m=n−d, D a full-row-rank m×n order-d difference matrix, B=DDᵀ ≻ 0 and Q=DᵀD ⪰ 0. Let 1 denote an m-vector of ones. Define

\[
y=\tau+\varepsilon,\quad D\tau=\mu\mathbf1+u,
\quad \varepsilon\sim N(0,\sigma_\varepsilon^2 I_n),
\quad u\sim N(0,\sigma_u^2 I_m),\quad u\perp\varepsilon.
\]

With lambda=σ_ε²/σ_u², the conditional posterior mode/mean of the trend is the PLS estimator

\[
\widehat\tau_\lambda=
(I_n+\lambda Q)^{-1}
(y+\lambda\mu D^\top\mathbf1).
\]

For the **fixed** mean, set z=Dy−mu·1. Differencing removes the unpenalized polynomial nullspace:

\[
z\sim N(0,\sigma_u^2 W_\lambda),\quad W_\lambda=I_m+\lambda B.
\]

The restricted minus-twice profile log likelihood, up to lambda-independent constants, is

\[
F_D(\lambda;\mu)=
\log|I_m+\lambda B|+
m\log\left[
\frac{(Dy-\mu\mathbf1)^\top
 (I_m+\lambda B)^{-1}(Dy-\mu\mathbf1)}{m}
\right].
\]

The profiled difference innovation variance is
\(\widehat{\sigma}_u^2(\lambda)=z^\top W_\lambda^{-1}z/m\).
The observation variance estimate is \(\widehat{\sigma}_\varepsilon^2=\lambda\widehat{\sigma}_u^2\).

The derivative used for numerical optimization is

\[
F_D'(\lambda)=
\mathrm{tr}(W_\lambda^{-1}B)
-m\,
\frac{z^\top W_\lambda^{-1}B W_\lambda^{-1}z}
{z^\top W_\lambda^{-1}z}.
\]

Interior zeros are candidates only: the objective can have local extrema and should also be checked at lambda→0⁺ and lambda→+∞. A finite candidate grid need not find its continuous global minimizer.

## EXACT equivalence with existing src/trendestimation/likelihood.py

Let the compact singular-value decomposition be
\(D=L\,\operatorname{diag}(\sqrt{\delta_j}) V_+^\top\),
with all positive eigenvalues \(\delta_j>0\), j=1,…,m, of both B and the penalized part of Q. Choose any p_mu such that D p_mu=mu·1. Define the positive-penalty trend coordinates

\[
c_j=(V_+^\top(y-p_\mu))_j.
\]

Then z = L diag(sqrt(delta_j)) c, so

\[
F_D(\lambda;\mu)=
\sum_{j=1}^m\log(1+\lambda\delta_j)
+m\log\left(\frac1m\sum_{j=1}^m
\frac{\delta_jc_j^2}{1+\lambda\delta_j}\right).
\]

The existing scorer in src/trendestimation/likelihood.py uses observation-variance parametrization and computes

\[
F_{\mathrm{repo}}(\lambda;\mu)=
\sum_{j=1}^m\log a_j+
m\log\left(\frac1m\sum_{j=1}^m\frac{c_j^2}{a_j}\right),
\quad a_j=1+\frac{1}{\lambda\delta_j}.
\]

Using \(a_j=(1+\lambda\delta_j)/(\lambda\delta_j)\) gives

\[
\boxed{F_{\mathrm{repo}}(\lambda;\mu)=
F_D(\lambda;\mu)-\sum_{j=1}^m\log\delta_j}
=F_D(\lambda;\mu)-\log|B|.
\]

**The two objectives have the same derivatives and exactly the same lambda minimizers for every fixed mu.** The additive constant can be large, so likelihood values themselves need not be numerically identical; only within-model rankings/parameter choices should be compared.

- The existing public selector is select_lambda(smoother, y, criterion="mle", mu=<fixed mean>).
- The library's estimator for lambda is a **grid minimizer** when supplied with a 15-point S grid, as in Experiments004–005; it does not perform continuous derivative-based minimization for criterion="mle".
- The variance components returned by estimate_variance_components agree with the same variance-ratio parametrization, for fixed mean.
- The Gaussian model's PLS trend is a **posterior mode/MAP**, equal to its posterior mean under the Gaussian linear system, not an unrestricted MLE of an unconstrained deterministic trend vector.
- The existing d=3, mu=0 MLE comparisons and the nonzero mu **conditional plug-in** comparisons in Exp004/005 have therefore already evaluated the intended fixed-mean Gaussian REML criterion. **Do not rerun or overwrite historical experiment results to rename an algebraically identical objective.**

### Independent numerical verification

For a 30-observation, order-3 series with mu=0.016 and several positive penalty values, a direct dense-B likelihood and the independent spectral-coordinate formula agreed to roughly 1e−10 after subtracting the constant log|B|. The regression tests in tests/test_paper_c_guerrero_reml_identity.py verify the equality and derivative directly against the actual library implementation.

## IMPORTANT: mean estimated rather than fixed

Guerrero Eq. (17) gives
\[
\widehat{\mu}_{\mathrm{sample}}=\frac{\mathbf1^\top Dy}{m}.
\]
It is unbiased under a zero-mean noise model, but **does not eliminate the need to account for its estimation in restricted likelihood**. Similarly, global/tail cubic OLS means are empirical plug-ins, not joint ML for the variance and mean parameters.

If **mu itself must be estimated by Gaussian ML/GLS**, set v=Dy and define

\[
\widehat\mu_\lambda=
\frac{\mathbf1^\top W_\lambda^{-1}v}
{\mathbf1^\top W_\lambda^{-1}\mathbf1}.
\]

Let \(r_\lambda=v-\widehat\mu_\lambda\mathbf1\) and
\(q_\lambda=r_\lambda^\top W_\lambda^{-1}r_\lambda\).
After eliminating one additional nuisance mean direction, the **mean-adjusted REML** objective, up to lambda-independent constants, is

\[
\boxed{
F_{\mathrm{REML},\,\mu\ \mathrm{unknown}}(\lambda)
=\log|W_\lambda|+
\log(\mathbf1^\top W_\lambda^{-1}\mathbf1)
+(m-1)\log\left(\frac{q_\lambda}{m-1}\right).
}
\]

The additional \(\log(\mathbf1^\top W_\lambda^{-1}\mathbf1)\) term and the reduction from m to m−1 penalized degrees of freedom are essential. This is **different** from merely plugging a previously estimated mean into the fixed-mu objective, or from jointly profiling mean/variance by ordinary full ML (which would not carry the same REML determinant term).

Do not re-label Exp005 mean-policy results as this unknown-mean REML. Implement it as a separately documented future experiment or API enhancement with numerical and statistical tests if desired. Under the d=3 physical interpretation, the reference jerk is \(\mu/\Delta t^3\), while the penalty uses mu in **discrete third-difference units**.

## Scientific consequence for Paper C

The surprising Exp005 finding that Gaussian profile ML produced substantially smaller **known-discrete-jerk RMSE** than GCV cannot be dismissed as having used the "wrong MLE": it used exactly the fixed-mean Gaussian restricted likelihood derived here, conditional on each chosen reference mean. What remains to verify is (1) continuous optimization and boundaries versus the coarse shared smoothness grid; (2) the **unknown-mean REML correction**; (3) how observation noise differs from modeled independent Gaussian errors; and (4) jerk versus *recorded-future-position* forecasting (Exp004).

Avoid claiming the existing MLE was invented as a new formula by the library, or historically proposed as a Gaussian likelihood by Guerrero in 2007. Cite the stochastic PLS variance-ratio source and distinguish the separate Gaussian REML derivation.
