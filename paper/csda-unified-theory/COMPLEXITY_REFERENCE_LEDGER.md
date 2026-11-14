# Computational-complexity reference ledger

Created November 9, 2026. Accompanies the consolidated CSDA theoretical manuscript. The standard algorithmic costs cited below are **prior art**. The end-to-end smoothness-indexed workflow formulae are the authors' own conditional derivations from those costs. Sources were verified for bibliographic identity and topic; confirm exact textbook pages before submission.

| Algorithmic claim | Authoritative source | Mathematical and implementation qualifications |
| --- | --- | --- |
| Dense matrix factorizations and eigendecompositions, O(n^3) arithmetic and O(n^2) storage | Golub and Van Loan (2013), Matrix Computations, 4th ed., Johns Hopkins University Press | Generic dense algorithms, not the optimal special-structure cost |
| Full retained reduced SVD of r-by-n matrix, O(n r^2) work, O(n r) singular-vector storage | Golub and Van Loan (2013) | Standard dense rectangular SVD; D is also banded, so other implementations may exist |
| Banded SPD Cholesky, O(nd^2) arithmetic, O(nd) storage; triangular solve O(nd) | Golub and Van Loan (2013); Davis (2006), DOI:10.1137/1.9780898718881 | Half-bandwidth d, natural banded factorization without a generic sparse pivoting pattern |
| Selected-inverse diagonal, O(nd^2) work and O(nd) storage in this recurrence | Erisman and Tinney (1975), DOI:10.1145/360680.360704; Weinert (2007), DOI:10.1016/j.csda.2006.11.038 | Authors count O(nd) selected entries with at most O(d) updates each; fixed d implies linear work |
| Sparse Cholesky and sparse LU | Davis (2006) | Fill, ordering and pivoting determine cost; no universal one-line cost for arbitrary sparse matrices |
| PCG, O(qnd) for q iterations with local order-d matvec | Saad (2003), DOI:10.1137/1.9780898718003 | Authors directly count O(nd) for the local difference application; this excludes preconditioner setup, spectral diagnostics and extra statistical scoring; q is convergence-dependent |
| Efficient Whittaker-Henderson trend and GCV with model structure | Weinert (2007), Computational Statistics and Data Analysis 52, 959-974 | Existing specialized GCV algorithms; do not claim first invention of efficient complete GCV |
| Shared spectral S-inversion O(M I r), CV leverage O(nr) per candidate, GCV projected score O(r) | Authors' finite-sum and matrix-vector arithmetic | Assumes r=n-d, M distinct smoothing values, at most I map iterations, and cached projections |
| Full-SVD amortized workload theorem | Authors' Complexity section, built from cited standard components | Original composite *upper bound* after counting mapping, preparation, series projections, criterion evaluations and CV leverage |
| Banded complete-grid workload theorem | Authors' Complexity section, built from cited standard components | Original composite *upper bound* assuming selected-inverse diagnostics for each map trial/candidate and reuse across criteria and series |
| Conditional affine crossover M_star | Authors' direct algebra | Requires measured or calibrated affine constants and favorable slope/intercept signs; Big-O cannot predict a machine crossover |

## Publication metadata references

- Golub, G. H. and Van Loan, C. F. (2013). Matrix Computations, 4th ed. https://www.press.jhu.edu/books/title/10678/matrix-computations
- Davis, T. A. (2006). Direct Methods for Sparse Linear Systems. SIAM. https://doi.org/10.1137/1.9780898718881
- Saad, Y. (2003). Iterative Methods for Sparse Linear Systems, 2nd ed. SIAM. https://doi.org/10.1137/1.9780898718003
- Erisman, A. M. and Tinney, W. F. (1975). On computing certain elements of the inverse of a sparse matrix. Communications of the ACM 18(3), 177-179. https://doi.org/10.1145/360680.360704
- Weinert, H. L. (2007). Efficient computation for Whittaker-Henderson smoothing. Computational Statistics and Data Analysis 52(2), 959-974. https://doi.org/10.1016/j.csda.2006.11.038

Local BibTeX additions are in algorithmic_references.bib, separate from the historical Paper B bibliography. The original CSDA A/B manuscripts are unchanged.

## Audit requirements

Cite foundational work for individual algorithmic methods; explicitly prove the adaptation to the PLS difference operator; label newly combined formulas as derived upper bounds; never claim theoretical work counts are measured wall-clock times. Inspect the final CAS PDF, ensure no undefined citations, archive the source SHA and PDF hash, and obtain coauthor review before submission.


## Original-method provenance audit (November 10, 2026)

The in-manuscript algorithm provenance table is located at
sections/algorithm_provenance.tex. Distinguish three evidence levels:

1. **Original numerical method:** the paper introducing or documenting the algorithm.
2. **Computational bound:** a numerical-analysis source that actually discusses or analyzes the operation and storage requirements.
3. **PLS specialization:** arithmetic that follows from the specific order-d difference stencil, smoother, normalized smoothness inversion, candidate grid and statistical scoring; this must be explicitly derived in the new manuscript.

