"""Safely publish generated trendestimation research outputs from a LOCAL checkout.

Run in PowerShell from the repository root:

    python scripts/publish_generated_outputs.py
    python scripts/publish_generated_outputs.py --publish

The default is a read-only preview. --publish creates a unique results
branch, commits *only allowlisted generated research artifacts*, pushes
to origin, and offers/creates a pull request. No main/Marp source changes.

Why this exists: benchmark outputs, generated paper PDFs, and Marp exports
are intentionally gitignored and cannot be uploaded from ChatGPT; they
must be committed on the machine that actually produced them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "heri-espino/trendestimation"
MAX_FILE_BYTES = 50 * 1024 * 1024  # Avoid GitHub >100 MiB rejection.

# Restrict uploads to *generated research outputs*. Never stage the root,
# "sources/", .env files, private data, temp files or licensed PDFs.
DIRECTORY_ALLOWLIST = {
    "paper/benchmarks/solver_study_runs": {
        ".csv", ".json", ".md", ".tex", ".dat", ".svg", ".png", ".pdf",
    },
    "paper/benchmarks/results": {
        ".csv", ".json", ".md", ".tex", ".dat", ".svg", ".png", ".pdf",
    },
    "paper/figures": {".pdf", ".svg", ".png", ".dat"},
    "slides/professor_lecture/figures": {".svg", ".png", ".pdf", ".json"},
}
FILE_ALLOWLIST = (
    "paper/main.pdf",
    "slides/professor_lecture/main.html",
    "slides/professor_lecture/main.pdf",
    "slides/professor_lecture/main.pptx",
)
# Ignore hidden files even if extension looks compatible.
BANNED_NAMES = {"secrets.json", "credentials.json", "token.json"}
DEFAULT_IMPORT_SOURCES = (
    "build/solver-study", "build/formal-solver-study",
    "build/solver-study-smoke",
)


def run_git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True, capture_output=True,
    )
    return completed.stdout.strip()


def is_allowed_file(path: Path, root: Path = ROOT) -> bool:
    """Reject symlinks, secrets and files outside explicitly approved paths."""
    if not path.is_file() or path.is_symlink():
        return False
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
        return False
    if path.name.casefold() in BANNED_NAMES:
        return False
    logical = relative.as_posix()
    if logical in FILE_ALLOWLIST:
        return True
    for prefix, extensions in DIRECTORY_ALLOWLIST.items():
        if logical.startswith(prefix + "/") and path.suffix.lower() in extensions:
            return True
    return False


def discover_publishable(root: Path = ROOT) -> list[Path]:
    """Read-only discovery of generated, explicitly allowed local artifacts."""
    collected: list[Path] = []
    for rel, extensions in DIRECTORY_ALLOWLIST.items():
        parent = root / rel
        if parent.is_dir() and not parent.is_symlink():
            for path in parent.rglob("*"):
                if path.suffix.lower() in extensions and is_allowed_file(path, root):
                    collected.append(path)
    for rel in FILE_ALLOWLIST:
        path = root / rel
        if is_allowed_file(path, root):
            collected.append(path)
    return sorted(set(collected))


def is_formal_study(source: Path) -> bool:
    return (
        (source / "raw_measurements.csv").is_file()
        and (source / "study_metadata.json").is_file()
    )


def locate_import_sources(root: Path, explicit: list[str]) -> list[Path]:
    """Find ignored local study directories that contain recorded evidence."""
    paths = [Path(p).expanduser() for p in explicit]
    if not explicit:
        paths = [root / p for p in DEFAULT_IMPORT_SOURCES]
    found = []
    for candidate in paths:
        if not candidate.is_absolute():
            candidate = root / candidate
        if is_formal_study(candidate):
            found.append(candidate.resolve())
        elif explicit:
            raise ValueError(
                f"Input lacks raw_measurements.csv or study_metadata.json: {candidate}"
            )
    return list(dict.fromkeys(found))


def safe_import_files(source: Path) -> list[Path]:
    """Keep the import to the documented scientific output extensions."""
    extensions = DIRECTORY_ALLOWLIST["paper/benchmarks/solver_study_runs"]
    selected = []
    for path in source.rglob("*"):
        if (
            path.is_file() and not path.is_symlink()
            and path.suffix.lower() in extensions
            and not any(part.startswith(".") for part in path.relative_to(source).parts)
            and path.name.casefold() not in BANNED_NAMES
        ):
            selected.append(path)
    return sorted(selected)


def import_study(
    source: Path, destination: Path, *, dry_run: bool,
) -> list[tuple[Path, Path]]:
    """Copy raw and derived study evidence, retaining relative paths."""
    planned = []
    for src in safe_import_files(source):
        rel = src.relative_to(source)
        dst = destination / rel
        if dst.exists():
            raise FileExistsError(f"Refusing to overwrite an existing artifact: {dst}")
        planned.append((src, dst))
    if not dry_run:
        for src, dst in planned:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    return planned


def verify_files(files: list[Path], root: Path) -> None:
    """Fail before publishing oversized or empty artifacts."""
    for path in files:
        if not is_allowed_file(path, root):
            raise ValueError(f"Refusing unsafe path: {path}")
        size = path.stat().st_size
        if size == 0:
            raise ValueError(f"Empty generated artifact: {path}")
        if size > MAX_FILE_BYTES:
            raise ValueError(
                f"Generated file exceeds 50 MiB: {path} ({size / 1e6:.1f} MB). "
                "Use Git LFS or an externally archived artifact, not a normal Git commit."
            )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(
    files: list[Path], root: Path, source_revision: str, stamp: str,
) -> Path:
    """Portable proof of exactly which generated artifacts were published."""
    dest = root / "paper/benchmarks/solver_study_runs" / (
        f"publication-manifest-{stamp}.json"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "kind": "generated_research_artifact_publication",
        "source_git_revision": source_revision,
        "published_utc": datetime.now(timezone.utc).isoformat(),
        "generated_output_only": True,
        "files": [
            {
                "path": item.relative_to(root).as_posix(),
                "sha256": sha256_file(item),
                "bytes": item.stat().st_size,
            }
            for item in files
        ],
        "note": (
            "The timing measurements originate from the user's local host. "
            "The manifest records hashes but does not independently validate "
            "hardware conditions, numerical results, or paper conclusions."
        ),
    }
    dest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--publish", action="store_true",
        help="Create/push a results-only Git branch; default is dry-run."
    )
    parser.add_argument(
        "--from-dir", action="append", default=[], metavar="PATH",
        help="Import one local ignored study folder; repeat for multiple runs."
    )
    parser.add_argument(
        "--no-pr", action="store_true",
        help="Push a branch but skip automatic gh pull-request creation."
    )
    args = parser.parse_args(argv)
    root = ROOT
    try:
        imports = locate_import_sources(root, args.from_dir)
        existing = discover_publishable(root)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        incoming: list[tuple[Path, Path]] = []
        for idx, source in enumerate(imports):
            # Do not duplicate runs already stored in publication directory.
            if source.is_relative_to((root / "paper/benchmarks/solver_study_runs").resolve()):
                continue
            destination = root / "paper/benchmarks/solver_study_runs" / (
                f"local-import-{stamp}-{idx + 1}"
            )
            incoming.extend(import_study(source, destination, dry_run=True))

        print(f"Repository: {root}")
        print(f"Already publishable generated artifacts: {len(existing)}")
        print(f"Importable study artifacts from ignored directories: {len(incoming)}")
        if not existing and not incoming:
            print("No measured/generated outputs found. Nothing will be committed.")
            print("Run the benchmark first, or supply --from-dir PATH.")
            return 1
        for path in existing:
            print("  ADD ", path.relative_to(root).as_posix())
        for _, target in incoming:
            print("  COPY", target.relative_to(root).as_posix())
        if not args.publish:
            print("\nPreview only. Use --publish to create/push the results branch.")
            return 0

        if run_git("branch", "--show-current") != "main":
            raise RuntimeError(
                "Switch to main before publishing. Other agents' branches "
                "will never be modified automatically."
            )
        if run_git("status", "--porcelain", "--untracked-files=no"):
            raise RuntimeError(
                "Tracked local changes exist. Commit or stash them first; "
                "this script never stages unrelated source edits."
            )
        # Pull before creating the new branch, preserving local generated files.
        run_git("pull", "--ff-only", "origin", "main")
        source_revision = run_git("rev-parse", "HEAD")
        publication_branch = f"results/local-research-{stamp}"
        run_git("switch", "-c", publication_branch)
        for idx, source in enumerate(imports):
            if source.is_relative_to((root / "paper/benchmarks/solver_study_runs").resolve()):
                continue
            destination = root / "paper/benchmarks/solver_study_runs" / (
                f"local-import-{stamp}-{idx + 1}"
            )
            import_study(source, destination, dry_run=False)
        actual = discover_publishable(root)
        verify_files(actual, root)
        manifest = write_manifest(actual, root, source_revision, stamp)
        actual.append(manifest)
        # Explicit per-file staging: never stage unreviewed unrelated artifacts.
        for start in range(0, len(actual), 25):
            group = actual[start:start + 25]
            run_git("add", "-f", "--", *[
                x.relative_to(root).as_posix() for x in group
            ])
        staged = run_git("diff", "--cached", "--name-only")
        if not staged:
            raise RuntimeError("No changes were staged: results may already be committed.")
        run_git(
            "commit", "-m", f"data: publish reproducible local research outputs {stamp}"
        )
        run_git("push", "-u", "origin", publication_branch)
        print(f"\nPublished results branch: {publication_branch}")
        print(f"https://github.com/{REPOSITORY}/tree/{publication_branch}")
        compare_url = (
            f"https://github.com/{REPOSITORY}/compare/"
            f"main...{publication_branch}?expand=1"
        )
        if not args.no_pr and shutil.which("gh"):
            result = subprocess.run(
                [
                    "gh", "pr", "create", "--base", "main",
                    "--head", publication_branch,
                    "--title", f"data: archive local research outputs ({stamp})",
                    "--body",
                    "Research output archive from the author's local computer. "
                    "Contains raw solver timings, statistical outputs, "
                    "figures and available paper/Marp builds, with SHA256 "
                    "publication manifest. Review numeric provenance and "
                    "do not confuse this archive with a manuscript submission.",
                ],
                cwd=root, text=True, capture_output=True,
            )
            if result.returncode == 0:
                print("Pull request:", result.stdout.strip())
            else:
                print("gh PR creation unavailable:", result.stderr.strip())
                print("Create the PR using:", compare_url)
        else:
            print("Create a pull request using:", compare_url)
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
