# Official SMCCA template provenance

The manuscript uses the **official** `smcca.cls` class supplied in the
uploaded `SMCCA_template.zip` (June 2026), not a recreated layout.

- The distributed `smcca.cls` and this repository's `paper/smcca.cls` have
  identical bytes: Git blob SHA
  `8f2642cbe1c9553e43f82f3c1e4e708b1a33d618`.
- The template selects English with `\\documentclass[english]{smcca}`.
  This is how the current `paper/main.tex` begins. The authors' common
  UDLAP affiliation, journal margins, section headings, headers, bibliography
  and float rules come from the official class.
- The official English author instructions recommend an abstract of at most
  approximately 10 lines, 4–6 keywords, centered tables with captions
  **above**, and figures with captions **below**.
- **Important submission constraint** (author instructions, section 3.3):
  Scipedia does *not* accept figures generated directly with TikZ. Export
  standalone `.pdf` or `.eps` art beforehand and include it using
  `\\includegraphics`; put the assets in `paper/figures/` where possible.

We therefore generate the statistical data using the existing
`paper/figures/make_*.py` programs, and draw all publication figures with
the **AwesomeFigures** Python package installed directly from its GitHub
repository. The git dependency is pinned in `paper/requirements.txt`.
The exported vector PDFs are then included in the manuscript with
`\\includegraphics`. This preserves the official format and keeps all
computations under `paper/`.

The uploaded archive also contains instructions, example images, and a
sample `SMCCA_template.tex` that demonstrates the class. These extra example
assets are **not** needed to compile the research manuscript and have not
been copied to the repository. The compiled `paper/main.pdf` is the
deliverable; it must still be reviewed by the authors before submission.
