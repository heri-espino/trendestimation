#!/usr/bin/env python3
"""One Windows VM run: formal solver uncertainty + four S-inversion methods.

Run from repository root:
    python paper/computational-statistics-submission/run_final_vm_study.py

Uses existing validated solver experiment and paired-signflip/Holm analyzer,
plus randomized Brent/Newton/secant/bisection inversion trials. Persists all
raw data and scripts, artifacts, machine metadata, and compiled paper inside
tracked repository directories (not gitignored build/ or benchmarks/results/).

The CLI is resumable: completed measured stages are NOT recomputed. Use
--rerun ONLY if deliberately replacing measurements from this VM. Existing
80,640-search Windows full-S study is reused, NOT rerun.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
RUN=HERE/"research"/"final_vm"
LOG=RUN/"run_commands.log"


def call(command: list[str], *, cwd:Path=REPO) -> None:
    text=" ".join(command)
    print(f"[final study] {text}",flush=True)
    with LOG.open("a",encoding="utf-8") as f:
        f.write(f"\nRUN {datetime.now(timezone.utc).isoformat()} {text}\n")
        f.flush()
        process=subprocess.Popen(
            command,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
            text=True,bufsize=1,errors="replace",
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line,end="",flush=True)
            f.write(line)
            f.flush()
        code=process.wait()
        f.write(f"EXIT={code}\n")
    if code:
        raise subprocess.CalledProcessError(code,command)


def sha(path:Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*, seeds:int=20, repeats:int=5, root_repeats:int=35,
        threads:int=1, profile:str="quick", rerun:bool=False,
        skip_pdf:bool=False) -> dict:
    if min(seeds,repeats,root_repeats,threads)<1:
        raise ValueError("Seeds, repetitions and threads must be positive")
    if seeds<5:
        print("[warning] fewer than five seeds disables formal solver inference",
              flush=True)
    RUN.mkdir(parents=True,exist_ok=True)
    PY=sys.executable
    solver=RUN/"solver"
    inversion=RUN/"inversion"
    analysis=solver/"analysis"
    stages=(
        ("solver", solver/"study_metadata.json",
         [PY,"benchmarks/formal_solver_study.py",
          "--preset",profile,"--seeds",str(seeds),"--repeats",str(repeats),
          "--single-calls","20","--threads",str(threads),
          "--output-dir",str(solver)]),
        ("analysis",analysis/"analysis_manifest.json",
         [PY,"benchmarks/analyze_formal_solver_study.py",
          "--input-dir",str(solver),"--output-dir",str(analysis),
          "--bootstrap","5000","--permutations","20000"]),
        ("inversion",inversion/"environment.json",
         [PY,"benchmarks/inversion_study.py","--repeats",str(root_repeats),
          "--threads",str(threads),"--output-dir",str(inversion)]),
        ("manuscript_figures",RUN/"final_report_manifest.json",
         [PY,str(HERE/"render_final_computation.py")]),
    )
    # An incomplete program from a previous run cannot be considered done.
    for name,finished,cmd in stages:
        if finished.is_file() and not rerun:
            print(f"[final study] reuse {name}: {finished}",flush=True)
        else:
            call(cmd)
    # Strictly require all intended reproducibility artifacts before PDF.
    required=(
        solver/"raw_measurements.csv",solver/"numerical_accuracy.csv",
        solver/"study_metadata.json",analysis/"timing_summary.csv",
        analysis/"paired_comparisons.csv",analysis/"analysis_manifest.json",
        inversion/"raw_inversions.csv",inversion/"summary.csv",
        inversion/"environment.json",RUN/"final_report_manifest.json",
        HERE/"final_solver_inference_table.tex",
        HERE/"final_inversion_table.tex",
        HERE/"final_computation_environment.tex",
        HERE/"figures"/"final_solver_inference.pdf",
        HERE/"figures"/"final_inversion_speed.pdf",
    )
    missing=[str(p) for p in required if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"Incomplete VM research output: {missing}")
    if not skip_pdf:
        if shutil.which("latexmk") is None:
            raise RuntimeError(
                "latexmk missing. Install MiKTeX + latexmk, or rerun "
                "with --skip-pdf (results remain committed-ready)."
            )
        call(["latexmk","-pdf","-interaction=nonstopmode",
              "-halt-on-error","main.tex"],cwd=HERE)
        if not (HERE/"main.pdf").is_file():
            raise FileNotFoundError("Standalone Springer PDF not created")
    manifest={
        "status":"complete",
        "recorded_utc":datetime.now(timezone.utc).isoformat(),
        "predeclared_study":{
            "solver_preset":profile,"data_seeds":seeds,
            "paired_timing_blocks":repeats,
            "inversion_timing_blocks":root_repeats,
            "blas_threads":threads,
        },
        "existing_windows_80640_measurements":"reused as archived source, not rerun",
        "compiled_pdf":not skip_pdf,
        "python_executable":sys.executable,
        "input_and_output_checksums":{
            str(p.relative_to(REPO)):sha(p) for p in required
        },
    }
    (RUN/"run_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n",encoding="utf-8",
    )
    print("[final study] Completed. All outputs are under "
          "paper/computational-statistics-submission/, ready for git add .",flush=True)
    return manifest


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds",type=int,default=20)
    parser.add_argument("--repeats",type=int,default=5)
    parser.add_argument("--root-repeats",type=int,default=35)
    parser.add_argument("--threads",type=int,default=1)
    parser.add_argument("--profile",choices=("smoke","quick","full"),default="quick")
    parser.add_argument("--rerun",action="store_true")
    parser.add_argument("--skip-pdf",action="store_true")
    args=parser.parse_args()
    run(seeds=args.seeds,repeats=args.repeats,
        root_repeats=args.root_repeats,threads=args.threads,
        profile=args.profile,rerun=args.rerun,skip_pdf=args.skip_pdf)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
