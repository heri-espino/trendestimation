# AGENTS.md — trendestimation repository agent guidance

This repository is the source of truth. Inspect root README.md, relevant
manuscripts, notes, source code, experiments, existing tests and current
GitHub branches/PRs before editing. Never assume chat results supersede
saved numerical output or code.

## Research conventions

- The public Python library implements finite-difference penalized
  least-squares trend estimation. The two CSDA drafts live under
  paper/csda-spectral-smoothness/ (statistical/numerical) and
  paper/csda-computational-costs/ (algorithmic time costs).
- Normalized smoothness S in [0,1] is the interpretation presented to
  users; lambda is the internal, bijectively related penalty coordinate
  for fixed n and d.
- Distinguish numerical fit error against independent same-parameter
  multiprecision truth, statistical latent-trend RMSE, and genuine
  chronological forecast RMSE. These are NOT interchangeable.
- Distinguish fixed mu and observed-difference plug-in mu; the latter
  is not joint maximum likelihood and classical conditional CV is not
  re-estimated in every deletion for that plug-in.
- Full SVD is the current library default for demonstrated numerical
  stability; it is NOT guaranteed to be the universally fastest solver.
- Prior art includes Guerrero (2007), Cortes-Toto et al. (2017),
  Weinert (2007), and Biessy (2026); maintain appropriate attribution.
- Treat undefined criterion boundaries (notably RSS BIC at S=0),
  numerical solver failures, and incomplete grids as DISTINCT statuses.
- Do not present independently sampled log-lambda grids as matched
  competitors to a user-facing full S grid.

## Experiment and branch discipline

- Use sequential experiment numbers, preserving all previous data.
  Latest joint study: paper/benchmarks/experiment005/.
- Each experiment must contain its question, methods, source,
  reproducibility command, raw numerical results, environment metadata,
  analysis, findings and next steps. See experiment005/README.md and
  HANDOFF.md. Save SHA256 hashes where practical.
- Always use new unique run directories; never overwrite archived runs.
  Preserve numerical failures, not just successful rows.
- Separate smoke/validation pilots from publication-grade independent
  timing studies. Compare runtimes on one identified host with recorded
  BLAS settings, never by mixing raw milliseconds from different CPUs.
- Use a feature branch and PR; respect other agents and do not merge
  concurrent branches without authorization. Never force push.
- Commit and push completed work, source, configurations, tests, notes,
  figures and results. Use Git LFS or documented external storage for
  unusually large datasets. Do not commit secrets, licensed PDFs or
  raw datasets without redistribution rights.
- Maintain this guide and the experiment-specific handoff when
  experimental conclusions or workflows change.
