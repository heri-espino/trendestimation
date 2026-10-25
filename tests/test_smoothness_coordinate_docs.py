"""Regression checks for the public S-versus-lambda learning path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_smoothness_guide_is_discoverable_and_links_to_deep_reference():
    landing = (DOCS / "index.rst").read_text(encoding="utf-8")
    guide = (DOCS / "smoothness_coordinate.rst").read_text(encoding="utf-8")
    quickstart = (DOCS / "quickstart.rst").read_text(encoding="utf-8")
    optimization = (DOCS / "smoothness_optimization.rst").read_text(
        encoding="utf-8"
    )
    assert "   smoothness_coordinate\n" in landing
    assert 'href="smoothness_coordinate.html"' in landing
    assert ':doc:`smoothness_coordinate`' in quickstart
    assert ':doc:`smoothness_coordinate`' in optimization
    assert ':doc:`smoothness_optimization`' in guide
    assert ':doc:`api/selection`' in guide


def test_guide_retains_key_mathematics_and_semantics():
    guide = (DOCS / "smoothness_coordinate.rst").read_text(encoding="utf-8")
    for label in (
        "smooth-coordinate-pls",
        "smooth-coordinate-index",
        "smooth-coordinate-edf",
        "smooth-coordinate-derivative",
        "smooth-coordinate-selection",
        "smooth-coordinate-score-derivative",
    ):
        assert f":label: {label}" in guide
    for fragment in (
        r"\arg\min",
        r"\lambda\|D_d\tau-\mu\mathbf{1}\|_2^2",
        r"S'(\lambda)",
        r"S^{-1}(s)",
        r"\nu(\lambda)=n-(n-d)S(\lambda)",
        r"dC/d\log\lambda",
        "not identical fitted curvature",
        "not by itself a proof of global optimality",
        "not rolling-origin",
    ):
        assert fragment in guide


def test_documented_code_uses_both_existing_search_spaces():
    guide = (DOCS / "smoothness_coordinate.rst").read_text(encoding="utf-8")
    assert 'search_space="lambda"' in guide
    assert 'search_space="smoothness"' in guide
    assert "lambda_for_smoothness(target_s)" in guide
    assert "smoother.fit(y, lambda_=penalty, mu=0.0)" in guide
    assert "original.scores, transformed.scores" in guide
    assert "r tol" not in guide
    assert "end-to-end timing comparisons" in guide
