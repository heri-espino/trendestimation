#!/usr/bin/env python3
"""Write Paper C's publication SHA-256 ledger using canonical Git bytes.

On the Windows PC08 runner, Git may check out text files with CRLF line endings.
The published PDF, by contrast, is a new working-tree binary.  This helper
hashes all *existing tracked sources* via `git show HEAD:<path>` (Git LF bytes)
and only the newly compiled `main.pdf` from the working tree.  The resulting
inventory passes the normal Linux CI check after the PDF and ledger are committed.

Use only after a successful LaTeX-only build from exactly the checked-out SHA:
  python paper/ngsim-jerk-case-study/write_publication_hashes_from_git.py
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess

from check_publication_hashes import INVENTORY, REQUIRED, ROOT

REPOSITORY = ROOT.parent.parent


def current_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPOSITORY
    ).decode("ascii").strip()


def git_source_bytes(relative: str) -> bytes:
    path = "paper/ngsim-jerk-case-study/" + relative
    return subprocess.check_output(
        ["git", "show", "HEAD:" + path], cwd=REPOSITORY
    )


def main() -> None:
    source_commit = current_commit()
    expected_commit = os.environ.get("GITHUB_SHA")
    if expected_commit and source_commit != expected_commit:
        raise RuntimeError("Checked-out revision differs from the workflow SHA")

    pdf = ROOT / "main.pdf"
    if not pdf.is_file() or pdf.stat().st_size < 100:
        raise FileNotFoundError("A newly compiled Paper C PDF is required")

    entries = []
    for relative in sorted(REQUIRED):
        data = pdf.read_bytes() if relative == "main.pdf" else git_source_bytes(relative)
        entries.append(f"{hashlib.sha256(data).hexdigest()}  {relative}")

    INVENTORY.write_text("\n".join(entries) + "\n", encoding="utf-8", newline="\n")
    print(f"Canonical Git-blob source inventory: {len(entries)} entries")
    print(f"Source revision: {source_commit}")
    print(f"Integrated PDF SHA-256: {hashlib.sha256(pdf.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
