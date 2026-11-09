"""Audit Paper C method-first PDF and its new source-backed method figures.

The existing visuals/audit_pdf.py independently audits previous six panels.
This adds final manuscript section and TSVD source-figure hash assertions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import logging
from pathlib import Path
from pypdf import PdfReader

logging.getLogger("pypdf").setLevel(logging.CRITICAL)

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(2**20),b""):
            h.update(b)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pdf",type=Path,required=True)
    p.add_argument("--figures",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():
        raise FileExistsError("Never overwrite existing paper audit")
    m=json.loads(args.manifest.read_text(encoding="utf-8"))
    if set(m["plots"])!={"exp008_known_jerk_benchmarks",
                          "exp008_real_forecast_benchmarks"}:
        raise ValueError("Missing method-comparison figure groups")
    for name,types in m["plots"].items():
        for ext,record in types.items():
            path=args.figures/(name+"."+ext)
            if not path.is_file() or path.stat().st_size!=record["bytes"]:
                raise ValueError("Missing or truncated scientific asset "+str(path))
            if sha(path)!=record["sha256"]:
                raise ValueError("Scientific figure checksum mismatch "+str(path))
    r=PdfReader(str(args.pdf),strict=False)
    pdftext="\n".join(page.extract_text() or "" for page in r.pages).lower()
    required={
        "method_not_backend":"truncated" in pdftext and "svd" in pdftext,
        "known_jerk_simulation":"simulation case" in pdftext,
        "real_ngsim_case":"real-data case" in pdftext,
        "calibration":"spectral" in pdftext and "noise" in pdftext,
        "physical_comparisons":"2.4413" in pdftext and "2.9416" in pdftext,
        "real_comparison":"0.5144" in pdftext and "0.5118" in pdftext,
        "spline_benchmark":"0.3480" in pdftext,
        "backend_section_removed":"all seven numerical fitting" not in pdftext,
        "no_computational_timing":"fit-only elapsed milliseconds" not in pdftext,
    }
    missing=[k for k,v in required.items() if not v]
    if missing:raise ValueError("Compiled PDF missing study text: "+str(missing))
    if len(r.pages)<8:raise ValueError("Truncated statistical paper")
    record={
        "status":"passed","pages":len(r.pages),"pdf_sha256":sha(args.pdf),
        "pdf_bytes":args.pdf.stat().st_size,
        "six_new_method_assets_hash_checked":True,
        "source_figure_manifest_sha256":sha(args.manifest),
        "method_comparison_checks":required,
        "manual_visual_review_required":True,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(record,indent=2))

if __name__=="__main__":
    main()
