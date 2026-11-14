"""Validate the AwesomeFigures atlas and compiled Paper C without refitting.

The archive contains the direct-from-source manifest plus complete paper and
supplementary PDF. This gate checks original scientific result counts, asset
hashes, required manuscript coverage, figure surfaces and nonempty page text.
It cannot replace manual examination of all rendered pages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


def sha(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()


def run(atlas: Path, figures: Path, paper: Path, supplement: Path):
    data=json.loads(atlas.read_text(encoding="utf-8"))
    if data["status"]!="validated" or data["library"]!="awesomefigures":
        raise ValueError("AwesomeFigures did not generate this scientific archive")
    required={"set_style","color_palette","plot_scheme","save_figure"}
    if not required.issubset(set(data.get("awesomefigures_APIs",[]))):
        raise ValueError("Actual AwesomeFigures APIs not recorded")
    if len(data["figures"])!=10 or data.get("n_figures")!=10:
        raise ValueError("Ten selected scientific figures were not generated")
    assets=0
    for stem,formats in data["figures"].items():
        if not stem.startswith("atlas_") or set(formats)!={"pdf","svg","png"}:
            raise ValueError("Incorrect scientific figure filenames or formats")
        for extension,record in formats.items():
            path=figures/(stem+"."+extension)
            if not path.is_file() or path.stat().st_size!=record["bytes"]:
                raise ValueError("Missing/truncated scientific figure "+str(path))
            if sha(path)!=record["sha256"]:
                raise ValueError("Mismatch from AwesomeFigures provenance "+str(path))
            assets+=1
    for key,value in data["immutable_input_sha256"].items():
        if len(value)!=64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError("Input source checksum invalid "+key)
    pr=PdfReader(str(paper),strict=False)
    sp=PdfReader(str(supplement),strict=False)
    if len(pr.pages)<11 or len(sp.pages)<9:
        raise ValueError("Required manuscript or supplement pages missing")
    main="\n".join(page.extract_text() or "" for page in pr.pages).lower()
    supp="\n".join(page.extract_text() or "" for page in sp.pages).lower()
    checks={
        "physical_synthetic_jerk":"known synthetic" in main or "synthetic jerk" in main,
        "nominal_edf":"nominal" in main and "degrees of freedom" in main,
        "tvsd_pathology":"78.9" in main and "145" in main,
        "real_ngsim":"us-101" in main and "i-80" in main,
        "unfavorable_spline":"0.3480" in main and "spline" in main,
        "supplement_A1":"a1. known-jerk regimes" in supp,
        "supplement_A10":"a10. reference-mean sensitivity" in supp,
        "supplement_no_fabrication":"real ngsim" in supp and "observ" in supp,
    }
    if not all(checks.values()):
        raise ValueError("Compiled visuals omit required scientific explanation: "+str(checks))
    return {
        "status":"passed", "awesomefigures_version":data["library_version"],
        "atlas_figures":10,"assets_sha256_verified":assets,
        "manuscript_pages":len(pr.pages),"supplement_pages":len(sp.pages),
        "manuscript_sha256":sha(paper), "supplement_sha256":sha(supplement),
        "original_sources_sha256":data["immutable_input_sha256"],
        "scientific_text_checks":checks,
        "manual_page_visual_inspection_required":True,
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("atlas","figures","paper","supplement","report"):
        p.add_argument("--"+name,required=True,type=Path)
    opts=p.parse_args()
    if opts.report.exists():raise FileExistsError(opts.report)
    result=run(opts.atlas,opts.figures,opts.paper,opts.supplement)
    opts.report.parent.mkdir(parents=True,exist_ok=True)
    opts.report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2),flush=True)


if __name__=="__main__":
    main()
