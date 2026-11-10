"""Inspect ONLY a freshly built PDF; archive checks and pages when renderers exist."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


def sha(file):
    h=hashlib.sha256()
    with file.open("rb") as fd:
        for data in iter(lambda:fd.read(1024*1024),b""):
            h.update(data)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pdf",type=Path,required=True)
    p.add_argument("--log",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    if not args.pdf.is_file() or args.pdf.stat().st_size<10000:
        raise RuntimeError("New compiled PDF absent or implausibly small")
    if not args.pdf.open("rb").read(5)==b"%PDF-":
        raise RuntimeError("Not a PDF binary")
    log=args.log.read_text(encoding="utf-8",errors="replace") if args.log.is_file() else ""
    out={"pdf_bytes":args.pdf.stat().st_size,"pdf_sha256":sha(args.pdf),
         "latex_overfull_lines":re.findall(r"Overfull \\hbox[^\\n]*",log)[:30],
         "latex_underfull_lines":re.findall(r"Underfull \\hbox[^\\n]*",log)[:15],
         "latex_undefined_references":re.findall(r"(?:undefined references|Citation .*? undefined|Reference .*? undefined)",log,re.I)[:30],
         "latex_errors":re.findall(r"^! .+$",log,re.M)[:30],
         "visual_pages":[],"pdf_backend":None}
    text=""
    try:
        import fitz
        pdf=fitz.open(str(args.pdf))
        out["pdf_backend"]="PyMuPDF"
        out["page_count"]=len(pdf)
        text="\n".join(page.get_text() for page in pdf)
        for j in sorted(set([0,1,2,max(0,len(pdf)//2),len(pdf)-1])):
            if j<0 or j>=len(pdf):continue
            pix=pdf[j].get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False)
            dest=args.output/f"proof_page_{j+1:02d}.png"
            pix.save(str(dest))
            out["visual_pages"].append(dest.name)
        pdf.close()
    except ImportError:
        try:
            from pypdf import PdfReader
            pdf=PdfReader(str(args.pdf))
            out["pdf_backend"]="pypdf"
            out["page_count"]=len(pdf.pages)
            text="\n".join(page.extract_text() or "" for page in pdf.pages)
        except ImportError:
            if shutil.which("pdftotext"):
                result=subprocess.run(["pdftotext",str(args.pdf),"-"],
                                     text=True,capture_output=True,check=False,timeout=60)
                text=result.stdout
                out["pdf_backend"]="pdftotext"
            if shutil.which("pdfinfo"):
                info=subprocess.run(["pdfinfo",str(args.pdf)],text=True,capture_output=True)
                m=re.search(r"Pages:\s*(\d+)",info.stdout)
                if m:out["page_count"]=int(m.group(1))
            if shutil.which("pdftoppm"):
                for index in (1,2):
                    stem=args.output/f"proof_page_{index:02d}"
                    cmd=["pdftoppm","-f",str(index),"-l",str(index),
                         "-scale-to","1000","-png","-singlefile",str(args.pdf),str(stem)]
                    rc=subprocess.run(cmd,check=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE).returncode
                    if rc==0:out["visual_pages"].append(stem.name+".png")
    checks=("Complete-criterion","Results","Conclusions","banded","SVD","References")
    out["text_checks"]={word:word.lower() in text.lower() for word in checks}
    (args.output/"extracted_pages.txt").write_text(text[:200000],encoding="utf-8")
    (args.output/"pdf_inspection.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in ("pdf_backend","page_count","pdf_sha256","latex_undefined_references","latex_errors","visual_pages","text_checks") if k in out},indent=2))
    if out["latex_errors"] or out["latex_undefined_references"]:
        raise RuntimeError("LaTeX log has unresolved errors/references")
    if out.get("page_count") is not None and out["page_count"]<4:
        raise RuntimeError("New empirical article has implausibly few pages")


if __name__=="__main__":
    main()
