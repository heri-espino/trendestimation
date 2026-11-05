"""Contract tests for the TeX-only PC08 manuscript build.

These tests inspect source and CLI contracts but do not require LaTeX, network,
a Windows runner, data downloads, or scientific benchmark execution.
"""
from __future__ import annotations

import subprocess
import sys
import unittest

from scripts.build_papers_pc08 import (
    CAS_FILES,
    CAS_TEMPLATE,
    PAPERS,
    ROOT,
    selected_papers,
    validate_sources,
)


class TestPC08ManuscriptBuild(unittest.TestCase):
    def test_seven_distinct_latex_entrypoints(self) -> None:
        self.assertEqual(len(PAPERS), 7)
        self.assertEqual(len({p.id for p in PAPERS}), 7)
        self.assertEqual(len({(p.folder, p.entry) for p in PAPERS}), 7)
        self.assertEqual(
            {p.id for p in PAPERS},
            {
                "csda-a", "csda-b", "springer", "ngsim",
                "direct-weights", "historical-springer", "historical-sncs",
            },
        )

    def test_all_sources_and_original_elsevier_template_exist(self) -> None:
        validate_sources(PAPERS)
        for paper in PAPERS:
            entry = ROOT / paper.folder / paper.entry
            self.assertTrue(entry.is_file(), entry)
            contents = entry.read_text(encoding="utf-8-sig")
            if paper.template == "cas":
                self.assertIn(r"\documentclass[a4paper,fleqn]{cas-dc}", contents)
            else:
                self.assertIn(r"{sn-jnl}", contents)
        for name in CAS_FILES:
            self.assertTrue((CAS_TEMPLATE / name).is_file(), name)

    def test_selection_never_expands_into_experiments(self) -> None:
        self.assertEqual(len(selected_papers("all")), 7)
        for paper in PAPERS:
            self.assertEqual(selected_papers(paper.id), (paper,))

    def test_dry_run_leaves_papers_untouched(self) -> None:
        source = ROOT / "scripts/build_papers_pc08.py"
        result = subprocess.run(
            [sys.executable, str(source), "--paper", "all", "--dry-run"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        self.assertEqual(len(result.stdout.strip().splitlines()), 7)
        self.assertNotIn("Compiling", result.stdout)


if __name__ == "__main__":
    unittest.main()
