# Primary-source audit: Weinert (2007), third differences, and SVD versus banded solvers

Status: manuscript-only mathematical and bibliographic revision; no empirical benchmark campaign.

## Original source, inspected directly

Howard L. Weinert (2007), **Efficient Computation for Whittaker–Henderson Smoothing**,
*Computational Statistics & Data Analysis* 52(2):959–974,
DOI https://doi.org/10.1016/j.csda.2006.11.038.

The PDF supplied by the user was read at these locations:

- **Published p. 959**, Eq. (1.1): objective alpha * ||y-x||² + ||Delta^p x||², forward difference, general p<n.
- **Published p. 960**, Eqs. (1.2)–(1.7): matrix M is the rectangular difference matrix; primal A = alpha I + M^T M; an alternate dual system uses I + alpha^-1 M M^T. Merely using M does NOT mean the algorithm takes its SVD.
- **Published p. 961**, Eq. (1.8): GCV uses the fitted trend and trace(alpha A^-1); the text explains O(n) inverse-trace computation for fixed p, historic attribution to Spoerl (1943) before Takahashi et al. (1973). Weinert explicitly restricts the subsequent new algorithms to p=2.
- **Published pp. 962–963**, Eqs. (2.1)–(2.14): a **banded LDL^T factorization of A**, forward/back substitution, and reverse inverse-diagonal recurrences for exact GCV. This is NOT an SVD(M) algorithm.
- **Published pp. 963–964**, Section 3: alternative **state-space** smoother, likewise not an SVD(M) algorithm.

## Parameter conventions

Weinert (mu=0): minimize alpha ||y-x||² + ||M x||², alpha > 0.
The paper studied here (mu=0): minimize ||y-tau||² + lambda ||D_d tau||², lambda >=0.

With M = D_d, the same fitted values arise for lambda = 1/alpha, alpha>0:

    (alpha I + D^T D) x = alpha y
    (I + lambda D^T D) tau = y.

Weinert's main recursive examples are order p=2; our original difference-order variable is d. **The current article also permits fixed nonzero mu**, for which the right side is y + lambda mu D^T 1, requiring an explicit distinction from Weinert's uncentered examples.

## Why SVD(D) is interesting (without claiming it is always faster)

- A retained SVD of D_d is independent of lambda, y and fixed mu. Scalar spectral weights vary with lambda; computed basis and data projections can be reused for many candidate penalty levels.
- Dense *retained* SVD for r=n-d has O(nr²) setup and O(nr) working storage; projected scalar GCV/IC/likelihood is O(r) per candidate after projection. Exact CV or complete reconstruction can require O(nr) per candidate; S-to-lambda root inversion costs must also be charged.
- Weinert's order-two LDL^T/trace method achieves O(n) fit/GCV per candidate at fixed difference order. It is not asymptotically exponential over M penalties; it scales linearly with M (if the penalties are already known).
- When d is fixed and n grows, dense retained SVD is O(n³) setup while banded Cholesky is O(n) per candidate, so moderate M generally favors banded methods in an arithmetic upper-bound comparison. A crossover is workload- and hardware-dependent, not implied by having "many lambda" alone.
- SVD(D) avoids forming Q=D^T D and squaring its **positive-spectrum** condition number. Symmetric eigendecomposition(Q) is exactly equivalent in exact arithmetic; **eigendecomposition(H_lambda)** is additionally unattractive because constructing the dense H_lambda can cost O(n³) and extracting small delta from h close to 1 may cancel. Its eigenvectors are nevertheless shared across lambda in exact arithmetic; never claim they intrinsically change.

## Third-difference exactly verified example

For n=6, D_3 has three rows with stencil (-1,3,-3,1).

    D3 = [[-1, 3,-3, 1, 0, 0],
          [ 0,-1, 3,-3, 1, 0],
          [ 0, 0,-1, 3,-3, 1]]

    Q3 = D3^T D3 =
         [[ 1,-3,  3, -1,  0,  0],
          [-3,10,-12,  6, -1,  0],
          [ 3,-12,19,-15,  6, -1],
          [-1, 6,-15, 19,-12,  3],
          [ 0,-1,  6,-12, 10, -3],
          [ 0, 0, -1,  3, -3,  1]]

Q3 is singular of rank 3 with nullity 3; A_lambda=I+lambda Q3 is SPD. H_lambda is usually dense. At lambda=1, its (1,6) entry is EXACTLY 11/195, even though (Q3)[1,6]=0.

For uniform sample spacing h, the centered third forward difference divided by h³ is an O(h²) approximation to the **third time derivative**, jerk, at the stencil midpoint. For x(t) polynomial of degree 3 with constant jerk j, Delta³ x = j h³ exactly; fixed mu=j h³ permits a cubic limiting trend, while mu=0 permits a quadratic (zero-jerk) trend.

Noisy observed positions do NOT imply separately observed physical jerk. A third-difference penalty regularizes an estimated derivative, not a physically measured signal.

## Selecting unknown d

If the application does not justify a fixed d a priori, one can select (d,S) as two hyperparameters with held-out validation; for future-time predictions prefer rolling-origin/future-held-out scores (see Tashman 2000 and Bergmeir et al. 2018, already in the manuscript bibliography), with the final test period untouched after tuning. The order d changes the nullspace, units and actual fit family. This procedure is an *extension*, not an experiment undertaken for this manuscript. No claim that d=3 is universally optimal.

## Reproduction and QA

Run the source-only deterministic identity and regression checks:

    python paper/csda-unified-theory/verify_theory.py
    python paper/csda-computational-costs/verify_theory.py
    python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_*.py' -v

The tests cover the manuscript's exact D3/Q3 matrices, rank/nullity, SPD A, dense H_1 endpoint, Weinert alpha=1/lambda equivalence for mu=0, cached nonzero-mu SVD reconstruction for several lambdas, and constant-jerk cubic versus zero-jerk quadratic identity.

Compilation uses the existing Elsevier CAS source-only Actions workflow, then the existing rotate_landscape_tables.py script to preserve the two native landscape table pages and PDF SHA-256 provenance. Do not rerun Experiment011, change software solvers, rewrite historical paper branches or invent measured timing conclusions.
