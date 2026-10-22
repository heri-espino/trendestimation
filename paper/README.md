# Computational Statistics manuscript — Springer Nature

This directory contains an **unsubmitted working draft** of the scientific
paper describing the `trendestimation` Python library. The intended venue
is **Computational Statistics** (Springer Nature, ISSN 0943-4062).
This is distinct from *Computational Statistics & Data Analysis* (Elsevier).

## Official December 2024 template

- `main.tex` uses `\documentclass[pdflatex,sn-mathphys-ay]{sn-jnl}`.
- `sn-jnl.cls` and `sn-mathphys-ay.bst` were checked against the author's
  uploaded December 2024 Springer Nature ZIP, **byte-for-byte** by Git blob hash:
  `d25f07cb51c685e90a4ab97e95479826289486d4` and
  `35533152b3a21c47815f2fe194fef46285c4ccd8` respectively.
- The style is **author–year**, consistent with the journal's instructions.
- The scientific model, mathematics, figures and experiments are inherited
  from the earlier paper; no new measurements were invented in changing venue.
- Previous SMCCA-specific entrypoint: `legacy_smcca_main.tex`. Original
  documentation: `README_SMCCA.md`; old `smcca.cls` is untouched.

Journal instructions: https://link.springer.com/journal/180/submission-guidelines

## Build

From repository root with your existing `trendestimation` conda environment:

```powershell
python -m pip install -e .
python -m pip install -r paper/requirements.txt
python paper/build.py
```

This creates `paper/main.pdf` using Springer Nature's `sn-jnl` class. It
generates deterministic synthetic, observational and higher-order data and
uses [AwesomeFigures](https://github.com/awesomefigures/awesomefigures) to
render standalone vector PDFs. Its `af.latex_style()` probes **the current
paper/main.tex**, not the old SMCCA document, so figure text sizes and
fonts follow the new class's physical layout. Requires `latexmk`,
`pdflatex`, and `bibtex` (e.g. MiKTeX).

To reuse results from an existing Windows benchmark run:

```powershell
python paper/build.py --render-figures --pdf --package
```

For a full fresh run, including costly benchmarks and packaging:

```powershell
python paper/build.py --all --benchmark-preset full --repeats 7
```

Additional steps:

| Flag | Effect |
| --- | --- |
| `--figures` | Regenerate deterministic data and publication figures. |
| `--render-figures` | Redraw using existing data; do not rerun experiments. |
| `--benchmarks` | Run full-fit and trace performance comparisons. |
| `--tables` | Regenerate benchmark tables from measured CSVs. |
| `--pdf` | Compile PDF from existing data/figures. |
| `--package` | Produce a **flat** Springer submission ZIP using existing PDF and LaTeX sources. |
| `--all` | Full reproducible figures + benchmarks + PDF + submission ZIP. |
| `--dry-run` | Show commands without writing files. |
| `--clean` | Clean LaTeX outputs, preserve experimental results. |

## Switching from the previous SMCCA / Boletín build

PR #29 already merged the Springer Nature `sn-jnl` manuscript into `main`.
If you still see a Boletín header, update your *local checkout*:

```powershell
git switch main
git pull --ff-only origin main
Select-String -Path paper/main.tex -Pattern 'documentclass'
python paper/build.py --pdf
```

The correct class declaration is
`\documentclass[pdflatex,sn-mathphys-ay]{sn-jnl}`.

When switching from `smcca.cls` and the old numeric `abbrv` bibliography,
the old `paper/main.aux` can contain `\NAT@force@numbers{}`. Springer
uses the author--year `sn-mathphys-ay` bibliography, so that stale auxiliary
file makes `pdflatex` fail *before* BibTeX can refresh citations.
The compiler now detects this mismatch automatically and removes only
the obsolete LaTeX/BibTeX auxiliary files. It preserves all numerical data,
benchmarks, figures and the previous PDF until the next successful compile.
You do not need to rerun `--all` merely to switch journal format.

If you inspect an old PDF after a successful build, ensure you open
`paper/main.pdf` (not an old downloaded copy of the SMCCA manuscript).

## Springer float and generated-table compatibility

The old SMCCA manuscript used forced `[H]` placement for tables and figures
and embedded a generated `tabular` source inside `\\resizebox{...}{...}{\\input{...}}`.
Both patterns can fail with the official Springer Nature `sn-jnl.cls`
(`Extra }, or forgotten \\endgroup` at `\\end{table}`).

The Springer version uses standard `[tbp]` placement and inputs
`full_fit_table.tex` and `trace_table.tex` directly. Their measured
numerical values, generated CSVs, and caption text are unchanged.
A regression test checks both the LaTeX source and (when available)
a minimal real `pdflatex` compile against the official class.

To resume after updating `main`:

```powershell
git switch main
git pull --ff-only origin main
python paper/build.py --pdf --package
```

The `--pdf` step reuses existing vector figures, benchmark tables,
and measured data. Undefined-citation warnings on the *first* LaTeX pass
are expected; `latexmk` runs BibTeX and the subsequent LaTeX passes.

## Flat submission source ZIP

The journal explicitly states: **do not upload LaTeX sources in subfolders**.
Running

```powershell
python paper/build.py --package
```

produces `paper/computational-statistics-submission.zip`. It includes
`main.tex`, `main.pdf`, `bibliografia.bib`, the official `.cls`
and `.bst`, referenced `sections/*.tex`, optional generated LaTeX timing
tables, and referenced vector `.pdf` figures, all **flattened at ZIP root**.
A reference-rewriting pass makes the flattened sources self-contained.
The packager checks template blob hashes, missing files and potentially
stale PDF outputs. It does **not** include ignored numeric benchmark CSVs
or private/local data by default. Consider archiving verified raw benchmark
results separately for research reproducibility.

## Journal requirements and remaining author approvals

Computational Statistics' online instructions request a 150–250 word
abstract, 4–6 keywords, author–year citations and editable LaTeX source.
The current paper includes an abstract and five keywords, and introduces
a `Declarations` section.

**Before any submission, the authors must verify and complete:**
corresponding-author email; affiliations; funding; competing interests;
author contributions; research data and code availability, ideally with
an archived code release and stable DOI; publication ethics statements;
permissions if any third-party figure is reused; novelty and statistical
significance relative to recent work. Placeholders have intentionally
not been filled with unverified statements.

The **computational** focus is critical: assess numerical stability,
setup vs repeated-use costs, scaling and hardware effects carefully.
Specialized banded solvers often outperform SVD for full fitted curves.
The work should not claim that existing Whittaker--Henderson methods,
penalized least squares, or standard cross-validation are newly invented.

The existing timing data generated by the author are in the ignored
`paper/benchmarks/results/`. Use `paper/benchmarks/README.md` for
experiment methodology and provenance. Heavy GitHub Actions continue to
run **only via manual workflow_dispatch**; regular CI is limited to tests.

Original template readme and full article authoring manual are supplied
in the uploaded Springer Nature December 2024 ZIP; the manuscript
repository stores the verified build-critical `.cls` and `.bst`.
