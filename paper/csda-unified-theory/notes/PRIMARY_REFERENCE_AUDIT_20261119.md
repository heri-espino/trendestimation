# Original-paper citation audit: eleven user-supplied PDFs

Date: 2026-11-19. Scope: the **unified CSDA theory** article. The original
files were inspected as primary references; the manuscript cites them but
DOES NOT copy copyrighted PDFs to GitHub. This is a bibliographic and
claim-to-source audit, **not** a new numerical experiment.

| Supplied PDF | Primary-paper bibliographic identity and checked location | How the manuscript uses it | Citation disposition |
| --- | --- | --- | --- |
| `360680.360704.pdf` | A. M. Erisman and W. F. Tinney, **1975**, *On Computing Certain Elements of the Inverse of a Sparse Matrix*, CACM **18(3)**, 177–179, DOI **10.1145/360680.360704**. Pp. 177–178, Eqs. (2)–(4), dependency theorem and cost section. | Selected-inverse recurrence; specifically selected entries/diagonal without forming all of inverse. The fixed-band O(nd²) is our specialization/count, not asserted to be their general theorem. | **Retain existing** `erisman1975`; cite beside inverse recurrence and implementation. |
| `Ubaru-2017-fast.pdf` | Shashanka Ubaru, Jie Chen, Yousef Saad, **2017**, *Fast Estimation of tr(f(A)) via Stochastic Lanczos Quadrature*, SIAM J. Matrix Anal. Appl. **38(4)**, 1075–1099, DOI **10.1137/16M1104974**. First two published pages + sections on SLQ/log determinants. | Monte Carlo/Lanczos **approximation** to traces of matrix functions including log determinant; not an exact LOOCV leverages algorithm. | **Add** `ubaru2017` to local bibliography and approximate-diagnostic subsection only. |
| `commun90.pdf` | M. F. Hutchinson, **1990**, *A Stochastic Estimator of the Trace of the Influence Matrix for Laplacian Smoothing Splines*, Communications in Statistics—Simulation and Computation **19(2)**, 433–450, DOI **10.1080/03610919008812866**. Scanned first page (433), pp. 435–438 derivation of unbiased estimator. | Random-probe stochastic trace estimate for influence/smoothing matrix, **not** an exact trace or leverage vector. | **Add** `hutchinson1990`. **Correct prior suggestion 1989 → 1990**; an apparently different earlier online record has an alternate DOI, but the supplied original published issue has 1990/19(2)/433–450. |
| `Reinsch1967_Article_SmoothingBySplineFunctions.pdf` | Christian H. Reinsch, **1967**, *Smoothing by Spline Functions*, Numerische Mathematik **10**, 177–183, DOI **10.1007/BF02162161**. Pp. 177–180, constrained integrated-square-second-derivative problem and subsequent five-diagonal/Cholesky banded system. | Continuous smoothing-spline regularization antecedent. **Not** the same discrete difference penalty `D_d`. | **Add** `reinsch1967`, cite in introduction. |
| `CG-orginal.pdf` | Magnus R. Hestenes and Eduard Stiefel, **1952**, *Methods of Conjugate Gradients for Solving Linear Systems*, J. Res. National Bureau of Standards **49(6)**, 409–436, DOI **10.6028/jres.049.044**. Pp. 409–411 Sec. 3. | Original conjugate-gradient method; no PCG performance/iteration guarantee for our special matrix is attributed to this paper. | **Retain** `hestenesstiefel1952`; cite original Section 3. |
| `1916461.1916464.pdf` | Lin Lin, Chao Yang, Juan C. Meza, Jianfeng Lu, Lexing Ying and Weinan E, **February 2011**, *SelInv—An Algorithm for Selected Inversion of a Sparse Symmetric Matrix*, ACM TOMS **37(4)** Article **40**, pp. 40:1–40:19, DOI **10.1145/1916461.1916464**. Article pp. 40:1–40:4 introduces supernodal LDLT selected inversion and Takahashi/Erisman–Tinney lineage. | Modern implementation of **general sparse** selected inverse; NOT the original invention of recurrence or guarantee of our **banded** O(nd²). | **Add** `lin2011`, cite explicitly next to Erisman–Tinney. |
| `HP_ACM.pdf` | Adriana Cornea-Madeira, **2017**, *The Explicit Formula for the Hodrick–Prescott Filter in Finite Sample*, *The Review of Economics and Statistics* **99(2)**, 314–318, DOI **10.1162/REST_a_00594**. Repository cover says 2017 published; manuscript inner cover says January 2016 preprint. Original pp. 2–6 defines d=2 HP filter and alternate finite-sample matrix formula/algorithm. | The d=2, mu=0 special case and alternative exact finite-sample computation. **Do not imply that this paper SVD-factorizes our D**. | **Add** `corneamadeira2017`, cite in introduction and provenance. |
| `cravenwabha79.pdf` | Peter Craven and Grace Wahba, **1979**, *Smoothing Noisy Data with Spline Functions: Estimating the Correct Degree of Smoothing by the Method of Generalized Cross-Validation*, Numerische Mathematik **31**, 377–403, DOI **10.1007/BF01404567**. P. 380 Eq. (1.9), GCV defined through influence matrix and trace. | Original smoothing-spline GCV. | **Retain** shared `craven1979`; cite at GCV formula. |
| `golub.heath.wahba.pdf` | Gene H. Golub, Michael Heath and Grace Wahba, **May 1979**, *Generalized Cross-Validation as a Method for Choosing a Good Ridge Parameter*, Technometrics **21(2)**, 215–223, DOI **10.1080/00401706.1979.10489751**. P. 216 Eq. (1.4), pp. 216–217 SVD analysis. | Original ridge regression GCV and SVD-based computation; not a proof of this paper's entire grid-workload complexity formula. | **Retain** shared `golub1979`; cite at GCV formula/provenance. |
| `Golub+Reinsch-NM-1970.pdf` | Gene H. Golub and Christian Reinsch, **1970**, *Singular Value Decomposition and Least Squares Solutions*, Numerische Mathematik **14**, 403–420, DOI **10.1007/BF02163027**. **P. 404** explicitly warns of unnecessary numerical inaccuracy when forming `A^T A` and provides a small-matrix example. | Original practical SVD method and **direct evidence for avoiding Gram-matrix formation**; does not establish universal runtime speed. | **Retain** existing `golubreinsch1970`; cite specifically p. 404 for conditioning. |
| `GlbKhnSv.pdf` | Gene H. Golub and William Kahan, **1965**, *Calculating the Singular Values and Pseudo-Inverse of a Matrix*, J. SIAM Series B Numerical Analysis **2(2)**, 205–224, DOI **10.1137/0702016**. Pp. 205–208 bidiagonalization concept. | Historical origin of bidiagonal SVD computation; arithmetic complexities for general dense matrices use later textbooks, not imputed to this original paper. | **Retain** `golubkahan1965`, cite as method origin only. |

