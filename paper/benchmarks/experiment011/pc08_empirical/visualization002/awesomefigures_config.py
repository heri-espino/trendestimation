"""Publication palette, typography and audited AwesomeFigures exports.

All color schemes and Matplotlib defaults are obtained from AwesomeFigures.
The default vector-PDF path is the actual AwesomeFigures save_figure API.
For manuscript-embedded plots the optional --tex-core flag additionally
runs af.paper against the canonical Springer preamble and archives TeX audit.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import awesomefigures as af

ROOT=Path(__file__).resolve().parents[5]
PAPER=ROOT/"paper/main.tex"
PALETTE="okabe-ito"
STYLE="elegante"
COLORS=tuple(af.color_palette(PALETTE,as_hex=True))
if len(COLORS)!=8:
    raise RuntimeError("Expected eight AwesomeFigures Okabe-Ito colors")
METHOD={
 "spectral_svd":COLORS[4],
 "banded_cholesky":COLORS[0],
 "naive_inverse":COLORS[2],
 "sparse_cholesky_banded_trace":COLORS[6]
}
METHOD_NAMES={
 "spectral_svd":"Spectral SVD",
 "banded_cholesky":"Banded Cholesky",
 "naive_inverse":"Dense inverse",
 "sparse_cholesky_banded_trace":"Sparse hybrid"
}
CRITERION={"cv":COLORS[4],"gcv":COLORS[0],"aicc":COLORS[2],
           "bic":COLORS[6],"mle":COLORS[1]}
INK="#1B2533"
BG="#FFFFFF"

def initialize():
    af.set_style(STYLE,palette=PALETTE,font="DejaVu Sans",use_tex=False,rasterize=True)
    plt.rcParams.update({
        "axes.facecolor":BG,"figure.facecolor":BG,"savefig.facecolor":BG,
        "axes.spines.top":False,"axes.spines.right":False,
        "pdf.fonttype":42,"ps.fonttype":42,"svg.fonttype":"none",
        "legend.frameon":False,"font.size":8.5
    })

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

class Exporter:
    def __init__(self,output,exact_tex=False):
        self.output=Path(output)
        self.exact_tex=exact_tex
        self.items=[]
        self.output.mkdir(parents=True,exist_ok=True)

    def export(self,fig,name,*,section,caption,primary=False):
        target=self.output/"figures"/(name+".pdf")
        target.parent.mkdir(parents=True,exist_ok=True)
        if primary and self.exact_tex and hasattr(af,"paper"):
            with af.paper(
                PAPER,style=STYLE,palette=PALETTE,
                width=r"\columnwidth",engine="pdflatex",
                minimum_text_pt=6.7,strict=False
            ) as publication:
                publication.savefig(fig,target,width=r"\columnwidth")
                record=publication.records[-1]
            if record.typography!="exact-tex-preamble":
                raise RuntimeError("Core figure did not match actual Springer TeX preamble")
            if not record.pdf_fonts or not all(f["embedded"] for f in record.pdf_fonts):
                raise RuntimeError("Unembedded core-figure TeX font")
            tex={
                "typography_provenance":record.typography,
                "actual_width_tex_pt":record.actual_width_tex_pt,
                "pdf_fonts":list(record.pdf_fonts),
                "warnings":list(record.warnings),
                "sha256":record.sha256,
            }
            target.with_suffix(".typography.json").write_text(
                json.dumps(tex,indent=2)+"\n",encoding="utf-8"
            )
        else:
            if primary and self.exact_tex and not hasattr(af,"paper"):
                # The runner's installed AwesomeFigures 0.1.0 predates
                # af.paper. Still use the genuine AwesomeFigures vector
                # export and disclose that no exact-TeX audit is available.
                print("[AwesomeFigures] af.paper unavailable; vector PDF via af.save_figure, not exact TeX",flush=True)
                target.with_suffix(".typography.json").write_text(
                    json.dumps({"typography_provenance":"awesomefigures-vector-pdf",
                       "exact_tex_preamble":False,"awesomefigures_version":af.__version__,
                       "reason":"Installed AwesomeFigures lacks af.paper API"},
                       indent=2)+"\n",encoding="utf-8")
            af.save_figure(fig,target,dpi=210)
        # Supplementary images retain editable vector SVG and raster previews.
        af.save_figure(fig,target.with_suffix(".svg"),dpi=210)
        af.save_figure(fig,target.with_suffix(".png"),dpi=170)
        plt.close(fig)
        self.items.append({
            "id":name,"section":section,"caption":caption,
            "primary":primary,"pdf":str(target.relative_to(self.output)).replace("\\","/"),
            "sha256":sha(target)
        })
        print("[AwesomeFigures]",name,flush=True)
        return target

    def save_manifest(self,inputs,config):
        manifest={
          "renderer":"awesomefigures",
          "awesomefigures_version":af.__version__,
          "pinned_commit":"a9760351c1f72ccf7a1a2ef2ff14136d6e280d88",
          "api":["set_style","color_palette","save_figure"]+
                (["paper","Publication.savefig"] if self.exact_tex else []),
          "palette":PALETTE,"style":STYLE,
          "canonical_manuscript":"paper/main.tex",
          "input_sha256":{p.name:sha(p) for p in inputs},
          "figure_count":len(self.items),"primary_count":sum(x["primary"] for x in self.items),
          "exact_tex_available":hasattr(af,"paper"),
          "figures":self.items,"configuration":config,
          "no_new_experiments":True,
          "numerical_limits":[
             "Only complete valid matched pairs enter speedup plots",
             "Independent seeds are the unit for paired density plots",
             "Worker phases are not assumed comparable CPU occupancy",
             "Resource budget is not a measured out-of-memory failure",
             "Residual failures are conditional on rejection"
          ]}
        path=self.output/"figure_manifest.json"
        path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
        return manifest
