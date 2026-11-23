"""Fail a CSDA build when a typeset prose paragraph breaches its column.

This targets TeX's "Overfull \hbox ... in paragraph" diagnostics, which
report actual line-breaking failures. The Elsevier CAS class also emits
one intrinsic "Overfull \hbox ... detected" message while constructing
its title/abstract metadata box; that is not a body paragraph and is
checked separately by rendered-page inspection.

Usage: python verify_layout.py main.log
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


PATTERN = re.compile(
    r"Overfull \\hbox \((?P<points>[0-9.]+)pt too wide\) "
    r"in paragraph at lines (?P<lines>[0-9-]+)"
)


def check(log: str, tolerance_pt: float = 0.5) -> list[str]:
    """Return human-readable violations above the strict tolerance."""
    issues = []
    for match in PATTERN.finditer(log):
        amount = float(match.group("points"))
        if amount > tolerance_pt:
            issues.append(
                f"{amount:.3f} pt overflow in paragraph "
                f"at lines {match.group('lines')}"
            )
    return issues


def main() -> int:
    log_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("main.log")
    if not log_path.is_file():
        print(f"Missing LaTeX log: {log_path}", file=sys.stderr)
        return 2
    violations = check(log_path.read_text(encoding="utf-8", errors="replace"))
    if violations:
        print("CSDA hard column margins failed:", file=sys.stderr)
        for item in violations:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("CSDA hard column margins: no overfull body paragraphs > 0.5 pt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
