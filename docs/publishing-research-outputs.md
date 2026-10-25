# Publishing locally generated research outputs to GitHub

This workflow is for the **author's own Windows/Linux/Mac checkout**.
ChatGPT and GitHub Actions cannot read unpublished files on your computer.
The repository intentionally ignores experimental datasets, LaTeX build
output and Marp exports by default.

## Recommended Windows PowerShell workflow

First update the code, then use a **read-only preview**:

~~~powershell
conda activate trendestimation
git switch main
git pull --ff-only origin main
python scripts/publish_generated_outputs.py
~~~

The preview lists precisely which local files can be included.
It does not modify your checkout or open a PR.

To publish all eligible local generated files:

~~~powershell
python scripts/publish_generated_outputs.py --publish
~~~

The command creates and pushes a new branch named
`results/local-research-YYYYMMDD-HHMMSS`. If GitHub CLI
(`gh`) is authenticated, it also opens a pull request;
otherwise it prints the GitHub link where you can open it manually.

**Do not use** `git add -A` or `git add -f .` as a substitute:
doing so can accidentally publish copyrighted papers, private files,
unrelated experimental results, or enormous build caches.

## What is included

- Scientific outputs from `paper/benchmarks/solver_study_runs/`:
  raw CSV, numerical accuracy, metadata JSON, statistical comparisons,
  LaTeX tables, SVG/PNG/PDF plots, and Markdown reports.
- Previous full-fit and trace benchmarks in `paper/benchmarks/results/`.
- Generated scientific figures under `paper/figures/`.
- The generated manuscript `paper/main.pdf`, when present.
- Generated slides `slides/professor_lecture/main.pdf`,
  `main.html`, `main.pptx` and `slides/professor_lecture/figures/`,
  when present.

If your benchmark was saved under `build/solver-study/` or
`build/formal-solver-study/`, the utility copies the results into a
new, timestamped directory under
`paper/benchmarks/solver_study_runs/local-import-*/`
before staging. No existing study data is overwritten.

For another study directory, including a folder outside the checkout:

~~~powershell
python scripts/publish_generated_outputs.py --from-dir "C:\path\to\my\solver-study"
python scripts/publish_generated_outputs.py --publish --from-dir "C:\path\to\my\solver-study"
~~~

Each explicitly imported directory must contain
`raw_measurements.csv` and `study_metadata.json`.
The publication manifest records relative paths, SHA-256 hashes
and the source code revision. It is a provenance record, not an
independent validation of the reported numerical conclusions.

## Deliberately excluded

- Original literature PDFs, third-party downloaded content, datasets
  outside explicitly allowed output folders, credentials, `.env` files,
  Python/LaTeX caches and virtual environments.
- Files larger than 50 MiB (use Git LFS or an external archive).
- Source modifications or pushes to the ongoing Marp branch.
- Journal submission, publishing on PyPI or creating a formal software
  release. **This archives measured research output to GitHub only.**

The new results branch/PR makes it possible to review provenance,
file sizes, numerical correctness and privacy before merging.

## Verify local evidence first

~~~powershell
Test-Path paper/benchmarks/solver_study_runs/pilot-01/raw_measurements.csv
Test-Path paper/benchmarks/solver_study_runs/pilot-01/analysis/results.md
python scripts/publish_generated_outputs.py
git status --short
~~~

If those first checks are false, the benchmark or analysis has not
created the required files **at that location**. The publisher
archives only real files; it never invents times or p-values.

After a results PR is merged, future agents can inspect the same
raw data and statistical reports directly in the repository.
Hardware-specific speedup measurements should still be independently
replicated before making general publication claims.
