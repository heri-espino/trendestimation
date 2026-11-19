# Gaussian restricted/marginal likelihood: primary-source and proof audit

Updated: 2026-11-19. Scope: theoretical CSDA manuscript clarification, not a new likelihood or numerical benchmark.

## Original sources

- **Patterson & Thompson (1971)**, Recovery of Inter-Block Information when Block Sizes Are Unequal, Biometrika 58(3):545--554, DOI 10.1093/biomet/58.3.545. Historical restricted/modified likelihood using error contrasts; original publisher metadata verified.
- **Wahba (1985)**, A Comparison of GCV and GML for Choosing the Smoothing Parameter in the Generalized Spline Smoothing Problem, Annals of Statistics 13(4):1378--1402, DOI 10.1214/aos/1176349743. Generalized maximum likelihood for smoothing selection; publisher record verified.
- **Wood (2011)**, Fast Stable Restricted Maximum Likelihood and Marginal Likelihood Estimation of Semiparametric Generalized Linear Models, JRSS Series B 73(1):3--36, DOI 10.1111/j.1467-9868.2010.00749.x. Stable methods for REML/marginal-likelihood smoothing; publisher and author-institution records verified.
- **Biessy (2026)**, Whittaker--Henderson Smoothing Revisited: A Modern Statistical Framework for Practical Use, ASTIN Bulletin, DOI 10.1017/asb.2025.10061. **Original user-uploaded full 31-page PDF inspected directly**. Section 5.2 mentions Patterson--Thompson REML and Wood; Section 5.3 (printed p. 12) derives a Gaussian WH marginal likelihood with minimized penalized quadratic and determinant difference ln|W+P_lambda| - ln|P_lambda|_+. Section 5.4 generalizes with a Laplace approximation. For unweighted mu=0 we specialize W=I and P_lambda=lambda D^T D, then profile the observation variance.

## Derivation and correct terminology

Set r=n-d and D_d=U Sigma V^T (reduced full-row-rank SVD), W an orthonormal nullspace basis. For fixed mu, choose D_d p_mu=mu 1_r. Assume y=p_mu+W beta+V theta+epsilon, beta an unknown FIXED effect, theta Gaussian with covariance sigma_u^2 Sigma^-2, and epsilon independent isotropic Gaussian with covariance sigma_e^2 I.

The contrast z=V^T(y-p_mu)=theta+V^T epsilon removes beta. Its independent variances are sigma_e^2 c_j, c_j=1+1/(lambda delta_j), lambda=sigma_e^2/sigma_u^2. The proper restricted error-contrast density has

    -2 ell_R = r log(2 pi sigma_e^2) + sum_j log c_j
               + (sum_j z_j^2/c_j)/sigma_e^2.

For nonzero z, profile sigma_e^2_hat = (sum_j z_j^2/c_j)/r, yielding

    L(lambda)=r log((sum_j z_j^2/c_j)/r)+sum_j log c_j,

plus the lambda-independent constant r(1+log(2pi)). This is the existing Gaussian contrast/REML likelihood in orthogonal penalized coordinates, not a newly invented likelihood. For unknown data-estimated mu, the fixed-effects and restriction dimension may change, requiring a distinct derivation. z=0 has a variance boundary degeneracy.

## Equivalent Cholesky sufficient statistics

Set A_lambda=I+lambda D^T D, B=DD^T and J_lambda the minimized fixed-mu penalized objective. By scalar quadratic minimization:

    J_lambda=sum_j z_j^2/c_j
    sum_j log c_j = logdet A_lambda - r log lambda - logdet B.

A and B are banded SPD for lambda>0. This representation does not need an SVD or dense inverse for every candidate. It belongs alongside classical prior art rather than being called a new likelihood.

## Deterministic tests

The file paper/csda-unified-theory/tests/test_reml_contrast.py tests n,d and fixed mu values, verifies SVD contrast versus direct differenced covariance, optimized PLS objective, determinant correction, beta invariance, shift-free contrasts and profiling constants.

Reproduction from repository root:

    python paper/csda-unified-theory/verify_theory.py
    python paper/csda-computational-costs/verify_theory.py
    python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_*.py' -v

The publication workflow compiles Elsevier CAS, preserves the two existing native-landscape algorithm tables and commits a compiled PDF with checksums to the paper branch.

## Limits and source verification status

The user-provided original Biessy PDF was inspected directly. Patterson--Thompson, Wahba and Wood were checked against publisher metadata and institutional abstract sources; their original full texts remain a pre-submission line-level source audit. No universal computational superiority, novelty of REML or profiling, or cross-time forecast advantage is claimed. No jointly estimated mean or correlated-error likelihood is proved here. Coauthor and journal-submission signoff are outside this editorial task.
