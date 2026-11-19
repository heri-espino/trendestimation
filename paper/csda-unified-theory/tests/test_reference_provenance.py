"""Audit citation-key integrity in the unified CSDA manuscript.

Run from anywhere:
    python -m unittest discover -s paper/csda-unified-theory/tests -p 'test_reference_provenance.py' -v
This audits author-visible sources only; it does not fetch licensed PDF scans.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SHARED_BIB = ROOT.parent / "csda-computational-costs" / "references.bib"
LOCAL_BIB = ROOT / "algorithmic_references.bib"
SECTION_FILES = sorted((ROOT / "sections").glob("*.tex"))
TEX_FILES = [ROOT / "main.tex", *SECTION_FILES]
REQUIRED_ORIGINAL_KEYS = {
    "erisman1975", "ubaru2017", "hutchinson1990", "reinsch1967",
    "hestenesstiefel1952", "lin2011", "corneamadeira2017",
    "craven1979", "golub1979", "golubreinsch1970", "golubkahan1965",
}
FIVE_NEW_KEYS = {
    "ubaru2017", "hutchinson1990", "reinsch1967",
    "lin2011", "corneamadeira2017",
}
SIX_REUSED_KEYS = REQUIRED_ORIGINAL_KEYS - FIVE_NEW_KEYS


def entry_keys(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    # Match a BibTeX record beginning; ignore comments.
    return re.findall(
        r"(?m)^\s*@(?!comment\b|string\b|preamble\b)[A-Za-z]+\s*\{\s*([^,\s]+)\s*,",
        text, flags=re.IGNORECASE,
    )


def citation_keys(text: str) -> set[str]:
    # Accept natbib \citep[pages]{a,b}, \citet[section]{a} and \cite{a}.
    # Escape the leading slash here because a Python string represents LaTeX.
    result: set[str] = set()
    for matches in re.finditer(
        r"\\cite(?:p|t|alt|alp|author|year|yearpar)?\*?"
        r"(?:\[[^\]]*\]){0,2}\s*\{([^}]+)\}",
        text,
    ):
        result.update(key.strip() for key in matches.group(1).split(","))
    return result


class TestBibliographyIntegrity(unittest.TestCase):
    def test_all_cite_keys_resolve_and_records_are_unique(self):
        records = entry_keys(LOCAL_BIB) + entry_keys(SHARED_BIB)
        occurrences = Counter(records)
        duplicates = [k for k, n in occurrences.items() if n > 1]
        self.assertEqual(duplicates, [], f"Duplicate BibTeX keys: {duplicates}")
        source = "\n".join(path.read_text(encoding="utf-8") for path in TEX_FILES)
        cited = citation_keys(source)
        self.assertTrue(cited, "Failed to identify LaTeX citation commands")
        self.assertEqual(cited - set(records), set(), "Cited keys missing from BibTeX")
        self.assertTrue(REQUIRED_ORIGINAL_KEYS.issubset(cited))
        self.assertTrue(FIVE_NEW_KEYS.issubset(set(entry_keys(LOCAL_BIB))))
        self.assertTrue(SIX_REUSED_KEYS.issubset(set(records)))
        self.assertTrue(SIX_REUSED_KEYS.isdisjoint(FIVE_NEW_KEYS))
        self.assertTrue(FIVE_NEW_KEYS.isdisjoint(set(entry_keys(SHARED_BIB))))

    def test_corrected_hutchinson_and_lin_metadata(self):
        local = LOCAL_BIB.read_text(encoding="utf-8")
        for key, yr, doi in (
            ("hutchinson1990", "1990", "10.1080/03610919008812866"),
            ("lin2011", "2011", "10.1145/1916461.1916464"),
            ("ubaru2017", "2017", "10.1137/16M1104974"),
            ("corneamadeira2017", "2017", "10.1162/REST_a_00594"),
            ("reinsch1967", "1967", "10.1007/BF02162161"),
        ):
            m = re.search(
                rf"@article\{{{key}\s*,(.*?)(?=^\s*@|\Z)",
                local,
                flags=re.MULTILINE | re.DOTALL,
            )
            self.assertIsNotNone(m, key)
            body = m.group(1)
            self.assertRegex(body, rf"year=\{{{yr}\}}")
            self.assertIn(doi, body)

    def test_exact_and_approximate_are_distinct(self):
        alg = (ROOT / "sections" / "algorithms.tex").read_text(encoding="utf-8")
        self.assertIn("sec:approximate-diagnostics", alg)
        self.assertIn(r"\citet{hutchinson1990}", alg)
        self.assertIn(r"\citet{ubaru2017}", alg)
        self.assertIn(r"\citet[Secs.~2--4]{lin2011}", alg)
        self.assertIn(r"\citet[p.~404]{golubreinsch1970}", alg)


if __name__ == "__main__":
    unittest.main()
