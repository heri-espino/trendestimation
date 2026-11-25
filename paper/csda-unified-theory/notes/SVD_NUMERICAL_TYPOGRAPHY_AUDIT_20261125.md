# CSDA numeric SVD, notation, captions and cross-references — 2026-11-25

## Background and user-requested corrections

The first figure in the 19-page merged CSDA source printed only
`D_3` and `D_3^T D_3`, making the principal **rectangular SVD**
contribution less visible. The published PDF also rendered the wide
figure and one table caption with Type 3 bitmap text, while other
captions used STIX. Equation (2) had cramped, visually inconsistent
real-number and arg-min typography. The user requested a numerical
SVD/inverse verification, uniform caption fonts, double-stroke
real numbers with `mathds`, nabla rather than delta notation,
an H-first introduction, and explicit textual references to all
figures/tables.

## Changes, mathematics and exact numerical ground truth

- `D_3` is **the original** 3×6 full-row-rank matrix with rows
  [-1,3,-3,1,0,0], [0,-1,3,-3,1,0], [0,0,-1,3,-3,1].
- Its reduced SVD has positive singular values
  6.66515456, 3.74165739, 1.25527476, in descending
  order. The numerical entries of U and V^T in the
  manuscript are rounded, so do **not** multiply the
  printed values and claim machine-precision equality;
  the Python regression uses the full-precision SVD.
- The **exact** smoother at lambda=1 is
  H=(I+D^T D)^(-1)=I−V diag(sigma²/(1+sigma²)) V^T
  = (1/195) times the symmetric integer matrix printed
  in `sections/third_difference_example.tex`.
  Its (1,6) entry equals 11/195 despite Q being banded.
- For y=(0,2,0,1,3,2)^T, lambda=mu=1, direct normal
  equations and the **nonzero-reference shift-free SVD**
  return (14,238,243,238,308,519)^T / 195.
  The proof is the existing `eq:shiftfree`, not a new theorem.
- `tests/test_d3_numeric_svd.py` independently checks
  reconstruction, singular values, exact H, far off-diagonal,
  nonzero reference at multiple penalties and references,
  and printed four-decimal singular-vector magnitudes.
- The source standardizes the *discrete difference*
  symbol to `\\nabla` with correct **backward-difference
  right-endpoint indexing**, while the positive penalty
  eigenvalue symbols `\\delta_j` were renamed
  `\\rho_j=\\sigma_j^2` to avoid overloading nabla.
  `\\nabla_\\tau` still denotes the ordinary gradient,
  distinguished by its subscript.
- In `main.tex`: `\\usepackage{dsfont}`;
  `\\newcommand{\\R}{\\mathds{R}}`; the PLS arg-min
  is `\\operatorname*{arg\\,min}`. H is defined before
  the normal matrix A in the initial assumptions
  and the model derivation; A remains the positive-definite
  linear system for numerical solution.
- `helvet` provides a scalable Type-1 sans font for the
  native CAS `\\sffamily\\small` captions. The
  `\\captionof{figure}` and the rotating-table
  captions now explicitly use the same local font family
  and size (the locally applied `\\footnotesize` produces
  the same 8.52-pt embedded caption size as the
  CAS `figure*`/`table*` `\\small` setting).
  Native CAS captions already request this family/size. Figure/table body
  formatting and original source labels are preserved.
- All **five** floating labels have a corresponding
  contextual `\\ref{fig:...}` or `\\ref{tab:...}`
  in narrative prose. The original synthetic Gaussian
  figure and all tables are unchanged numerically.

## Compatibility and scientific restrictions

- This is one **worked numerical example**, not a new
  benchmark campaign; do not allocate an experimentNNN
  label or claim a timing improvement.
- The SVD numerical basis signs are arbitrary. The
  exact results use the full basis, not rounded printed
  factors; retain full positive spectrum.
- Do not infer a Gaussian uncertainty-quantification
  advantage, forecasting ability, or SVD timing dominance
  from the toy six-point example.
- A nonzero fixed mu uses a **different affine part**
  of the fitted trend, so `H y` alone is not the
  general estimate.
- Other project papers, tests, source assets, experiments,
  figures, declarations, bibliography and coauthors'
  identities must remain unmodified.
- The user's request does not itself authorize
  merging this new PR or submitting to CSDA.

## Reproduce and verify

```bash
python paper/csda-unified-theory/verify_theory.py
python paper/csda-computational-costs/verify_theory.py
python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_*.py' -v
```

The dedicated source-matched CAS compilation workflow
must (1) have `dsfont.sty`, `helvet.sty`, and `stix.sty`;
(2) build a complete PDF with all figure/table citations;
(3) detect any remaining Type 3 caption text using
`pdffonts` and the exact caption pages; (4) pass the
strict no-overflow body-column check and PDF-native
sideways table rotations; (5) archive source, PDF,
figure, log, hashes and the present note; and
(6) inspect the first mathematical page, the numeric
SVD figure, both landscape tables and inline figure
caption at useful zoom.

Do not represent a local or prior-turn PDF as a
source-matched final build of this PR.
