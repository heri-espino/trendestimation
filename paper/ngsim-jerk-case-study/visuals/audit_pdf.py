"""Audit the compiled Paper C PDF and 6 new source-derived vector assets.

This does not validate scientific superiority; it checks document integrity,
page count, caption presence, source hashes and figure set completeness.
The PDF must be inspected visually before any journal submission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import warnings
from pathlib import Path

from pypdf import PdfReader

# The author-supplied CAS PDF repeats an optional /Group dictionary key.
# pypdf (strict=False) tolerates it, but its warning to stderr is fatal
# under PowerShell's ErrorActionPreference=Stop. Mute that benign parser
# warning while still explicitly checking readable pages, captions and hashes.
logging.getLogger('pypdf').setLevel(logging.CRITICAL)
warnings.filterwarnings('ignore', message='Multiple definitions in dictionary*')


def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for part in iter(lambda:fh.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()


def audit(pdf,manifest,out):
    if out.exists():
        raise FileExistsError(f"Audit already exists: {out}")
    m=json.loads(manifest.read_text(encoding="utf-8"))
    if m["n_new_multipanel_figures"] != 6:
        raise ValueError("Missing the six original requested plots")
    paper=pdf.parent
    expected=tuple(m["figure_files"])
    if len(expected)!=6:
        raise ValueError("Unexpected figure manifest")
    for name in expected:
        for fmt in ("pdf","svg","png"):
            rec=m["figure_files"][name][fmt]
            file=paper/rec["relative_path"]
            if (not file.is_file() or sha256(file)!=rec["sha256"]
                or file.stat().st_size != rec["bytes"]):
                raise ValueError("Missing/modified figure: "+str(file))
    reader=PdfReader(str(pdf),strict=False)
    if len(reader.pages)<8:
        raise ValueError("Unexpectedly short manuscript / missing figures")
    text="\n".join((page.extract_text() or "") for page in reader.pages).lower()
    checks={
      "abstract_new_topic":"relative-noise calibration" in text,
      "spectral_index_definition":"spectral mode" in text,
      "calibration_caption":"empirical calibration" in text,
      "intervention_caption":"controlled interventions" in text or
          "separately controlled interventions" in text,
      "misspecification_caption":"calibration error" in text,
      "tradeoff_jerk":"known historical" in text,
      "discussion_limits":"correlated" in text,
      "ngsim_reference":"ngsim" in text,
    }
    missing=[k for k,v in checks.items() if not v]
    if missing:
        raise ValueError("New manuscript text missing from PDF extraction: "+
                         repr(missing))
    report={
        "schema":1,
        "status":"passed",
        "pdf_path":str(pdf.resolve()),
        "pdf_sha256":sha256(pdf),
        "pdf_bytes":pdf.stat().st_size,
        "pages":len(reader.pages),
        "new_figures":len(expected),
        "verified_pdf_svg_png_sets":len(expected),
        "caption_text_checks":checks,
        "source_manifest_sha256":sha256(manifest),
        "caveat":"PDF-text integrity checks do not replace human page-by-page layout review.",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2),flush=True)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf",required=True,type=Path)
    p.add_argument("--manifest",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    audit(a.pdf,a.manifest,a.output)


if __name__=="__main__":
    main()
