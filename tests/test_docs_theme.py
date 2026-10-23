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
        ".sd-btn-primary", ".te-reveal",
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
    assert 'rx="0"' in favicon



def test_native_syntax_highlighting_is_not_tinted_as_branding():
    """Pygments owns token colors; navy only decorates the code border."""
    stylesheet = CSS.read_text(encoding="utf-8")
    assert ".highlight span[class]" not in stylesheet
    assert ".highlight span:is(" not in stylesheet
    assert "--te-code-keyword:" not in stylesheet
    assert "--te-code-string:" not in stylesheet
    assert ".te-code-keyword { color: #c792ea; }" in stylesheet
    assert ".te-code-string { color: #a8d8a0; }" in stylesheet
    assert ".te-code-number { color: #f7bc7d; }" in stylesheet


def test_square_corners_and_scroll_reveal_are_progressive():
    stylesheet = CSS.read_text(encoding="utf-8")
    conf = (DOCS / "conf.py").read_text(encoding="utf-8")
    script = (DOCS / "_static" / "js" / "reveal.js").read_text(encoding="utf-8")
    assert "--te-radius: 0px;" in stylesheet
    assert "border-radius: var(--te-radius) !important" in stylesheet
    assert "prefers-reduced-motion: reduce" in stylesheet
    assert "IntersectionObserver" in script
    assert 'root.dataset.teRevealReady = "true"' in script
    assert 'html_js_files = ["js/reveal.js", "js/sidebar.js"]' in conf


def test_site_title_is_only_the_project_name():
    conf = (DOCS / "conf.py").read_text(encoding="utf-8")
    assert 'html_title = "trendestimation"' in conf
    assert 'html_short_title = "trendestimation"' in conf



def test_furo_sidebar_motion_and_muted_links():
    """Keep Furo checkbox navigation usable while smoothing its appearance."""
    css = CSS.read_text(encoding="utf-8")
    js = (DOCS / "_static" / "js" / "sidebar.js").read_text(encoding="utf-8")
    conf = (DOCS / "conf.py").read_text(encoding="utf-8")

    assert "--color-brand-visited: var(--te-link)" in css
    assert "--color-sidebar-link-text--top-level: var(--te-sidebar-text)" in css
    assert ".sidebar-tree li.current-page > a.reference" in css
    assert ".sidebar-tree .toctree-checkbox:checked ~ label .icon svg" in css
    assert "@keyframes te-document-enter" in css
    assert "prefers-reduced-motion: reduce" in css
    assert "js/sidebar.js" in conf
    assert "toctree-checkbox" in js
    assert 'sidebar.addEventListener("change"' in js
    assert "submenu.animate(" in js
    assert "prefers-reduced-motion: reduce" in js
    assert "location.href" not in js
    # Only keyboard disclosure handling may prevent a default action;
    # page links and browser navigation are never intercepted.
    assert 'sidebar.addEventListener("click"' not in js
    assert 'if (event.key !== "Enter" && event.key !== " ") return;' in js
    assert "event.preventDefault();" in js


def test_right_toc_matches_left_sidebar_in_light_and_dark():
    """Furo's active scroll-current selector must not revert to bright blue."""
    css = CSS.read_text(encoding="utf-8")
    assert "--color-toc-item-text: var(--te-sidebar-text)" in css
    assert "--color-toc-item-text--hover: var(--te-link)" in css
    assert "--color-toc-item-text--active: var(--te-link)" in css
    assert ".toc-tree a.reference:visited" in css
    assert ".toc-tree li.scroll-current > a.reference" in css
    assert "background: var(--te-nav-current)" in css
    assert ':root,\n[data-theme="dark"] {' in css
    assert ".toc-tree a.reference { transition: none !important; }" in css


def test_sidebar_expanders_are_keyboard_accessible_without_motion_support():
    """Checkbox labels expose button semantics, expansion state and focus."""
    script = (DOCS / "_static" / "js" / "sidebar.js").read_text(
        encoding="utf-8"
    )
    css = CSS.read_text(encoding="utf-8")
    assert "label.tabIndex = 0" in script
    assert 'label.setAttribute("role", "button")' in script
    assert 'label.setAttribute("aria-expanded", String(checkbox.checked))' in script
    assert 'checkbox.addEventListener("change", syncExpanded)' in script
    assert 'label.addEventListener("keydown"' in script
    assert "checkbox.click()" in script
    assert 'if (!Element.prototype.animate) return;' in script
    assert ".sidebar-tree li.has-children > label:focus-visible" in css
    assert "prefers-reduced-motion: reduce" in css
    # Never load duplicate WAAPI controllers for the same checkbox.
    assert 'html_js_files = ["js/reveal.js", "js/sidebar.js"]' in (
        DOCS / "conf.py"
    ).read_text(encoding="utf-8")


def test_sphinx_and_awesomefigures_use_identical_dejavu_letter_shapes():
    """A browser's fallbacks must not silently alter outlined SVG labels."""
    stylesheet = CSS.read_text(encoding="utf-8")
    helper = (ROOT / "src" / "trendestimation" / "_docs_style.py").read_text(
        encoding="utf-8"
    )
    readme = (DOCS / "README.md").read_text(encoding="utf-8")
    assert 'font-family: "DejaVu Sans";' in stylesheet
    assert "fontsource/fonts/dejavu-sans@5.3.0/latin-400-normal.woff2" in stylesheet
    assert "fontsource/fonts/dejavu-sans@5.3.0/latin-700-normal.woff2" in stylesheet
    assert "--font-stack: var(--te-font);" in stylesheet
    assert "--font-stack--headings: var(--te-font);" in stylesheet
    assert '"font.family": "DejaVu Sans"' in helper
    assert '"svg.fonttype": "path"' in helper
    assert "outlined" in readme
