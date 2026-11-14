# Backup and transfer: completed Experiment011

The final dataset is on the Windows VM. No backup has been made by the chat agent; `Backup-Experiment011.ps1` must run there first. It creates a fresh directory outside the checkout, copies all Experiment011 attempts (including prior run tags/logs), Experiment006 and `src`, checks every copied file with SHA-256, and writes a final-report copy plus machine-readable provenance and file inventory. It rejects active Experiment011 Python processes and a non-2813 final checkpoint. It performs no Git staging, commits, push, pruning, deletion or benchmark execution.

This copies the relevant result and numerical-source directories, not the whole repository or Git history. The repository itself remains in GitHub. Leave the source checkout intact. The copy can be large: ensure the destination has enough free space. A partial copy on error is not verified. Store a second copy on an independent persistent disk/external location for disk-loss protection; the default same-disk destination provides protection against accidental edits only.

## Execute on the VM

After this documentation branch is published, run the following in PowerShell. Downloading this small operational script does not upload results or change the numerical checkout. Inspect it if desired. No execution-policy change is required; invoke the script in the current shell. If local policy blocks scripts, use the institution's approved method rather than changing machine policy.

```powershell
$backupScript = Join-Path $env:TEMP 'Backup-Experiment011.ps1'
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/heri-espino/trendestimation/docs/experiment011-completion-handoff/paper/benchmarks/experiment011/handoff/Backup-Experiment011.ps1' -OutFile $backupScript
& $backupScript
```

To choose another persistent disk, use `& $backupScript -BackupRoot 'D:\experiment011-backups'` after checking that drive exists. Actual output paths include a fresh timestamp. Success prints `VERIFIED COPY`, `FINAL REPORT`, `PROVENANCE` and `FILE INVENTORY`. **Do not describe a backup as complete unless that run succeeds.** Script hashes every source/copied file; do not run a benchmark concurrently. PowerShell execution is not verified by the Linux preparation session.

## Transfer and GitHub record

1. Send the printed `metadata/report.json`, `metadata/provenance.json` and `metadata/files_sha256.csv` to the analysis agent, or attach them to the conversation. These establish final job records and exact file hashes but are not a replacement for raw timings.
2. On a new documentation/results-manifest branch, commit those compact metadata files under `paper/benchmarks/experiment011/handoff/verified/` after checking sizes and reviewing machine paths. Update `VM_LOCATIONS.json` from reported/unverified to actually inspected/verified evidence. Keep source paths and reference hashes. No local-only raw files are automatically published.
3. Give a VM-capable analysis agent the accompanying prompt. It can analyze from the original tree or verified backup. A remote agent needs the full referenced raw/case/QA/environment files; arrange a compressed archive at an agreed external location with size and SHA-256 recorded in Git. Do not assume the final report alone is enough. No blanket result push or LFS quota workaround is required.
4. Preserve original/backup until the analysis and an independent-storage copy are verified. A copy within this handoff of location metadata is redundancy for instructions, not a safety copy of measurements.

The author's current choice is **no automatic publication of raw results**. Never run `git add .`, force-push, rewrite history, delete result branches, prune LFS, or recreate the repository as part of this procedure. The local `git lfs` commands returned no listed objects; a GitHub `commit_refs` error by itself did not identify an LFS quota failure.
