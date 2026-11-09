"""Inventory every persistent VM experiment004 artifact, including raw pages.

The inventory is a readable audit index, not a substitute for copying data.
If raw NGSIM data are retained only on PCAG103A-08, their availability
depends on VM retention/access policy; keep checked-in hashes and summaries.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def create_inventory(root: Path, *, status: str, output: Path) -> dict:
    root = root.resolve()
    output = output.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Persistent run root is absent: {root}")
    dirs = sorted(
        str(p.relative_to(root)).replace("\\", "/")
        for p in root.rglob("*") if p.is_dir()
    )
    items = []
    for file in sorted(p for p in root.rglob("*") if p.is_file() and p != output):
        items.append({
            "relative_path": str(file.relative_to(root)).replace("\\", "/"),
            "bytes": file.stat().st_size,
            "sha256": sha256(file),
        })
    result = {
        "schema": 1,
        "run_status": status,
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "host": os.environ.get("RUNNER_NAME", "manual"),
        "persistent_run_root": str(root),
        "source_commit": os.environ.get("GITHUB_SHA", "manual"),
        "directory_paths_relative_to_root": dirs,
        "files": items,
        "total_files_excluding_this_inventory": len(items),
        "total_bytes_excluding_this_inventory": sum(i["bytes"] for i in items),
        "inventory_file_excluded_from_own_hashes": True,
        "data_reproducibility_note": (
            "Raw public FHWA NGSIM pages and complete scoring rows reside "
            "on persistent VM storage. The Git results branch preserves "
            "hashes, the manifest and compact analysis; it is not a "
            "byte-for-byte backup of all raw pages."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--status", default="unknown")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create_inventory(args.run_root, status=args.status, output=args.output)
    print(
        "Inventory written:", args.output.resolve(),
        "Files:", value["total_files_excluding_this_inventory"],
        "Bytes:", value["total_bytes_excluding_this_inventory"],
        flush=True,
    )


if __name__ == "__main__":
    main()
