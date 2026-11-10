"""Render every compiled Paper C PDF page for independent visual review.

Manuscript-only utility: no numerical experiments, raw NGSIM or
archived simulation outcomes are recomputed. Requires PyMuPDF and Pillow.
Write only into a new, non-existing, run-scoped output directory.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import fitz
from PIL import Image, ImageOps, ImageDraw

def digest(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--dpi", type=int, default=144)
    parser.add_argument("--columns", type=int, default=3)
    args=parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError("Do not overwrite a prior PDF review: "+str(args.output_dir))
    if args.dpi < 72 or args.dpi > 240 or args.columns < 1:
        raise ValueError("Invalid preview resolution or column count")
    args.output_dir.mkdir(parents=True)
    tiles=[]
    record=[]
    pdf=fitz.open(args.pdf)
    for index, page in enumerate(pdf):
        pix=page.get_pixmap(matrix=fitz.Matrix(args.dpi/72,args.dpi/72),
                            colorspace=fitz.csRGB, alpha=False)
        img=Image.frombytes("RGB", (pix.width,pix.height), pix.samples)
        out=args.output_dir/f"page-{index+1:02d}.png"
        img.save(out,optimize=True)
        record.append({"page":index+1,"file":out.name,"sha256":digest(out),
                       "bytes":out.stat().st_size,"width_px":pix.width,"height_px":pix.height})
        small=img.copy()
        small.thumbnail((470,670), Image.Resampling.LANCZOS)
        tile=Image.new("RGB",(490,715),"white")
        tile.paste(small,((490-small.width)//2,25))
        ImageDraw.Draw(tile).text((12,5),f"Paper C page {index+1}",fill="black")
        tiles.append(tile)
    if not tiles:
        raise ValueError("Empty PDF")
    cols=args.columns
    rows=(len(tiles)+cols-1)//cols
    sheet=Image.new("RGB",(cols*490,rows*715),(224,229,234))
    for k,tile in enumerate(tiles):
        sheet.paste(tile,((k%cols)*490,(k//cols)*715))
    combined=args.output_dir/"contact-sheet.png"
    sheet.save(combined,optimize=True)
    report={"status":"rendered","input_pdf_sha256":digest(args.pdf),
            "page_count":len(record),"dpi":args.dpi,
            "contact_sheet_sha256":digest(combined),
            "contact_sheet_bytes":combined.stat().st_size,"pages":record}
    (args.output_dir/"preview_manifest.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"rendered","pages":len(record),
                      "contact_sheet":str(combined),
                      "sha256":report["contact_sheet_sha256"]}),flush=True)

if __name__=="__main__":
    main()
