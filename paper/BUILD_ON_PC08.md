# Compile every manuscript on PC08

This is a **LaTeX-only, manually dispatched GitHub Actions workflow**. It
compiles the existing manuscript sources and archived figures/tables. It does
not rerender figures, redownload NGSIM data, choose smoothing parameters, run
Experiment011 or start any timing benchmark.

- Workflow: [Compile research manuscripts on PC08](../.github/workflows/compile-papers-pc08.yml)
- Builder: [scripts/build_papers_pc08.py](../scripts/build_papers_pc08.py)
- Workstation: **PCAG103A-08** (pc08), Windows x64
- Existing Conda environment: **trendestimation**
- Conda installation: C:\Users\175199\AppData\Local\miniconda3

## Run on GitHub

Navigate to **Actions → Compile research manuscripts on PC08 (Conda
trendestimation) → Run workflow**. Select **all** (default) to compile
seven source entrypoints sequentially, or select one of these IDs:

| Input | Main source | Scope |
| --- | --- | --- |
| csda-a | paper/csda-spectral-smoothness/main.tex | CSDA numerical accuracy |
| csda-b | paper/csda-computational-costs/main.tex | CSDA computational theory |
| springer | paper/main.tex | Canonical Springer Computational Statistics |
| ngsim | paper/ngsim-jerk-case-study/main.tex | Vehicle trajectory application |
| direct-weights | paper/direct-spectral-weights/main.tex | Additional theoretical draft |
| historical-springer | paper/computational-statistics-submission/main.tex | Historical full manuscript |
| historical-sncs | paper/computational-statistics-submission/sncs_main.tex | Historical SNCS draft |

The two historical entries are preserved for reproducibility, not recommended
as separate submissions. The seven LaTeX targets are compiled in one job to
avoid competing compile processes on the same machine. This workflow has
**manual dispatch only**: a push or PR does not occupy PC08.

## Existing workstation prerequisites

1. The PC08 self-hosted runner must be **online**. Its existing installation
   was designed to operate while its university Windows user is logged in.
2. The Conda executable at
   C:\Users\175199\AppData\Local\miniconda3\Scripts\conda.exe and the
   existing environment at
   C:\Users\175199\AppData\Local\miniconda3\envs\trendestimation must
   exist. The workflow uses **conda run -n trendestimation** and does not
   install or update anything.
3. The existing system TeX toolchain must expose **latexmk, pdflatex, and
   bibtex** on PATH. MiKTeX and the Perl required by latexmk are external
   to the Conda environment. A missing tool fails with a diagnostic; no
   package installation is attempted.
4. GitHub currently has evidence of standard labels
   **self-hosted, Windows, X64**, and the workflow verifies
   **RUNNER_NAME = PCAG103A-08** before proceeding. The runner name
   is *not* automatically a label. If multiple self-hosted Windows
   machines exist, assign the explicit custom label **pc08** in
   Settings → Actions → Runners and also add that label to
   the workflow's runs-on list. Without a dedicated label, another
   Windows runner could be assigned and will refuse to execute.

## Manuscript source and result isolation

CSDA A, CSDA B, NGSIM and direct spectral weights copy the exact
author-provided Elsevier CAS v2.4 class, shared style and bibliography
style from paper/els-cas-templates into the temporary checkout.
Springer entrypoints retain their existing sn-jnl class.

The builder uses **latexmk -pdf -g** (force a fresh compile),
noninteractive mode, and failure on LaTeX errors. No experiment or
figure renderer is invoked. One failure does not suppress compilation
of the other papers. Previous tracked PDFs are **never reported as a
successful new compile** when a new build fails.

An Actions artifact named
pc08-papers-(selection)-(run-id)-a(attempt) contains separate PDF and
log files for each successful attempt and a build_manifest.json listing
source commit, runner, Python/Conda paths, input SHA-256 hashes,
toolchain locations, per-paper status, timestamps and PDF SHA-256 hashes.

The workflow additionally pushes an independent, run-specific branch:

    artifacts/papers-pc08-(run-id)-a(attempt)

It commits the build manifest, logs and compiled PDFs, and updates
the repository's original manuscript PDF paths **only for successful
compilations**, on that results branch. It does not push PDFs to main
or merge any branch automatically. The Actions artifact is retained
90 days; the branch preserves build records afterward.

## Local PowerShell commands

From the repository root:

~~~powershell
conda activate trendestimation
python scripts/build_papers_pc08.py --list
python scripts/build_papers_pc08.py --paper all --dry-run
python scripts/build_papers_pc08.py --paper all --output-dir paper/builds/pc08/local001
~~~

The runner restriction is only enforced locally if you explicitly
supply --require-runner. Save local build outputs on a separate
results branch before pushing; never overwrite concurrent work.

## Validation boundary

The source-catalogue and safe dry-run tests are in
tests/test_pc08_paper_build.py. CI tests and workflow inspection do
not prove the actual PC08 MiKTeX/Perl environment can compile all
seven papers. The first successful complete workstation run and its
uploaded logs/manifest are the evidence required to make that claim.
