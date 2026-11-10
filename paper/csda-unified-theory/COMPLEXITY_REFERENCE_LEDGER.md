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
