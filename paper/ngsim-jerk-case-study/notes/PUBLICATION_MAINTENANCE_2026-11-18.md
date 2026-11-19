# Paper C publication and workflow maintenance (2026-11-18)

This is a **maintenance-only** change to the integrated Paper C on `main`, not a new scientific experiment or journal submission. It preserves all previously committed observations, models, runs, figures, manuscripts and immutable results archives.

## Problem and correction

1. The AwesomeFigures PCAG103A-08 workflow's automatic push trigger, early branch guard and source-branch publication guard still named the old `feature/paper-c-awesomefigures-atlas` and `paper/paper-c-scientific-editorial-review` branches. The manuscript-only workflow still used `research/paper-c-experiment001-d3-recurrence` for its push trigger. Since the approved manuscript moved to `main`, both branch assumptions were stale.
2. `publication_sha256.txt` described the earlier pre-atlas manuscript and misleadingly included its older `main.pdf` hash.

Both Windows workflows are now **manual `workflow_dispatch` only**. A dispatcher must select `main` or a scoped `feature/paper-c-*`, `fix/paper-c-*` or `paper/paper-c-*` branch. Each job checks runner identity, the event and branch type, the allowed ref and the exact checked-out source SHA. This prevents automatic heavy Windows builds on future merges. Only the explicitly dispatched branch is read.

- **AwesomeFigures on `main`**: build, validate, upload artifacts and create a *unique append-only results branch*; **never push generated files to `main`**.
- **AwesomeFigures on a scoped Paper C source branch**: after successful audits, publish to that branch **only if its remote HEAD still equals the original source SHA**. If the branch advanced, skip source publication. The unique results-only archive remains a separate operation.
- **Manuscript-only workflow**: compile only on an explicit dispatch; publish a run-specific results archive, not a direct commit to `main`.
- Both retain the existing Windows runner, frozen detached Experiment006/007/008 inputs, scientific audits and archive naming. No experiment runner has been changed.

## Canonical checksum records

The previous `publication_sha256.txt` contents are copied **byte-for-byte as text** to `publication_sha256_legacy_pre_atlas.txt`; they remain historically correct for their old snapshot and are **not** the current publication fingerprint.

The new `publication_sha256.txt` covers 16 current committed files: both final PDFs, both LaTeX entrypoints, bibliography, six included section files, the original renderer, root AwesomeFigures LaTeX manifest, and the three established figure provenance manifests. Figure PDF/SVG/PNG checksums and immutable experiment input hashes remain in their **own** AwesomeFigures/visual-suite manifest files and historical results branches.

The two integrated final PDFs were independently decoded from the current GitHub `main` objects and SHA-256 checked against the final Windows build #43631207424:

| File | SHA-256 | Pages |
| --- | --- | ---: |
| `main.pdf` | `a61b70f081c48f3b98711e6d18fbd64f9f97a20772732093a08ec7c5ff56f22d` | 14 |
| `atlas_supplement.pdf` | `1f11e85758ea82130359e76f1c463a944d27765d5fb6a9e8f45bb12e38a9345b` | 12 |

To validate a checkout without running any experiments:

```powershell
python paper/ngsim-jerk-case-study/check_publication_hashes.py --check
python -m pytest tests/test_paper_c_publication_maintenance.py -q
```

**After** a separately reviewed manuscript/figure change and successful new build, explicitly refresh the active inventory, inspect the diff and commit the result:

```powershell
python paper/ngsim-jerk-case-study/check_publication_hashes.py --write
python paper/ngsim-jerk-case-study/check_publication_hashes.py --check
```

A missing asset or mismatched hash fails closed; `--check` never modifies files. The current 16-file manifest is an **integrated publication snapshot**, not the historical exhaustive simulation inventory. This maintenance does not rerender images, recompile the manuscript, alter numerical conclusions, or rewrite historic archives.

## Next-agent workflow

Read `AGENTS.md`, `paper/AGENTS.md`, `paper/ngsim-jerk-case-study/README.md` and `NEXT_AGENT_COMPREHENSIVE_HANDOFF_2026-11-18.md` before scientific or editorial changes. Use a fresh Paper C branch from current `main`. Check or update checksum inventory only when publication assets change. The newer user's explicit standing permission authorizes **validated maintenance PR merges**, but prohibits unverified merges and requires a separate authorization for journal submission. All Experiments004–008 remain frozen.

This note documents maintenance; no new experiment number has been allocated.
