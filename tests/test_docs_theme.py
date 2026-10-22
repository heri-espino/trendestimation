"""Fast regression checks for the single-accent Sphinx design system."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CSS = DOCS / "_static" / "css" / "custom.css"


def test_one_editable_brand_token():
    stylesheet = CSS.read_text(encoding="utf-8")
    choices = re.findall(r"--te-brand\s*:\s*(#[0-9a-fA-F]{6})\s*;", stylesheet)
    assert choices == ["#003A70"]
    assert "color-mix(" in stylesheet
    assert "[data-theme=\"dark\"]" in stylesheet


def test_one_css_source_no_conflicting_furo_colors():
    conf = (DOCS / "conf.py").read_text(encoding="utf-8")
    assert 'html_css_files = ["css/custom.css"]' in conf
    assert '"light_css_variables"' not in conf
    assert '"dark_css_variables"' not in conf
    assert not (DOCS / "_static" / "custom.css").exists()


def test_documentation_accents_share_one_color_family():
    stylesheet = CSS.read_text(encoding="utf-8")
    for selector in (
        "--color-brand-content", "--color-brand-primary", ".content a:visited",
        ".sidebar-tree a:visited", ".cell_input", ".nbinput",
        ".highlight span[class]", ".sd-btn-primary",
        ".te-chart-panel", ".te-demo", "prefers-reduced-motion",
    ):
        assert selector in stylesheet
    for unused_bright_accent in ("#275fd0", "#2f6ce0", "#174bb4", "#9abbff"):
        assert unused_bright_accent not in stylesheet.lower()
    # Neither a green notebook bar nor browser purple visited links should
    # be used as decorative accents.
    assert "border-left-color: var(--te-accent) !important;" in stylesheet
    assert "color: var(--te-accent);" in stylesheet


def test_favicon_matches_brand():
    favicon = (DOCS / "_static" / "favicon.svg").read_text(encoding="utf-8")
    assert 'fill="#003A70"' in favicon
    assert "<linearGradient" not in favicon
