# State-of-the-art positioning and citation audit — 2026-11-23

## Scope and source of truth

This is a **source-only editorial revision** of the canonical unified
CSDA theoretical manuscript at `paper/csda-unified-theory/main.tex`.
The mathematical definitions, theorems, proofs, code, results, figures,
data, historical A/B manuscripts, and other publication tracks were not
modified. This note is intended to make later referee and AI-agent review
reproducible. No new experiment, speed measurement, source-matched PDF
compilation, or journal submission was performed in this editorial pass.

Read `../AGENTS.md`, `../SCOPE_AND_PROOF_AUDIT.md`,
`CONTRIBUTION_PRIORITY_AUDIT_20261123.md`,
`PRIMARY_REFERENCE_AUDIT_20261119.md`, and
`GAUSSIAN_LIKELIHOOD_PROVENANCE.md` before further edits.

## Central claim

We contribute a **joint smoothness-indexed computation and selection
framework** for fixed-reference, unweighted, arbitrary-order
finite-difference PLS: rank-normalized smoothness with exact endpoints;
a retained SVD of the rectangular difference matrix; shift-free
nonzero-reference reconstruction; profiling of established Gaussian
REML/error-contrast likelihood in the same spectral coordinates;
complete CV/GCV/IC/likelihood diagnostics; and end-to-end setup,
candidate, series, memory and admissibility accounting.

It is the **combination, full-criterion specification, and computational
decision analysis** that distinguishes the treatment. The manuscript
does not claim invention of penalized least squares, SVD, the
Demmler–Reinsch basis, smoothing likelihoods, the historical trace
index, the nonzero mean of differences, selected inversion or
Whittaker–Henderson rank reduction. Numerical complexity bounds are
not hardware speed measurements.

## Original and externally checked works: claim-to-citation mapping

| Source | DOI | Role and manuscript use |
| --- | --- | --- |
| Demmler & Reinsch (1975), *Oscillation matrices with spline smoothing*, Numerische Mathematik 24:375–382 | 10.1007/BF01437406 | Historical spectral/orthogonal spline-penalty basis; new key `demmler1975` in introduction, model, algorithm comparison and provenance. Not the invention of the modern direct SVD of discrete D. |
| Biessy (2026), *Whittaker–Henderson smoothing revisited*, ASTIN Bulletin | 10.1017/asb.2025.10061 | The especially important modern prior art: Section 6.4 **explicitly credits Demmler–Reinsch**, eigendecomposes discrete penalty `D^T D`, and develops **approximate rank reduction**; Section 5.3 gives Gaussian marginal likelihood. Existing key `biessy2026`; strengthen precise use-site citations. |
| Golub & Reinsch (1970), *Singular Value Decomposition and Least Squares Solutions* | 10.1007/BF02163027 | Direct SVD and danger of explicitly forming Gram matrices (published p. 404). Existing `golubreinsch1970`. Distinguish loss of accuracy potential from guaranteed runtime superiority. |
| Eilers (2003), *A Perfect Smoother*, Analytical Chemistry 75:3631–3636 | 10.1021/ac034173t | Applied Whittaker smoothing in spectroscopy/analytical chemistry; new `eilers2003`. Demonstrates scope beyond finance and actuarial graduation; does **not** establish our full grid complexity. |
| Eilers & Marx (1996), *Flexible Smoothing with B-Splines and Penalties* | 10.1214/ss/1038425655 | Existing `eilersmarx1996`. P-spline regression-basis penalty is related but not identical to unweighted direct finite-difference smoothing of the observed trend. |
| Kim, Koh, Boyd & Gorinevsky (2009), *L1 Trend Filtering* | 10.1137/070690274 | Existing `kim2009`. L1 difference penalty as alternative promoting structural adaptivity/piecewise linear trends. Not claimed an algorithmic competitor in our exact quadratic cost table. |
| Tibshirani (2014), *Adaptive Piecewise Polynomial Estimation via Trend Filtering*, Annals of Statistics 42:285–323 | 10.1214/13-AOS1189 | New `tibshirani2014`; rigorous adjacent L1 treatment. Clarifies why quadratic PLS remains attractive for an affine smoothing operator with explicit influence, trace and exact Gaussian coordinates when smooth regularity is appropriate. |
| Hamilton (2018), *Why You Should Never Use the Hodrick-Prescott Filter*, Review of Economics and Statistics 100:831–843 | 10.1162/REST_a_00706 | New `hamilton2018`; important boundary: an easier numerical smoother or new coordinate does not remove model-based concerns about interpreting macroeconomic cycles. Does not directly challenge algebraic PLS identities. |
| Guerrero (2007; 2008); Cortés-Toto et al. (2017) | 10.1016/j.spl.2007.03.006; 10.1111/j.1751-5823.2008.00047.x; 10.1080/03610918.2015.1005236 | Established fixed nonzero mean, original n-normalized smoothness index and variance ratio, and classical selection criteria. The present r=n-d normalization is an operational rescaling, not a new smoother or a new statistical measure of absolute precision. |
| Weinert (2007), *Efficient computation for Whittaker–Henderson smoothing* | 10.1016/j.csda.2006.11.038 | Banded structured exact WH/GCV algorithm, especially q=2; not an SVD of D. O(n) for fixed order/penalty; full M candidates cost O(Mn). Existing `weinert2007`. |
| Craven & Wahba (1979); Golub, Heath & Wahba (1979) | 10.1007/BF01404567; 10.1080/00401706.1979.10489751 | GCV and spectral ridge GCV. Existing citations already placed in criterion section. |
| Patterson & Thompson (1971); Wahba (1985); Wood (2011) | 10.1093/biomet/58.3.545; 10.1214/aos/1176349743; 10.1111/j.1467-9868.2010.00749.x | Original REML, GML smoothing-selection and modern semiparametric likelihood context. Existing references; Gaussian-contrast novelty restricted to the explicit fixed-mu specialization and computational integration. |
| Erisman & Tinney (1975); Lin et al. (2011); Hutchinson (1990); Ubaru et al. (2017) | See `PRIMARY_REFERENCE_AUDIT_20261119.md` | Distinguish exact selected-inverse leverages from approximate stochastic trace/logdet; existing references remain unchanged. |