| Numerical method | Origin source | Complexity source and inferential boundary |
| --- | --- | --- |
| Full bidiagonal SVD | Golub and Kahan (1965), DOI:10.1137/0702016; Golub and Reinsch (1970), DOI:10.1007/BF02163027 | Standard dense rectangular complexity from Golub and Van Loan (2013). Per-series smoothness and score counts are derived in our manuscript, not in the historical SVD papers. |
| Banded Cholesky | Cholesky's posthumously documented method by Commandant Benoit (1924), DOI:10.1007/BF03031308 | Standard factorization in Golub and Van Loan (2013) and LAPACK Users' Guide (Anderson et al., 1999), DOI:10.1137/1.9780898719604. Half-bandwidth d yields O(nd^2) factorization and O(nd) storage; do not attribute the banded work theorem to 1924. |
| Dense symmetric eigenanalysis | QR eigensolver by Francis (1961), DOI:10.1093/comjnl/4.3.265 | Modern dense eigendecomposition analysis from Golub and Van Loan (2013). This cites a foundational family, not the exact implementation of every present eigensolver. |
| Sparse selected inverse | Takahashi, Fagan, Chin (1973); Erisman and Tinney (1975), DOI:10.1145/360680.360704 | Erisman and Tinney explicitly analyze dependencies and computational costs. The banded O(nd^2) result is a direct operation count for our selected entries. **Bibliographic caveat:** secondary sources disagree about Chin/Chen and Formation/Formulation for the 1973 conference paper. Verify original proceedings before submission. |
| Sparse direct factorization | Markowitz (1957), DOI:10.1287/mnsc.3.3.255, an early sparsity-conscious elimination example | Davis (2006) for fill-in, ordering, and general sparse work/storage. The bandwidth-based bound does not apply to arbitrary sparse matrices. |
| CG and PCG | Hestenes and Stiefel (1952), DOI:10.6028/jres.049.044 (original CG) | Saad (2003) for PCG and convergence. The O(qnd) bound is our cost of q order-d local matrix-vector products; preconditioner costs are additional. |
| Efficient Whittaker-Henderson/GCV | Whittaker (1923) original smoother | Weinert (2007), DOI:10.1016/j.csda.2006.11.038, provides efficient WH trend and GCV algorithms. Golub--Heath--Wahba (1979) previously developed spectral GCV. These results are prior art. |

Publisher pages confirm the publication identities and the algorithmic subjects.
The exact original textbook sections and any source-specific leading
constants need a separate pre-submission review. Some primary papers
do **not** provide the precise Big-O formula claimed for our special
difference-penalty problem; in those instances, credit them as the
method origin and display our own elementary operation-count derivation.

No archived experiments or predecessor manuscripts were altered in
this provenance update.


## Detailed Whittaker--Henderson historical corrections (primary full-text audit)

The uploaded original Howard L. Weinert (2007) article,
*Efficient Computation for Whittaker--Henderson Smoothing*,
published in *Computational Statistics & Data Analysis* 52(2):959--974,
DOI 10.1016/j.csda.2006.11.038, was read in its original PDF
(not merely as an abstract). Key material:

- **Page 959--960 / Introduction:** the paper reports that
  Bohlmann (1899) proposed the regularized least-squares graduation
  principle before Whittaker's 1923 rediscovery. It documents
  Henderson (1925) as an early WH matrix-factorization implementation.
- **Page 961 / Introduction and GCV discussion:** the work credits
  Brooks, Stone, Chan and Chan (1988) with applying cross-validation
  to WH graduation. It further reports that the efficient inverse-trace
  idea often credited to Takahashi et al. (1973) had been employed
  by Spoerl (1943). It states O(n) floating-point operations
  for fixed-order inverse-trace/WH computations.
- **Page 961 / scope statement:** Weinert thereafter restricts
  its explicit new factorization, state-space and truncated algorithms
  principally to difference order p=2. Its analysis is not a published
  proof of every arbitrary-d and nonzero-mu bound stated in our
  paper.
- **Page 973 / original bibliography:** supplies the archival
  title and pages for Bohlmann (1899), Henderson (1925) and
  Spoerl (1943). Those records are cited here via Weinert
  and should still be independently checked against the original
  archives before formal submission.
- **Brooks et al. (1988)** bibliographic metadata was independently
  corroborated through the publisher DOI
  10.1016/0167-6687(88)90097-2, *Insurance: Mathematics and
  Economics*, 7(1):59--66.

These findings require a sharper novelty statement:
**The application of cross-validation to WH smoothing and
linear-time trace computation for fixed difference order were
already established decades ago.** The present contribution may
be an integrated, explicit workload accounting over arbitrary
order, reference mean, smoothness-grid inversion, criteria and
numerical admissibility. Its originality still requires the
full specialist literature audit. In particular, do not mistake
Weinert's inverse penalty convention for the one used in
our Equation (PLS).

**Archival caveat for Takahashi (1973):** Weinert's own reference
list spells the third author *Chen*, while other numerical
analysis literature (including a Stanford bibliography and
Yousef Saad slides) spells *Chin*. Original-conference
proceedings must resolve the variant before submission.
