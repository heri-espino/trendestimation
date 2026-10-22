"""Check mathematical typesetting and navigable, source-generated API sections."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_api_reference_is_split_into_navigable_pages():
    landing = (DOCS / "api.rst").read_text(encoding="utf-8")
    paths = [
        "core", "selection", "variances", "forecasting",
        "simulation", "visualization",
    ]
    assert ".. toctree::" in landing
    for name in paths:
        assert f"api/{name}" in landing
        assert (DOCS / "api" / f"{name}.rst").is_file()


def test_every_public_api_object_is_documented_once():
    initializer = (
        ROOT / "src" / "trendestimation" / "__init__.py"
    ).read_text(encoding="utf-8")
    public = re.search(r"__all__\s*=\s*\[([^\]]+)\]", initializer, re.S)
    assert public is not None
    names = re.findall(r'"([^"]+)"', public.group(1))
    pages = "\n".join(
        file.read_text(encoding="utf-8")
        for file in sorted((DOCS / "api").glob("*.rst"))
    )
    for name in names:
        # Every public class/function has one autodoc directive.
        directives = re.findall(
            rf"^\.\. auto(?:class|function):: trendestimation\.{name}\s*$",
            pages,
            flags=re.M,
        )
        assert len(directives) == 1, name
    assert ".. autoclass::" not in (
        DOCS / "api.rst"
    ).read_text(encoding="utf-8")


def test_big_o_uses_real_math_not_plain_text():
    for name in ("mathematics.rst", "benchmarks.rst"):
        source = (DOCS / name).read_text(encoding="utf-8")
        assert r":math:`\mathcal{O}(n)`" in source
        assert "O(n^3)" not in source
        assert "O(n^2)" not in source
        assert not re.search(r"(?<!\\)\\\\mathcal", source)