Bibliographic details for the four added entries were checked against
the cited publisher records and scholarly indexes in this pass.
For Demmler & Reinsch, the DOI 10.1007/BF01437406 refers to the
Numerische Mathematik article on pp. 375–382, **not** the distinct
1975 Reinsch paper on pp. 383–393 (DOI 10.1007/BF01437407).

## Essential distinction: Demmler–Reinsch, Biessy, and our direct SVD

For the full-row-rank difference operator
`D_d` of shape `r × n`, `r=n-d`, let
`D_d=U diag(sigma_j) V^T` denote a reduced SVD.
Then `Q_d = D_d^T D_d = V diag(sigma_j^2) V^T`
on the penalized subspace. Therefore the **Gram
eigenvectors and right singular vectors agree up to
orthogonal transformations within repeated eigenspaces**,
and the exact zero-nullspace part must also be retained.

The positive-spectrum condition-number relation
`kappa_+(Q_d)=kappa_+(D_d)^2` is elementary algebra.
Forming Q explicitly may lose information about small
positive singular values in floating point, so working
directly with D is an accuracy-motivated **design choice**.
This does not imply all eigensolvers are inferior or that
a full SVD is universally faster than banded Cholesky.

Biessy's rank-reduced Gram-eigenbasis trades approximation
for speed and supports weight matrices not restricted to
I. In particular, general `U^T W U` is not diagonal
when `W != I`. Our exact scalar shrinkage and full
candidate-criterion identities assume `W=I` and retain
all r penalized directions. They are therefore narrower
in statistical model class but expose an explicit
smoothness-coordinate/criterion-completion comparison
that is central to our article.

## Editorial changes introduced

1. Rewrote the abstract to open with the practical problem and
   explain the integration and its testable computational meaning.
2. Added direct Demmler–Reinsch and Biessy Section 6.4 citations
   to introduction, SVD model, algorithms, and provenance table.
3. Distinguished direct full SVD versus Gram eigendecomposition,
   weighted rank reduction, and the `W=I` assumption in prose.
4. Cited Eilers for use outside actuarial/economic series and
   Eilers–Marx for P-spline alternatives.
5. Added L1 trend filtering as an honest methodological contrast
   and Hamilton's macroeconomic caution in the conclusion.
6. Strengthened the problem statement and concluding significance:
   exact complete-criterion and amortized-workload accounting,
   conditional on the prescribed reference and the model.

## Reproduction / remaining gate

This is a citation/wording/context edit: **no change to equations,
theorems, proofs, numeric measurements or figure artifacts**.
Before merging or submitting, run existing checks:

```bash
python paper/csda-unified-theory/verify_theory.py
python paper/csda-computational-costs/verify_theory.py
python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_*.py' -v
```

Compile `paper/csda-unified-theory/main.tex` with the established
manual-only `csda-unified-theory.yml` GitHub Actions workflow or
documented Elsevier CAS source-only method; verify the four new
bibliography keys resolve, both native landscape tables remain
legible, and all PDF pages/figures remain intact. Record
commit and PDF hash before acceptance. **No new benchmark,
no publication submission, and no PR merge** in this pass.

## Suggested future citation scrutiny (not automatically inserted)

Broader benchmark or discussion revisions could consider
Ravn & Uhlig (2002) on sampling-frequency scaling of HP,
Hutchinson & de Hoog (1985) on trace computations,
and contemporary weighted WH extensions. They should be
placed only where a concrete supported claim warrants them;
the present source-only edit is deliberately focused.
