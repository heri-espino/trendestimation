#!/usr/bin/env python3
"""Set native landscape orientation for the two CSDA sideways table pages.

LaTeX's rotating package rotates only the table contents. This script sets
/Rotate=90 on the corresponding PDF page dictionaries without rasterization.
It fails closed if either table caption cannot be found uniquely.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from pypdf import PdfReader, PdfWriter

# Match the stable descriptive captions, not their ordinal table numbers.
# Moving tables between sections or appendices must not break orientation.
LABELS = {
    "algorithmprovenanceandsourcesofcomputationalcomplexity": "algorithm provenance",
    "costsofnumericalalgorithms": "algorithm costs",
}


def find_pages(reader: PdfReader) -> dict[str, int]:
    found: dict[str, int] = {}
    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        normalized = "".join(ch.lower() for ch in text if ch.isalnum())
        for marker, label in LABELS.items():
            if marker in normalized:
                if label in found:
                    raise ValueError(f"Duplicate landscape table: {label}")
                found[label] = index
    if len(found) != len(LABELS):
        raise ValueError(
            f"Expected {len(LABELS)} table pages, found {found}. "
            "Source PDF left unchanged."
        )
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--check", action="store_true",
                        help="Verify that both pages have PDF rotation 90")
    args = parser.parse_args()
    reader = PdfReader(str(args.pdf))
    locations = find_pages(reader)

    if args.check:
        for label, index in locations.items():
            if reader.pages[index].rotation != 90:
                raise ValueError(f"{label}: page {index + 1} is not landscape")
            print(f"Verified landscape page {index + 1}: {label}")
        return

    writer = PdfWriter()
    writer.append(reader)
    for label, index in locations.items():
        if writer.pages[index].rotation != 0:
            raise ValueError(f"{label}: page {index + 1} was already rotated")
        writer.pages[index].rotate(90)
        print(f"Setting landscape page {index + 1}: {label}")
    if reader.metadata:
        writer.add_metadata({
            key: str(value)
            for key, value in reader.metadata.items()
            if value is not None
        })

    with NamedTemporaryFile(
        dir=args.pdf.parent, prefix="landscape-", suffix=".pdf", delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        with temporary.open("wb") as handle:
            writer.write(handle)
        check = PdfReader(str(temporary))
        for label, index in locations.items():
            if check.pages[index].rotation != 90:
                raise AssertionError(f"Landscape rotation failed for {label}")
            if check.pages[index].mediabox != reader.pages[index].mediabox:
                raise AssertionError("PDF page geometry unexpectedly changed")
        os.replace(temporary, args.pdf)
    finally:
        if temporary.exists():
            temporary.unlink()


if __name__ == "__main__":
    main()
