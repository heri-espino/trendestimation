# Agent instructions: unified CSDA theoretical manuscript

Read repository README.md, AGENTS.md, AI_HANDOFF.md, paper/AGENTS.md, paper/PUBLICATION_MAP.md and paper/SESSION_HANDOFF.md before modifying this manuscript. Also read this directory's README, all its sections and deterministic checks, both source CSDA papers, and the editorial literature audit.

## Ownership and concurrency
Work only in an independent feature branch and an appropriate PR. This folder is the new theoretical canonical source; preserve all material under paper/csda-spectral-smoothness, paper/csda-computational-costs, paper/benchmarks, paper/main.tex and paper/ngsim-jerk-case-study. Separate agents own the Springer timing tensor and the applied vehicle paper. Do not rerun Experiment011 or any large prior benchmark. Do not merge without explicit author approval.

## Mandatory scientific contracts
- Objective: squared residuals + lambda times squared order-d differences centered on fixed numeric mu.
- Fixed nonzero mu is an established Guerrero feature, not a newly invented penalty. Mu=data is conditional plug-in; it is not a jointly estimated mean in the core proofs.
- Conditional normalized S=(n-tr(H))/(n-d), with exact 0/interpolation and 1/constrained-polynomial endpoints. Old trace/n index has upper bound 1-d/n.
- The eigenvalues, inverse S map and H depend only on n,d,lambda, not a fixed mu or observed series.
- Do not report an independently spaced log-lambda grid as the same candidate search as an S grid.
- Fixed-mu leverage and EDF do not give exact foldwise refit for a data-dependent mean.
- Keep exact CV/GCV/AICc/residual BIC/likelihood definitions. Disclose residual BIC's interpolation pathology.
- Include every mapping, factorization, selected inverse, determinant, projection and scoring cost before identifying a cheap pipeline.
- Arithmetic O bounds are not measured runtime. SPD existence does not guarantee finite-precision correctness. Distinguish factorization, KKT, S-inversion, memory and undefined-score failure mechanisms.
- The Python package does not implement every proposed theoretical auto-dispatch policy.

Preserve all TeX source, scripts, tests, PDF, compilation logs and checksums. Name new experiments sequentially and include purpose, methodology, outputs, reproduction, findings and next steps if a new experiment is authorized. Never delete prior numerical evidence or overwrite other agents' work. Before publication verify all proofs and citations directly against original papers; obtain coauthor approval.
