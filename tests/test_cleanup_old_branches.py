"""No live repository is modified by these branch-cleanup safety tests."""
from __future__ import annotations

from scripts.cleanup_old_branches import archive_tag, classify_branch, cleanup


def branch(name="feature/a", sha="a" * 40, protected=False):
    return {"name": name, "commit": {"sha": sha}, "protected": protected}


def pr(name="feature/a", sha="a" * 40, state="closed", merged=True):
    return {
        "head": {
            "ref": name,
            "sha": sha,
            "repo": {"full_name": "example/trendestimation"},
        },
        "state": state,
        "merged_at": "2026-10-25T01:00:00Z" if merged else None,
    }


def test_merged_head_can_be_deleted_without_tag():
    row = classify_branch(branch(), [pr()], "example/trendestimation")
    assert row["classification"] == "merged_pr_same_sha"
    assert row["tag"] is None


def test_unmerged_and_advanced_heads_are_archived_before_delete():
    historical = classify_branch(
        branch("paper/old-paper"), [pr("paper/old-paper", merged=False)],
        "example/trendestimation",
    )
    assert historical["classification"] == "closed_unmerged_pr"
    assert historical["tag"] == archive_tag("paper/old-paper", "a" * 40)
    divergent = classify_branch(
        branch(), [pr(sha="b" * 40)], "example/trendestimation",
    )
    assert divergent["classification"] == "merged_pr_branch_advanced"
    assert divergent["tag"] is not None


def test_open_pr_and_protected_branches_cannot_be_deleted():
    assert classify_branch(
        branch(), [pr(state="open", merged=False)],
        "example/trendestimation",
    )["status"] == "skipped"
    assert classify_branch(
        branch("main"), [], "example/trendestimation",
    )["status"] == "skipped"
    assert classify_branch(
        branch(protected=True), [], "example/trendestimation",
    )["status"] == "skipped"


class FakeAPI:
    repository = "example/trendestimation"

    def __init__(self, *, break_archive=False, changed_sha=False):
        self.break_archive = break_archive
        self.changed_sha = changed_sha
        self.calls = []
        self.refs = {"feature/a": "a" * 40, "paper/old-paper": "c" * 40}
        self.tags = {}
        self.branches = [
            branch("main", "x" * 40),
            branch("feature/a"),
            branch("paper/old-paper", "c" * 40),
        ]
        self.prs = [pr(), pr("paper/old-paper", "c" * 40, merged=False)]

    def paginate(self, path):
        return self.branches if path == "branches" else self.prs

    def branch_sha(self, name):
        if self.changed_sha and name == "feature/a":
            return "z" * 40
        return self.refs[name]

    def tag_sha(self, tag):
        if self.break_archive:
            raise RuntimeError("tag authorization denied")
        return self.tags.get(tag)

    def request(self, method, path, data=None):
        self.calls.append((method, path))
        if method == "POST" and path == "git/refs":
            tag = data["ref"].removeprefix("refs/tags/")
            self.tags[tag] = data["sha"]
        elif method == "DELETE":
            name = path.removeprefix("git/refs/heads/")
            self.refs.pop(name)
        return {}, {}


def test_default_dry_run_has_no_mutations():
    api = FakeAPI()
    rows = cleanup(api, apply=False)
    assert [r["status"] for r in rows] == ["skipped", "planned", "planned"]
    assert api.calls == []
    assert len(api.refs) == 2


def test_apply_archives_unmerged_history_first():
    api = FakeAPI()
    rows = cleanup(api, apply=True)
    assert all(x["status"] in ("deleted", "skipped") for x in rows)
    assert api.calls == [
        ("DELETE", "git/refs/heads/feature/a"),
        ("POST", "git/refs"),
        ("DELETE", "git/refs/heads/paper/old-paper"),
    ]
    assert len(api.tags) == 1
    assert list(api.tags.values()) == ["c" * 40]
    assert api.refs == {}


def test_archive_failure_never_deletes_unmerged_branch():
    api = FakeAPI(break_archive=True)
    rows = cleanup(api, apply=True)
    assert rows[2]["status"] == "failed"
    assert "paper/old-paper" in api.refs
    assert not any(
        method == "DELETE" and "paper/old-paper" in path
        for method, path in api.calls
    )


def test_concurrent_head_change_is_not_deleted():
    api = FakeAPI(changed_sha=True)
    rows = cleanup(api, apply=True)
    assert rows[1]["status"] == "skipped_changed_sha"
    assert "feature/a" in api.refs
