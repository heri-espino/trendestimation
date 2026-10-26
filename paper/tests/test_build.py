"""Fast unit tests for paper/build.py; no TeX or scientific data required."""
from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


BUILD_FILE = Path(__file__).resolve().parents[1] / "build.py"
spec = importlib.util.spec_from_file_location("smcca_paper_builder", BUILD_FILE)
builder = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(builder)


class BuildFlagsTest(unittest.TestCase):
    def _capture(self, args):
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = builder.run(args)
        return code, stream.getvalue()

    def test_default_build_generates_three_figure_sets_and_pdf(self):
        status, output = self._capture(["--dry-run"])
        self.assertEqual(status, 0)
        for name in ("make_figures.py", "make_extended_figures.py",
                     "benchmark_orders.py"):
            self.assertIn(name, output)
        self.assertIn("latexmk -pdf", output)
        self.assertIn("render_awesomefigures.py", output)
        self.assertNotIn("run_all.py", output)

    def test_figures_flag_does_not_run_latex_or_benchmarks(self):
        status, output = self._capture(["--dry-run", "--figures"])
        self.assertEqual(status, 0)
        self.assertIn("make_figures.py", output)
        self.assertIn("render_awesomefigures.py", output)
        self.assertNotIn("latexmk", output)
        self.assertNotIn("run_all.py", output)

    def test_all_runs_figures_benchmarks_and_pdf(self):
        status, output = self._capture([
            "--dry-run", "--all", "--benchmark-preset", "full",
            "--repeats", "7", "--blas-threads", "2"
        ])
        self.assertEqual(status, 0)
        self.assertIn("benchmark_orders.py", output)
        self.assertIn("render_awesomefigures.py", output)
        self.assertIn("render_awesomefigures.py --benchmarks-only", output)
        self.assertIn("run_all.py --preset full --repeats 7 --blas-threads 2", output)
        self.assertIn("latexmk -pdf", output)
        self.assertNotIn("write_paper_results.py", output)  # already done by run_all

    def test_tables_only_uses_existing_results(self):
        status, output = self._capture(["--dry-run", "--tables"])
        self.assertEqual(status, 0)
        self.assertIn("write_paper_results.py", output)
        self.assertIn("render_awesomefigures.py --benchmarks-only", output)
        self.assertNotIn("run_all.py", output)
        self.assertNotIn("latexmk", output)

    def test_benchmarks_only_does_not_touch_figures_or_pdf(self):
        status, output = self._capture(["--dry-run", "--benchmarks"])
        self.assertEqual(status, 0)
        self.assertIn("run_all.py --preset quick --repeats 5", output)
        self.assertIn("render_awesomefigures.py --benchmarks-only", output)
        self.assertNotIn("make_figures.py", output)
        self.assertNotIn("latexmk", output)

    def test_render_only_without_pdf_is_not_default_full_build(self):
        status, output = self._capture(["--dry-run", "--render-figures"])
        self.assertEqual(status, 0)
        self.assertIn("render_awesomefigures.py", output)
        self.assertNotIn("make_figures.py", output)
        self.assertNotIn("latexmk", output)
        self.assertNotIn("run_all.py", output)

    def test_render_only_reuses_benchmarks_and_compiles_pdf(self):
        status, output = self._capture(["--dry-run", "--render-figures", "--pdf"])
        self.assertEqual(status, 0)
        self.assertIn("render_awesomefigures.py", output)
        self.assertIn("latexmk -pdf", output)
        self.assertNotIn("make_figures.py", output)
        self.assertNotIn("run_all.py", output)

    def test_springer_packaging_is_opt_in_and_does_not_trigger_benchmarks(self):
        status, output = self._capture(["--dry-run", "--package"])
        self.assertEqual(status, 0)
        self.assertIn("package_submission.py", output)
        self.assertNotIn("run_all.py", output)
        self.assertNotIn("latexmk", output)
        status, output = self._capture(["--dry-run", "--pdf", "--package"])
        self.assertEqual(status, 0)
        self.assertIn("latexmk -pdf", output)
        self.assertIn("package_submission.py", output)

    def test_pdf_engine_flag_and_clean(self):
        status, output = self._capture([
            "--dry-run", "--pdf", "--latex-engine", "xelatex"
        ])
        self.assertEqual(status, 0)
        self.assertIn("latexmk -xelatex", output)
        status, output = self._capture(["--dry-run", "--clean"])
        self.assertEqual(status, 0)
        self.assertIn("latexmk -C main.tex", output)
        self.assertNotIn("make_figures.py", output)

    def test_rejects_incompatible_clean_and_bad_repeats(self):
        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            builder.run(["--clean", "--figures"])
        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            builder.run(["--repeats", "0", "--dry-run"])

    def test_records_manifest_after_mocked_successful_build(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paper = root / "paper"
            paper.mkdir()
            with patch.object(builder, "PAPER", paper), \
                 patch.object(builder, "REPOSITORY", root), \
                 patch.object(builder, "_command") as command, \
                 patch.object(builder, "_verify_required") as verify, \
                 patch.object(builder, "_git_sha", return_value="test-revision"), \
                 patch.object(builder, "check_bibliography", return_value=17), \
                 patch.object(builder, "_prepare_latex_transition", return_value=[]), \
                 patch.object(builder, "_save_latex_identity"), \
                 patch.object(builder.shutil, "which", return_value="latexmk"):
                status, _ = self._capture(["--figures", "--pdf"])
            self.assertEqual(status, 0)
            self.assertEqual(command.call_count, len(builder.FIGURE_GENERATORS) + 2)
            self.assertGreaterEqual(verify.call_count, 1)
            manifest = json.loads((paper / "build_manifest.json").read_text())
            self.assertEqual(manifest["git_revision"], "test-revision")
            self.assertEqual(len(manifest["steps"]), len(builder.FIGURE_GENERATORS) + 2)
            self.assertEqual(manifest["steps"][-1]["name"], "compile:PDF")
            self.assertIn("main.pdf", manifest["pdf"])

    def test_bibtex_duplicate_keys_preflight(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "bibliografia.bib"
            file.write_text(
                "@article{biessy2026wh,\n  title={First}\n}\n"
                "@article{Biessy2026WH,\n  title={Duplicate}\n}\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, r"Duplicate BibTeX.*lines 1 and 4"):
                builder.check_bibliography(file)

    def test_bibtex_unique_keys_preflight(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "bibliografia.bib"
            file.write_text(
                "@article{biessy2026wh,\n  title={Research}\n}\n"
                "@book{guerrero2007penalized,\n  title={Another reference}\n}\n",
                encoding="utf-8",
            )
            self.assertEqual(builder.check_bibliography(file), 2)

    def test_repo_bibliography_has_unique_keys(self):
        self.assertGreaterEqual(
            builder.check_bibliography(BUILD_FILE.parent / "bibliografia.bib"),
            17,
        )

    def test_dry_run_does_not_write_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            fake_paper = Path(temp)
            with patch.object(builder, "PAPER", fake_paper):
                status, _ = self._capture(["--dry-run", "--figures"])
            self.assertEqual(status, 0)
            self.assertFalse((fake_paper / "build_manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
