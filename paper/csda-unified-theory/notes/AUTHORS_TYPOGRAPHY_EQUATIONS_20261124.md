**Final font compatibility decision (2026-11-24):** The current CAS v2.4 class provides an official STIX-only text/math path if the legacy `charis.sty` style is absent. Both Charis style files (`charis.sty`, `charissil.sty`) proved unavailable in the tested Ubuntu TeX package set; the build now requires `stix.sty` and uses CAS's own STIX text/math rather than Computer Modern or a custom font override. This supersedes earlier notes about explicitly loading Charis.\n\n# CSDA typography, author metadata and equation numbering — 2026-11-24

## Source of truth and scope

This change is restricted to `paper/csda-unified-theory/` and its
dedicated source-only PDF verification workflow. The user requested
official-looking fonts, identified both authors and the corresponding
author, required every **displayed** equation to be numbered, and
requested the removal of boxes. All inline `$...$` mathematical
expressions remain inline; this is appropriate in mathematical journals.

No proof statement, numerical value, inference procedure, figure data,
software estimator, experiment, algorithm complexity, or separate paper
is intentionally changed. The existing pre-submission confirmations of
funding/CRediT/competing interests remain open.

## Typography diagnosis

The archived 2026-11-23 PDF contained Computer Modern Roman math/text
fonts and several Type 3 resources. That is not the preferred **full**
Elsevier CAS v2.4 font combination: the bundled
`paper/els-cas-templates/cas-dc.cls` explicitly tests for
`stix.sty` and `charis.sty` and, if both exist, loads
`stix` for mathematics and `charis` for the main text.
Otherwise it may load STIX alone or fall back to Computer Modern;
it separately prefers Inconsolata for typewriter text.

The compiled PDF had to be rebuilt with the correct font dependencies.
The CSDA workflow now installs `texlive-fonts-extra` in addition
to its prior TeX packages and checks:
`kpsewhich stix.sty`, `kpsewhich charissil.sty`,
`kpsewhich inconsolata.sty`.
This deliberately preserves the **upstream CAS class** rather than
overriding it with an arbitrary body font. Before accepting the new
PDF, inspect `pdffonts`, the title/abstract/body, the code page,
and representative math pages. Any residual Type 3 icon glyphs
should be separately assessed; font family names and text readability
are the main check.

Upstream CAS author syntax is documented in Elsevier's official
`cas-dc-template.tex` and CAS documentation; author metadata uses
`\author[affiliation]{Name}[orcid=...]`, `\ead`,
`\cormark[1]`, `\cortext[cor1]` and `\affiliation`.

## Verified author facts supplied directly by corresponding author

- Heriberto Espino-Montelongo: corresponding author; ORCID
  0009-0009-1230-2931; email heriberto.espinomo@udlap.mx;
  Universidad de las Américas Puebla, San Andrés Cholula,
  Puebla 72810, Mexico.
- Daniela Cortés-Toto: Departamento de Actuaría, Física y Matemáticas,
  Universidad de las Américas Puebla, San Andrés Cholula,
  Puebla 72810, Mexico; ORCID 0000-0003-0893-6455;
  email daniela.cortes@udlap.mx.

No department for Heriberto was supplied in this request, so the
manuscript retains the university-level affiliation for him
and uses the department specifically for Daniela.

## Display equation audit and de-boxing

Converted **14** formerly unnumbered `\[...\]` blocks to
`\begin{equation}\label{eq:...}...\end{equation}`:
eight in the likelihood proof, one gradient derivation, three in the third-order matrix
example, one finite-difference derivative approximation, and one
candidate-count model. Two existing `\boxed{}` highlights were
removed without touching the underlying expressions. The framed
Python listing was also changed to a borderless syntax-colored
listing; existing two-column hard-margin and rotated-table checks
stay intact.

A regression test verifies the supplied author metadata,
no surviving unnumbered display delimiters (`\[`, `$$`,
starred displays), no `\boxed`/`\fbox` or framed code,
balanced equation environments, and unique equation labels.

## Validation

1. Dedicated GitHub Action: `.github/workflows/csda-unified-theory.yml`.
2. No benchmark/experiment reruns; source-only deterministic checks
   and one previously established figure reproduction.
3. Compile the official Elsevier CAS PDF, check citations and
   hard columns (`python verify_layout.py main.log`), ensure both
   rotated landscape tables remain legible, and archive the exact
   PDF/source/checksum provenance.
4. Check PDF font inventory with `pdffonts` and render multiple
   pages to confirm legibility of Charis/STIX and equation numbers.
5. CI and author review before integration.

**No journal submission.** Maintain a separate PR and do not merge
without an explicit approval for this new PR.

## Font package compatibility correction

On Ubuntu's current TeX Live distribution, the standard maintained Charis SIL LaTeX package is `charissil.sty`, while the CAS class's legacy optional test looks for `charis.sty`. Installing the complete font bundle did not satisfy that legacy test. The manuscript therefore loads `\usepackage{charissil}` explicitly after the official CAS class, which provides the intended Charis SIL text family, while the class loads STIX for mathematics. CI verifies `charissil.sty`, `stix.sty` and `inconsolata.sty`. The underlying CAS class file is unmodified.
