# Paper C — normalized smoothness and relative-precision source audit

**Date:** 2026-11-19. **Scope:** Mathematical and editorial verification from the two original author-uploaded PDFs. No new experiments, numerical claims, or methods.

## Primary sources directly inspected

**Guerrero (2007)**, *Time series smoothing by penalized least squares*, Statistics & Probability Letters 77:1225–1234, DOI [10.1016/j.spl.2007.03.006](https://doi.org/10.1016/j.spl.2007.03.006). Author-uploaded complete article *Time Series Smoothinhg by Penalized Least Squares 2.pdf*: printed pp. 1225–1226 discuss nonzero difference-reference mean; pp. 1229–1230, equations (21)–(23), derive fitted-trend precision and Theil-inspired relative precision; p. 1233 discusses percentage smoothness and comparability conditions.

**Cortés-Toto, Guerrero and Reyes (2017)**, *Trend smoothness achieved by penalized least squares with the smoothing parameter chosen by optimality criteria*, Communications in Statistics--Simulation and Computation 46(2):1492–1507, DOI [10.1080/03610918.2015.1005236](https://doi.org/10.1080/03610918.2015.1005236). Author-uploaded full article: printed p. 1495, equation (9), explicitly writes the original smoothness index and its exact limit $1-d/n$; printed p. 1496, equations (13)–(16), gives the variance-ratio, precision-matrix and Theil trace interpretation. Standard CV/GCV/AICc/BIC may induce different smoothness levels.

We attribute the trace method to Theil (1963) **through these directly read sources**, without inserting a separate unverified Theil BibTeX entry.

## Original index versus rank-normalized index

Let $D=D_d$ be a full-row-rank $(n-d)\times n$ difference matrix, $Q=D^\top D$, and $H_\lambda=(I+\lambda Q)^{-1}$. Write $m=n-d$ and $\delta_1,\ldots,\delta_m>0$ for the penalized eigenvalues. The original Guerrero index is

$$
S_G(\lambda)=1-\frac{\operatorname{tr}(H_\lambda)}{n}
=\frac1n\sum_{j=1}^m\frac{\lambda\delta_j}{1+\lambda\delta_j}
\longrightarrow \frac{m}{n}=1-\frac dn \quad(\lambda\to\infty).
$$

Paper C's **rank-normalized** index (already used in the library and experiments) is

$$
S(\lambda)=\frac1m\sum_{j=1}^m\frac{\lambda\delta_j}{1+\lambda\delta_j}
=\frac n{n-d}S_G(\lambda).
$$

This version has exactly the closed limiting range $[0,1]$. For any finite $\lambda>0$, the value lies strictly in $(0,1)$. As $\lambda\to\infty$, $S\to1$ and the $d$ unpenalized polynomial modes remain. The derivative

$$
S'(\lambda)=\frac1m\sum_j\frac{\delta_j}{(1+\lambda\delta_j)^2}>0
$$

implies a unique $\lambda$ for each target $s\in(0,1)$, **at fixed $n,d$ and fixed difference operator**. Do not claim equal $s$ implies identical trajectory geometry under changed data grids or difference orders. For fixed reference $\mu$, $\operatorname{df}(H_\lambda)=n-mS$; if $\mu$ or $\lambda$ is data-selected, the full adaptive degrees of freedom need further treatment.

## Precisely what relative precision refers to

Assume the second-moment model

$$
y=\tau+\varepsilon,\quad D\tau=\mu\mathbf1+u,\qquad
\operatorname{Cov}(\varepsilon)=\sigma_\varepsilon^2I,\quad
\operatorname{Cov}(u)=\sigma_u^2I,\quad\operatorname{Cov}(u,\varepsilon)=0,
\quad \lambda=\sigma_\varepsilon^2/\sigma_u^2.
$$

Guerrero's total estimator-error precision matrix is $J=\sigma_\varepsilon^{-2}I+\sigma_u^{-2}Q$; smoothness contributes $P=\sigma_u^{-2}Q$. The relative-precision trace normalized over the **penalized directions** gives

$$
\frac1m\operatorname{tr}(PJ^{-1})
=\frac1m\operatorname{tr}[(\lambda Q)(I+\lambda Q)^{-1}]=S(\lambda).
$$

Separately, the covariance of the observed differences $z=Dy-\mu\mathbf1$ is $\sigma_u^2I+\sigma_\varepsilon^2DD^\top$. The average spectral variance fraction due to differenced measurement noise is

$$
\frac1m\operatorname{tr}[(\sigma_u^2I+\sigma_\varepsilon^2DD^\top)^{-1}
(\sigma_\varepsilon^2DD^\top)]=S(\lambda).
$$

This second expression is our derived *conditional spectral covariance attribution*. Neither expression is absolute sensor precision, the percentage of accurate individual position records, the probability a trajectory observation is correct or a guarantee of reconstructing physical jerk. Gaussianity is required for the Gaussian likelihood used elsewhere, not for these second-moment identities. Simultaneously increasing both observation noise and genuine jerk volatility by the same multiplicative factor preserves $S$ while changing absolute sensor-noise variance.

## Six defensible design advantages; different from a novelty assertion

1. Strict convexity and unique fixed-parameter quadratic trend fit.
2. Penalizing the physical **discrete third-difference jerk** proxy, not merely minimizing position error.
3. A trainable signed, possibly nonzero reference third difference $\mu$ and a meaningful cubic rather than necessarily quadratic strong-smoothing limit.
4. Gradual soft spectral attenuation rather than hard TSVD cutoff.
5. Bounded monotone $S$, exact fixed-reference conditional degrees of freedom, and model-dependent relative precision.
6. Sparse/banded fixed-order differences supporting structured linear algebra without a dense inverse.

These properties were known in the wider PLS/regularization literature or follow algebraically; they are **not six new inventions**. The contribution in Paper C is their physical combination and controlled comparison on 1,296 archived known-jerk synthetic trajectories, 1,944 factorial calibration treatments from only 72 independent parents, and 200 non-independent recorded NGSIM episodes. Preserve the adverse spline-plus-quadratic-Taylor 0.3480 m first-second recorded-position result. This is not a claim of universal superiority, robustness to abrupt maneuvers, hard physical feasibility, novel forecasting dynamics or independently observed true NGSIM jerk.

## Manuscript integration and reproducibility

Relevant edits: main.tex and sections/introduction.tex, sections/methods.tex, sections/discussion.tex. The 51-entry source-matched bibliography is unchanged. The exact original mathematical normalization difference is now explicit. Build only the manuscript through an approved Windows PC08 build; no Experiments004–008, plots, observations or supplement should be regenerated. Check bibliography/LaTeX, inspect all pages, update the active 16-file SHA-256 publication ledger using Git LF bytes and archive the compiled PDF. The earlier verified 15-page SOA PDF archive must be preserved. No journal submission or unauthorized changes to other manuscripts.
