"""Check that Sphinx actually parsed notebook Markdown mathematics.

Run after a warning-strict Sphinx build:
    python scripts/check_rendered_notebook_math.py build/site

It inspects generated HTML rather than accepting syntactically valid notebook
Markdown that accidentally renders $...$ as ordinary text. The script does
not execute notebooks and requires no third-party packages.
"""

from __future__ import annotations

import argparse
from html import unescape
from html.parser import HTMLParser
from pathlib import Path


# MathJax-backed Sphinx builds contain <span class="math ..."> for inline
# and <div class="math ..."> for displayed formulae.
class MathNodes(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._math_depth = 0
        self._body: list[str] = []
        self.nodes: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = dict(attrs).get("class") or ""
        if tag in {"span", "div"} and "math" in classes.split():
            if self._math_depth == 0:
                self._body = []
            self._math_depth += 1
        elif self._math_depth and tag in {"span", "div"}:
            self._math_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self._math_depth and tag in {"span", "div"}:
            self._math_depth -= 1
            if self._math_depth == 0:
                self.nodes.append(unescape("".join(self._body)))
                self._body = []

    def handle_data(self, data: str) -> None:
        if self._math_depth:
            self._body.append(data)


# Each case checks a notebook's *actual* formulas. A rendered literal
# "$\\mu$" or "$$...$$" outside a math node cannot satisfy this check.
CASES: dict[str, tuple[str, ...]] = {
    "examples/01_first_trend.html": ("\\lambda=30",),
    "examples/02_select_smoothness.html": (
        "\\mu", "\\sigma_\\varepsilon^2", "\\sigma_\\eta^2",
    ),
    "examples/03_difference_orders.html": ("d=1", "\\lambda=\\infty"),
    "notebooks/04-nonzero-mean.html": ("\\widehat{\\mu}", "\\lambda"),
    "notebooks/09-gaussian-mle-and-guerrero-smoothness.html": (
        "\\sigma_\\varepsilon^2", "\\sigma_\\eta^2", "\\frac",
    ),
    "notebooks/10-forecast-pipeline.html": ("\\lambda", "\\tau"),
}


def check(root: Path) -> None:
    failures = []
    for relative, tokens in CASES.items():
        path = root / relative
        if not path.is_file():
            failures.append(f"Missing HTML: {relative}")
            continue
        parser = MathNodes()
        parser.feed(path.read_text(encoding="utf-8"))
        if not parser.nodes:
            failures.append(f"No Sphinx/MathJax math nodes in {relative}")
            continue
        rendered = "\n".join(parser.nodes)
        for token in tokens:
            if token not in rendered:
                failures.append(f"Missing rendered math {token!r} in {relative}")
        print(f"{relative}: {len(parser.nodes)} math nodes")
    if failures:
        raise SystemExit("Notebook math rendering failed:\n" + "\n".join(failures))
    print("Notebook inline and display math: rendered successfully")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_dir", type=Path, help="Sphinx HTML output directory")
    args = parser.parse_args()
    check(args.html_dir)


if __name__ == "__main__":
    main()
