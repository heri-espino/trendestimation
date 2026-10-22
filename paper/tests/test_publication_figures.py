"""Check official SMCCA class and AwesomeFigures PDF exports.

Numerical estimators are tested elsewhere. These checks validate the artwork
pipeline and use synthetic miniature data so ordinary PR CI stays lightweight.
"""
from __future__ import annotations

import hashlib
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
HAS_AWESOME = importlib.util.find_spec("awesomefigures") is not None
HAS_LATEX = shutil.which("pdflatex") is not None


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


class SmccaTemplateTest(unittest.TestCase):
    def test_official_class_matches_uploaded_zip(self):
        digest = git_blob_sha((HERE / "smcca.cls").read_bytes())
        self.assertEqual(digest, "8f2642cbe1c9553e43f82f3c1e4e708b1a33d618")

    def test_figures_are_external_pdf_files_not_inline_tikz(self):
        for source, pdf in (
            ("main.tex", "figures/cortes_toto_synthetic.pdf"),
            ("sections/mauna_loa.tex", "figures/mauna_loa_1990_1999.pdf"),
            ("sections/high_order_numerics.tex", "figures/high_order_numerics.pdf"),
            ("sections/timing_experiments.tex", "figures/full_fit_at_M64.pdf"),
        ):
            content = (HERE / source).read_text(encoding="utf-8")
            self.assertNotIn(r"\begin{tikzpicture}", content)
            self.assertIn(pdf, content)
            self.assertIn(r"\includegraphics{" + pdf + "}", content)
            self.assertNotIn(r"\includegraphics[width=", content)


@unittest.skipUnless(HAS_AWESOME, "Install paper/requirements.txt for figure smoke checks")
class AwesomeFiguresPDFTest(unittest.TestCase):
    def setUp(self):
        import numpy as np

        spec = importlib.util.spec_from_file_location(
            "smcca_renderer", HERE / "figures" / "render_awesomefigures.py"
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.renderer = module
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.figures = self.folder / "figures"
        self.benchmarks = self.folder / "benchmarks"
        self.figures.mkdir()
        self.benchmarks.mkdir()
        # The tested figure generator probes the true SMCCA preamble.
        (self.folder / "main.tex").write_bytes((HERE / "main.tex").read_bytes())
        (self.folder / "smcca.cls").write_bytes((HERE / "smcca.cls").read_bytes())
        self.patcher = patch.multiple(
            module, PAPER=self.folder, FIGURES=self.figures,
            BENCHMARKS=self.benchmarks,
        )
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.time = np.arange(1, 11)
        t = self.time
        self._write("cortes_toto_synthetic.dat", "t observed true cv gcv aicc bic",
                    [
                        (k, k + .1, k, k, k+.05, k+.12, k)
                        for k in t
                    ])
        self._write("mauna_loa_1990_1999.dat", "year observed d2 d3 d4 d5",
                    [
                        (1990 + k/12, 350+k, 350+k-.1, 350+k-.2,
                         350+k-.3, 350+k-.4)
                        for k in t
                    ])
        self._write("high_order_numerics.dat", "d condition error lambda",
                    [(k, 10**(k/2), 0.0, .1) for k in t])

    def _write(self, name, header, rows, *, directory=None):
        target = (directory or self.figures) / name
        target.write_text(
            header + "\n"
            + "\n".join(" ".join(map(str, row)) for row in rows)
            + "\n",
            encoding="utf-8",
        )
        return target

    def _assert_pdf(self, path):
        data = path.read_bytes()
        self.assertGreater(len(data), 1000)
        self.assertTrue(data.startswith(b"%PDF-"), path)

    def test_renderer_never_silently_falls_back_to_dejavu(self):
        with patch.object(self.renderer.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "pdflatex on PATH"):
                with self.renderer.publication_context():
                    pass

    def test_publication_context_configures_exact_solid_latin_modern(self):
        layout = SimpleNamespace(
            textwidth_pt=400.0, fontsize_pt=10.0,
            font_family="lmr", font_name="ec-lmr10",
        )
        fake = MagicMock()
        fake.__enter__.return_value = SimpleNamespace(layout=layout)
        with patch.object(self.renderer.shutil, "which",
                          return_value="/usr/bin/pdflatex"), \
             patch.object(self.renderer.af, "latex_style", return_value=fake) as ctor:
            with self.renderer.publication_context():
                self.assertEqual(self.renderer.matplotlib.rcParams["pgf.texsystem"],
                                 "pdflatex")
                self.assertEqual(self.renderer.matplotlib.rcParams["pgf.rcfonts"],
                                 False)
                self.assertIn(r"\usepackage{lmodern}",
                              self.renderer.matplotlib.rcParams["pgf.preamble"])
            self.assertEqual(ctor.call_args.kwargs["width"], "text")
            self.assertEqual(ctor.call_args.kwargs["font"], "auto")

    def test_save_requests_pgf_backend_not_matplotlib_pdf_fonts(self):
        import matplotlib.pyplot as plt

        fig, _ = plt.subplots()
        publisher = SimpleNamespace(
            audit=lambda fig: SimpleNamespace(
                output_width_pt=400.0, expected_width_pt=400.0,
                smallest_text_pt=8.0,
            ),
            savefig=MagicMock(),
        )
        target = self.figures / "mock.pdf"
        self.renderer._save(publisher, fig, target)
        publisher.savefig.assert_called_once()
        self.assertEqual(publisher.savefig.call_args.kwargs["backend"], "pgf")
        self.assertTrue(publisher.savefig.call_args.kwargs["audit"])

    @unittest.skipUnless(HAS_LATEX, "Exact TeX-backed figures need pdflatex")
    def test_core_vector_pdfs(self):
        self.renderer.main(["--figures-only"])
        for name in ("cortes_toto_synthetic", "mauna_loa_1990_1999",
                     "high_order_numerics"):
            self._assert_pdf(self.figures / f"{name}.pdf")
        if shutil.which("pdffonts"):
            info = subprocess.run(
                ["pdffonts", str(self.figures / "cortes_toto_synthetic.pdf")],
                capture_output=True, text=True, check=True,
            ).stdout
            self.assertIn("LMRoman", info)
            self.assertNotIn("DejaVu", info)
        import awesomefigures as af
        af.verify_latex_placement(
            self.folder / "main.tex",
            self.figures / "cortes_toto_synthetic.pdf",
        )

    @unittest.skipUnless(HAS_LATEX, "Exact TeX-backed figures need pdflatex")
    def test_benchmark_figures_do_not_invent_data(self):
        self.renderer.main(["--benchmarks-only"])
        self.assertFalse((self.figures / "full_fit_at_M64.pdf").exists())
        self.assertFalse((self.figures / "trace_at_M32.pdf").exists())
        self._write(
            "full_fit_at_M64.dat",
            "n M densefresh densecached spectral banded",
            [(100, 64, .1, .08, .05, .02),
             (180, 64, .6, .5, .25, .04)],
            directory=self.benchmarks,
        )
        self._write(
            "trace_at_M32.dat",
            "n M densefresh densecached spectral banded",
            [(100, 32, .1, .08, .04, .03),
             (180, 32, .6, .5, .12, .3)],
            directory=self.benchmarks,
        )
        self.renderer.main(["--benchmarks-only"])
        self._assert_pdf(self.figures / "full_fit_at_M64.pdf")
        self._assert_pdf(self.figures / "trace_at_M32.pdf")


if __name__ == "__main__":
    unittest.main()
