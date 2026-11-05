"""Contract tests for the TeX-only PC08 manuscript build.

These tests inspect source and CLI contracts but do not require LaTeX, network,
a Windows runner, data downloads, or scientific benchmark execution.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import scripts.build_papers_pc08 as pc08

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

    def test_springer_missing_table_restored_from_tracked_example(self) -> None:
        # No solver run or figure regeneration is needed if NOAA PDF is present.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper = root / "paper"
            figures = paper / "figures"
            figures.mkdir(parents=True)
            original = (
                "\\begin{tabular}{lrrr}\n" + ("Example & 2 & 3 & 4 \\\\\n" * 8)
                + "\\end{tabular}\n"
            )
            (paper / "criteria_table.example.tex").write_text(original)
            pdf = figures / "mauna_loa_1990_2026_09.pdf"
            pdf.write_bytes(b"%PDF-1.4\n" + b"x" * 120)
            with mock.patch.object(pc08, "ROOT", root):
                with mock.patch.object(pc08.subprocess, "run") as run:
                    result = pc08.prepare_springer_inputs(root)
                    run.assert_not_called()
            self.assertEqual((paper / "criteria_table.tex").read_text(), original)
            self.assertTrue(any(x["path"] == "paper/criteria_table.tex" for x in result))

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