## Audit rules and unresolved priorities

1. **No duplicate BibTeX entries** for prior keys already in
   `paper/csda-computational-costs/references.bib` or the local
   `algorithmic_references.bib`. Five newly useful papers are added only
   to the latter: Reinsch, Cornea-Madeira, Lin et al., Hutchinson, Ubaru et al.
2. The exact-method algorithm table retains its original references.
   The added papers are cited in appropriate text or provenance notes,
   and **stochastic** trace/log-determinant alternatives have their own
   subsection explicitly excluded from the exact cost theorems.
3. All assertions are limited to the printed original papers.
   The **2016 date inside Cornea-Madeira's manuscript is not the 2017
   journal publication date**, and **Lin's 2010 style-template example
   is not its printed February 2011 publication date**.
4. **Important Hutchinson correction:** the uploaded 1990 printed issue
   is authoritative. The DOI for the 1990 issue is
   10.1080/03610919008812866 (publisher metadata verified).
5. The special d=2 HP result, continuous Reinsch spline problem, exact
   GCV, selected inversion, and Monte Carlo trace estimates are
   **distinct methods**. Their presence in a citation list does not
   prove equivalence, a new priority claim, or measured speedups.
6. No copyrighted scans are committed, only author-created summaries
   and bibliographic metadata. Compilation must report no
   undefined or multiply defined bibliography keys and include the
   correct citation labels in the final PDF.
