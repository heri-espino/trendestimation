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

def polish_primary(fig,name):
    """Make archived 7-9in plots legible on the 372-pt Springer page."""
    if name=="fig02_runtime_distributions":
        ax=fig.axes[0]
        ax.set_title("Paired complete-grid runtime distributions",fontsize=10)
        fig.subplots_adjust(left=.35,right=.98,top=.86,bottom=.20)
    elif name=="fig03_mapping_distributions":
        if getattr(fig,"_suptitle",None) is not None:
            fig._suptitle.set_text("Penalty mapping and reuse: observed distributions")
            fig._suptitle.set_fontsize(10)
        for ax in fig.axes:
            old=[txt.get_text() for txt in ax.get_xticklabels()]
            new=[]
            for label in old:
                compact=(label.replace("M=10,000","10k")
                              .replace("M=1,000","1k")
                              .replace("M=100","100")
                              .replace("Banded","B")
                              .replace("SVD","S"))
                new.append(compact)
            ax.set_xticks(ax.get_xticks(),new,fontsize=7.2)
        fig.subplots_adjust(left=.12,right=.99,top=.81,bottom=.23,wspace=.17)
    elif name=="fig04_workload_stacked":
        if getattr(fig,"_suptitle",None) is not None:
            fig._suptitle.set_text("Runtime components: candidates x series")
            fig._suptitle.set_fontsize(10)
        fig.subplots_adjust(left=.13,right=.99,top=.82,bottom=.25,wspace=.11)
    elif name=="fig05_grid_completion":
        ax=fig.axes[0]
        ax.set_title("Complete-grid acceptance: Cholesky and SVD",fontsize=10)
        for item in ax.texts:
            if item.get_text() in ("0%","100%"):
                item.set_x(.90)
        fig.subplots_adjust(left=.38,right=.98,top=.85,bottom=.26)
    elif name=="fig06_order4_failures":
        ax=fig.axes[0]
        ax.set_title("Fourth-order acceptance and rejection",fontsize=10)
        fig.subplots_adjust(left=.38,right=.98,top=.85,bottom=.25)
    elif name=="fig07_crossover_distributions":
        ax=fig.axes[0]
        ax.set_title("Single-candidate versus full-grid cost",fontsize=10)
        ax.set_xticks(range(6),[
            "CV\n256,3\n1","CV\n256,3\n100",
            "CV\n128,3\n1","CV\n128,3\n100",
            "GCV\n64,1\n1","GCV\n64,1\n100"
        ],fontsize=7.2)
        fig.subplots_adjust(left=.13,right=.98,top=.85,bottom=.28)
    elif name=="fig08_memory_scaling":
        ax=fig.axes[0]
        ax.set_title("Dense versus banded memory allowance",fontsize=10)
        handles,labels=ax.get_legend_handles_labels()
        short=["SVD: 5 dense arrays","Inverse: 7 dense arrays",
               "Banded: 2 arrays","Dense cap: 2 GiB"]
        if len(handles)==4:
            ax.legend(handles,short,loc="upper center",
                      bbox_to_anchor=(.5,-.29),ncol=2,
                      fontsize=7.2,frameon=False)
        fig.subplots_adjust(left=.18,right=.98,top=.84,bottom=.33)
    elif name=="fig09_kkt_rejections":
        ax=fig.axes[0]
        ax.set_title("Rejected scaled-optimality residuals",fontsize=10)
        fig.subplots_adjust(left=.15,right=.98,top=.85,bottom=.20)

class Exporter:
    def __init__(self,output,exact_tex=False):
        self.output=Path(output)
        self.exact_tex=exact_tex
        self.items=[]
        self.output.mkdir(parents=True,exist_ok=True)

    def export(self,fig,name,*,section,caption,primary=False):
        if primary:
            polish_primary(fig,name)
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
        elif primary and self.exact_tex and hasattr(af,"latex_style"):
            # AwesomeFigures 0.1.0 exposes latex_style rather than paper.
            # This is the project's established exact Springer/PGF pathway.
            with af.latex_style(
                PAPER, width="text", engine="pdflatex", font="auto",
                height_ratio=.59, minimum_text_pt=6.7,
            ) as publication:
                # The historical figures were created at screen widths of
                # 7–9 inches. Rescale the *figure canvas* to the actual
                # Springer text width BEFORE PGF export; do not rely on
                # LaTeX shrinking a wide PDF and making text <7pt.
                from matplotlib.text import Text
                width_inches = publication.layout.textwidth_pt / 72.27
                old_width, old_height = fig.get_size_inches()
                fig.set_size_inches(
                    width_inches,
                    max(2.85, old_height * width_inches / old_width),
                    forward=True,
                )
                for item in fig.findobj(match=Text):
                    if item.get_text() and item.get_fontsize() < 7.2:
                        item.set_fontsize(7.2)
                preliminary=publication.audit(fig)
                if abs(preliminary.output_width_pt-preliminary.expected_width_pt)>0.9:
                    raise RuntimeError("Springer physical figure width mismatch")
                if (preliminary.smallest_text_pt is not None and
                    preliminary.smallest_text_pt < 6.7):
                    raise RuntimeError("Springer figure contains unreadable text at print width")
                import matplotlib as mpl
                with mpl.rc_context({
                    "pgf.texsystem":"pdflatex",
                    "pgf.rcfonts":False,
                    "pgf.preamble":r"\usepackage{amsmath,amssymb}",
                    "savefig.bbox":None,
                    "savefig.pad_inches":0,
                }):
                    publication.savefig(fig,target,backend="pgf",audit=True)
                    audit=publication.audit(fig)
                tex={
                    "typography_provenance":"awesomefigures-latex_style-pgf",
                    "exact_tex_preamble":True,
                    "textwidth_pt":publication.layout.textwidth_pt,
                    "body_font_pt":publication.layout.fontsize_pt,
                    "audit_warnings":list(audit.warnings),
                    "pdf_sha256":sha(target),
                }
                target.with_suffix(".typography.json").write_text(
                    json.dumps(tex,indent=2)+"\n",encoding="utf-8"
                )
        else:
            if primary and self.exact_tex and not hasattr(af,"paper") and not hasattr(af,"latex_style"):
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
          "exact_tex_available":(hasattr(af,"paper") or hasattr(af,"latex_style")),
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
