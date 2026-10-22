"""Fast, offline checks for the flat Springer Nature manuscript package."""
from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


PAPER = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "springer_package", PAPER / "package_submission.py"
)
package_mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(package_mod)


class FlatSubmissionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "paper"
        self.root.mkdir()
        for name in ("sn-jnl.cls", "sn-mathphys-ay.bst"):
            (self.root / name).write_bytes((PAPER / name).read_bytes())
        (self.root / "bibliografia.bib").write_text(
            "@article{reference, author={Test, Ada}, title={T}, year={2026}}\n",
            encoding="utf-8",
        )
        (self.root / "sections").mkdir()
        (self.root / "sections" / "model.tex").write_text(
            r"\section{Model}" + "\n"
            r"\includegraphics{figures/testplot.pdf}" + "\n",
            encoding="utf-8",
        )
        (self.root / "figures").mkdir()
        (self.root / "figures" / "testplot.pdf").write_bytes(
            b"%PDF-1.4\n% test fixture PDF content\n"
        )
        (self.root / "main.tex").write_text(
            "\\documentclass[pdflatex,sn-mathphys-ay]{sn-jnl}\n"
            "\\begin{document}\n"
            "\\input{sections/model}\n"
            "\\IfFileExists{figures/missing_optional.pdf}{%\n"
            "\\includegraphics{figures/missing_optional.pdf}\n"
            "}{}\n"
            "\\bibliography{bibliografia}\n\\end{document}\n",
            encoding="utf-8",
        )
        # ensure it is newer than all sources, as it would be after latexmk
        (self.root / "main.pdf").write_bytes(b"%PDF-1.4\ncurrent draft")
        self.patch = patch.object(package_mod, "PAPER", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_exact_official_sources(self):
        self.assertEqual(
            package_mod.git_blob_sha((self.root / "sn-jnl.cls").read_bytes()),
            package_mod.CLASS_GIT_SHA,
        )
        self.assertEqual(
            package_mod.git_blob_sha(
                (self.root / "sn-mathphys-ay.bst").read_bytes()
            ),
            package_mod.BST_GIT_SHA,
        )

    def test_flat_zip_rewrites_sections_and_image_paths(self):
        target = self.root / "output.zip"
        entries = package_mod.package(target)
        with zipfile.ZipFile(target) as zf:
            self.assertEqual(sorted(zf.namelist()), entries)
            self.assertTrue(all("/" not in filename for filename in entries))
            main = zf.read("main.tex").decode("utf-8")
            section = zf.read("model.tex").decode("utf-8")
            self.assertIn(r"\input{model.tex}", main)
            self.assertIn(r"\includegraphics{testplot.pdf}", section)
            self.assertIn(
                r"\IfFileExists{missing_optional.pdf}", main,
            )
            self.assertIn(
                r"\includegraphics{missing_optional.pdf}", main,
            )
            self.assertIn("sn-jnl.cls", entries)
            self.assertIn("sn-mathphys-ay.bst", entries)
            self.assertIn("bibliografia.bib", entries)
            self.assertIn("testplot.pdf", entries)

    def test_rejects_missing_required_graphic(self):
        (self.root / "figures" / "testplot.pdf").unlink()
        with self.assertRaises(FileNotFoundError):
            package_mod.package(self.root / "output.zip")

    def test_rejects_stale_pdf(self):
        pdf = self.root / "main.pdf"
        tex = self.root / "main.tex"
        mtime = pdf.stat().st_mtime
        os.utime(tex, (mtime + 10, mtime + 10))
        with self.assertRaisesRegex(ValueError, "older than main.tex"):
            package_mod.package(self.root / "output.zip")

    def test_rejects_unverified_class(self):
        (self.root / "sn-jnl.cls").write_text("not the uploaded class")
        with self.assertRaisesRegex(ValueError, "official December 2024"):
            package_mod.package(self.root / "output.zip")

    def test_package_without_pdf_is_explicit(self):
        (self.root / "main.pdf").unlink()
        entries = package_mod.package(
            self.root / "without-pdf.zip", require_pdf=False
        )
        self.assertNotIn("main.pdf", entries)


if __name__ == "__main__":
    unittest.main()
