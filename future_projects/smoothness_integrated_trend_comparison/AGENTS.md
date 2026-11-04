# AGENTS.md — future project: smoothness-integrated trend comparison

## Start here
Read this file, [README.md](README.md), [trend_comparison_two_column.tex](trend_comparison_two_column.tex), the repository [README](../../README.md), [notes/smoothness_parameterization.md](../../notes/smoothness_parameterization.md), and the current [notes/README.md](../../notes/README.md) before modifying this proposal. Inspect the active manuscript and open PRs before changing shared code or files.

## Status / non-goals
This directory contains a **future project**, not a delivered or validated package feature. Do not edit the published library API, active manuscripts, unrelated experiments, Sphinx theme, or other agents' branches as part of a documentation-only change. Avoid causal-detection claims derived from full-series smoothing.

## Mathematical conventions
Use `y` for the observations; `N` sample size; `D_d` finite-difference matrix; `Q=D_d^T D_d`; `H_lambda=(I+lambda Q)^-1`; and `S in [0,1]` for normalized smoothness, with its exact endpoints. Use `tau` for trends, `mu` for target d-th difference drift, and `mu_Delta` for signed mean **between** trend levels. Explicitly distinguish nonzero drift from nonzero mean difference. Restrict the mean-preservation result to the appropriate difference operators `d>=1`.

## Reproduction / extension policy
- Build the standalone `trend_comparison_two_column.tex` with `latexmk -pdf -outdir=build -interaction=nonstopmode -halt-on-error -file-line-error trend_comparison_two_column.tex` in this folder. Source must remain tracked; local auxiliary build files are ignored.
- Future research experiments belong under `experiment001/`, `experiment002/`, etc., not date-based folders. Each includes what/why, full commands, environment, deterministic seeds, tests, inputs or provenance, outputs, interpretation and failures, and recommended next actions.
- Persist all meaningful runs (including numerical CSVs, plots, reproducibility logs, and results) into the repository before ephemeral VM shutdown. Never represent unrun proposed experiments as completed.
- Benchmark against raw rolling RMS, single-smoothness distances, and explicit change-point baselines; report onset uncertainty and false-alarm rates, and distinguish causal versus retrospective smoothing.
- Heavy document builds / experiments should remain **manual**, consistent with existing repository workflow; do not add automatic heavy Actions runs.
- Work on a dedicated branch and PR; **do not merge without explicit authorization**.
