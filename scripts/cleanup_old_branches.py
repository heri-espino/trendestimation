"""Audit and safely remove obsolete GitHub branches after merged PRs.

This utility never changes main. It deletes a branch only if:
- it is not protected/main;
- it has no open pull request;
- it still points at the exact SHA inspected during the audit;
- and, if not exactly the head of a merged PR, a recovery tag has
  been created and verified to point to the identical SHA.

A closed but unmerged branch is archived to a tag before deletion.
This is intentionally different from merging stale, superseded work
over the current manuscript.

Usage:
    python scripts/cleanup_old_branches.py
    python scripts/cleanup_old_branches.py --apply

Requires GITHUB_TOKEN with repository contents:write for --apply.
The preview mode makes no changes. Writes a machine-readable JSON report.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

API = "https://api.github.com"


class GitHubAPI:
    def __init__(self, repository: str, token: str):
        if repository.count("/") != 1 or not token:
            raise ValueError("Require GITHUB_REPOSITORY and GITHUB_TOKEN")
        self.repository = repository
        self.token = token

    def request(self, method: str, path: str, data=None):
        url = f"{API}/repos/{self.repository}/{path}"
        raw = None if data is None else json.dumps(data).encode("utf-8")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "trendestimation-branch-cleanup",
        }
        if raw is not None:
            headers["Content-Type"] = "application/json"
        req = Request(url, data=raw, headers=headers, method=method)
        try:
            with urlopen(req, timeout=30) as result:
                body = result.read()
                return (json.loads(body) if body else None), dict(result.headers)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:600]
            raise RuntimeError(f"GitHub HTTP {exc.code} for {method} {path}: {detail}") from exc

    def paginate(self, path: str):
        result = []
        page = 1
        while True:
            separator = "&" if "?" in path else "?"
            batch, _ = self.request("GET", f"{path}{separator}per_page=100&page={page}")
            if not isinstance(batch, list):
                raise ValueError(f"Expected list from {path}")
            result.extend(batch)
            if len(batch) < 100:
                return result
            page += 1
            if page > 50:
                raise ValueError("Pagination safety limit reached")

    def branch_sha(self, name: str) -> str:
        obj, _ = self.request("GET", f"git/ref/heads/{quote(name, safe='/')}")
        return obj["object"]["sha"]

    def tag_sha(self, tag: str) -> str | None:
        try:
            obj, _ = self.request("GET", f"git/ref/tags/{quote(tag, safe='/')}")
            return obj["object"]["sha"]
        except RuntimeError as error:
            if "GitHub HTTP 404" in str(error):
                return None
            raise


def archive_tag(branch: str, sha: str) -> str:
    """Stable, readable tag name for old non-integrated branch history."""
    slug = branch.replace("/", "--")
    return f"archive/removed-branch/{slug}-{sha[:10]}"


def classify_branch(
    branch: dict, pull_requests: list[dict], repository: str,
) -> dict:
    name = branch["name"]
    sha = branch["commit"]["sha"]
    result = {"branch": name, "sha": sha, "classification": None,
              "tag": None, "status": "planned"}
    if name == "main" or branch.get("protected", False):
        result.update(classification="protected", status="skipped")
        return result
    matching = [
        pr for pr in pull_requests
        if pr["head"]["ref"] == name
        and (pr["head"].get("repo") or {}).get("full_name") == repository
    ]
    if any(pr["state"] == "open" for pr in matching):
        result.update(classification="open_pr", status="skipped")
        return result

    if any(pr.get("merged_at") and pr["head"]["sha"] == sha for pr in matching):
        result["classification"] = "merged_pr_same_sha"
    elif any(pr.get("merged_at") for pr in matching):
        result["classification"] = "merged_pr_branch_advanced"
        result["tag"] = archive_tag(name, sha)
    elif matching:
        result["classification"] = "closed_unmerged_pr"
        result["tag"] = archive_tag(name, sha)
    else:
        result["classification"] = "no_pr_preserve"
        result["tag"] = archive_tag(name, sha)
    return result


def cleanup(api: GitHubAPI, apply: bool) -> list[dict]:
    branches = api.paginate("branches")
    pulls = api.paginate("pulls?state=all")
    rows = [
        classify_branch(branch, pulls, api.repository)
        for branch in branches
    ]
    # The inventory is built from live GitHub metadata; never hardcode branch
    # names and never delete a branch that has an open PR.
    for row in rows:
        if row["status"] == "skipped":
            continue
        if not apply:
            continue
        name, original_sha, tag = row["branch"], row["sha"], row["tag"]
        try:
            now_sha = api.branch_sha(name)
            if now_sha != original_sha:
                row.update(status="skipped_changed_sha",
                           detail=f"Expected {original_sha}, got {now_sha}")
                continue
            if tag:
                existing = api.tag_sha(tag)
                if existing is None:
                    api.request("POST", "git/refs", {
                        "ref": f"refs/tags/{tag}", "sha": original_sha,
                    })
                elif existing != original_sha:
                    raise RuntimeError("Existing recovery tag points to a different commit")
                if api.tag_sha(tag) != original_sha:
                    raise RuntimeError("Recovery tag was not verified")
            # Recheck SHA immediately before the destructive API request.
            # Conservatively skip a branch if it has changed in the meantime.
            if api.branch_sha(name) != original_sha:
                row.update(status="skipped_changed_sha_after_archive")
                continue
            api.request("DELETE", f"git/refs/heads/{quote(name, safe='/')}")
            row["status"] = "deleted"
        except Exception as error:
            row.update(status="failed", detail=str(error)[:500])
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Delete safe branches. Default is preview only.")
    parser.add_argument("--output", default="build/branch-cleanup-report.json")
    args = parser.parse_args(argv)
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token or not repo:
        parser.error("GITHUB_TOKEN and GITHUB_REPOSITORY are required")
    api = GitHubAPI(repo, token)
    rows = cleanup(api, args.apply)
    report = {
        "repository": repo,
        "utc": datetime.now(timezone.utc).isoformat(),
        "applied": args.apply,
        "branches": rows,
    }
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
        print(
            f"{row['status']:30} {row['classification']:30} "
            f"{row['branch']}"
            + (f" (archive: {row['tag']})" if row["tag"] else "")
        )
    print("Summary:", json.dumps(counts, sort_keys=True))
    if args.apply and any(row["status"] == "failed" for row in rows):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
