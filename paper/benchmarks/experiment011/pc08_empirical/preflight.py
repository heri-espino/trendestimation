"""Read-only Experiment011 Windows preflight. No numerical experiment is launched."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import traceback

REL_REPORT = Path("paper/benchmarks/experiment011/campaigns/PC08_resume12_20261108_200034/report.json")
BASE = Path("paper/benchmarks/experiment011")
REQUIRED = ("measurements/raw_times.csv", "measurements/environment.json",
            "experiment011_case.json", "experiment011_qa.json")
EXPECTED = 2813


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def inspect(root: Path, backup: Path):
    out = {"utc": datetime.now(timezone.utc).isoformat(),
           "runner": os.environ.get("RUNNER_NAME"),
           "account": os.environ.get("USERNAME"),
           "windows": platform.system() == "Windows",
           "root": str(root), "backup": str(backup),
           "checks": {}, "warnings": [], "samples": []}
    if os.environ.get("RUNNER_NAME") != "PCAG103A-08":
        raise RuntimeError("Wrong runner: PCAG103A-08 required")
    for label, place in (("root", root), ("backup", backup)):
        out["checks"][label] = {"exists": place.is_dir(), "readable": os.access(place, os.R_OK)}
    report_path = root / REL_REPORT
    backup_report = backup / "metadata/report.json"
    for label, file in (("report", report_path), ("backup_report", backup_report),
                        ("backup_provenance", backup / "metadata/provenance.json"),
                        ("backup_inventory", backup / "metadata/files_sha256.csv")):
        info = {"exists": file.is_file()}
        if file.is_file():
            info.update({"bytes": file.stat().st_size, "sha256": sha(file)})
        out["checks"][label] = info
    if not report_path.is_file():
        raise FileNotFoundError(f"Cannot read original final cumulative report: {report_path}")
    report = load_json(report_path)
    records = report.get("results", [])
    out["report"] = {
        "planned_jobs": report.get("planned_jobs"),
        "recorded_jobs": len(records),
        "status": report.get("status"),
        "source_commit": report.get("source_commit"),
        "cases_sha256": report.get("cases_sha256"),
        "keys": sorted(report),
        "record_keys": sorted(records[0]) if records else [],
        "phase_workers": dict(sorted(Counter(str(r.get("phase_workers", "missing")) for r in records).items())),
        "process_exit_codes": dict(sorted(Counter(str(r.get("returncode", "missing")) for r in records).items())),
        "qa_classifications": dict(sorted(Counter(str(r.get("qa_classification", "missing")) for r in records).items())),
    }
    seen, duplicates, malformed = set(), [], []
    for rec in records:
        key = (rec.get("seed_index"), rec.get("case"))
        if key in seen:
            duplicates.append(key)
        seen.add(key)
        i = rec.get("seed_index")
        if not isinstance(i, int) or not (3 <= i <= 99) or rec.get("seed") != 1000000000 + (i-3)*1000000:
            malformed.append(key)
    out["report"]["unique_job_keys"] = len(seen)
    out["report"]["duplicate_keys"] = duplicates[:12]
    out["report"]["bad_seed_keys"] = malformed[:12]
    out["report"]["distinct_cases"] = len({r.get("case") for r in records})
    design_path = root / BASE / "cases.json"
    if design_path.is_file():
        design = load_json(design_path)
        expected = {(i, c["id"]) for i in range(3,100) for c in design["cases"]}
        out["report"]["design_cases"] = len(design["cases"])
        out["report"]["design_sha256"] = sha(design_path)
        out["report"]["missing_design_keys"] = len(expected - seen)
        out["report"]["unexpected_design_keys"] = len(seen - expected)
    # Build a single lookup of run-tag directories. Report records do not include
    # origin tag, so do NOT silently select a duplicate attempt as canonical.
    runs = root / BASE / "runs"
    by_index = defaultdict(list)
    if runs.is_dir():
        for folder in runs.iterdir():
            if not folder.is_dir():
                continue
            suffix = folder.name.rsplit("_s", 1)
            if len(suffix) == 2 and suffix[1].isdigit():
                by_index[int(suffix[1])].append(folder)
    out["inventory"] = {
        "seeded_run_folders": sum(map(len, by_index.values())),
        "distinct_run_tags": len({p.name.rsplit("_s",1)[0] for folders in by_index.values() for p in folders}),
        "unreferenced_series_index_folders": sorted(set(by_index)-set(range(3,100)))[:20],
    }
    candidate_counts = Counter()
    inaccessible = []
    for rec in records:
        i,case,block = rec["seed_index"],rec["case"],rec["block"]
        found = [f / case / f"block{block:03d}" for f in by_index.get(i, [])
                 if (f / case / f"block{block:03d}").is_dir()]
        candidate_counts[len(found)] += 1
        if not found:
            inaccessible.append((i, case, block))
    out["inventory"]["candidate_path_count_distribution"] = dict(sorted(candidate_counts.items()))
    out["inventory"]["unresolved_records"] = inaccessible[:30]
    # Sample a small number from each actual worker phase and report time.
    selected = {}
    for rec in records:
        phase = str(rec.get("phase_workers","missing"))
        if phase not in selected:
            selected[phase] = rec
    for rec in list(selected.values()) + records[-2:]:
        i,case,block = rec["seed_index"],rec["case"],rec["block"]
        found = [f / case / f"block{block:03d}" for f in by_index.get(i, [])
                 if (f / case / f"block{block:03d}").is_dir()]
        s = {"seed_index":i,"case":case,"block":block,"phase_workers":rec.get("phase_workers"),
             "candidate_paths":len(found)}
        if found:
            candidate=found[0]
            s["run_folder"]=str(candidate.relative_to(root))
            s["required_files"]={k:(candidate/k).is_file() for k in REQUIRED}
            for k in REQUIRED:
                p=candidate/k
                if p.is_file():
                    s.setdefault("sha256", {})[k]=sha(p)
            p=candidate/REQUIRED[0]
            if p.is_file():
                with p.open(newline="",encoding="utf-8-sig") as f:
                    reader=csv.DictReader(f)
                    s["raw_fields"]=reader.fieldnames
                    s["raw_rows"]=sum(1 for _ in reader)
            for fn,key in (("experiment011_case.json","case_manifest"),
                           ("experiment011_qa.json","qa"),
                           ("measurements/environment.json","environment")):
                f=candidate/fn
                if f.is_file():
                    obj=load_json(f)
                    s[key]={"keys":sorted(obj)}
                    for name in (("source_commit","source_file_sha256","seed","block","case") if key=="case_manifest" else
                                 ("classification","raw_rows","status_counts","issues") if key=="qa" else
                                 ("host","blas_threads","git_sha","code_sha256","n","d","criterion")):
                        if name in obj:
                            v=obj[name]
                            s[key][name]=v if name not in ("case","issues") else (v.get("id") if isinstance(v,dict) else str(v)[:200])
            for k in REQUIRED:
                original=candidate/k
                copied=backup/candidate.relative_to(root)/k
                if original.is_file() and copied.is_file():
                    s.setdefault("backup_sample_parity",{})[k] = sha(original)==sha(copied)
        out["samples"].append(s)
    inv = backup / "metadata/files_sha256.csv"
    if inv.is_file():
        with inv.open(newline="",encoding="utf-8-sig") as f:
            reader=csv.DictReader(f)
            out["inventory"]["backup_inventory_fields"]=reader.fieldnames
            out["inventory"]["backup_inventory_entries"]=sum(1 for _ in reader)
    prov = backup / "metadata/provenance.json"
    if prov.is_file():
        p=load_json(prov)
        out["backup_provenance"]={k:v for k,v in p.items() if k not in ("source_checkout","source_report","backup_path")}
        out["backup_provenance"]["matches_original_hash"]=(str(p.get("report_sha256","")).lower()==sha(report_path).lower())
    if backup_report.is_file():
        out["checks"]["backup_report"]["matches_original"]=sha(backup_report)==sha(report_path)
    out["tools"]={key:shutil.which(key) for key in ("latexmk","pdflatex","bibtex")}
    for name in ("numpy","scipy","matplotlib","pandas","awesomefigures"):
        try:
            mod=__import__(name)
            out["tools"][name]=getattr(mod,"__version__","imported")
        except Exception as exc:
            out["tools"][name]="UNAVAILABLE: "+str(exc)[:180]
    if len(records)!=EXPECTED or len(seen)!=EXPECTED:
        out["warnings"].append("Report not exactly 2813 unique recorded jobs")
    if out["inventory"]["candidate_path_count_distribution"].get(0):
        out["warnings"].append("Some final-report records have no candidate run folder")
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--backup",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=inspect(a.root,a.backup)
    except Exception as exc:
        result={"error":str(exc),"traceback":traceback.format_exc()[-3000:],
                "runner":os.environ.get("RUNNER_NAME"),"account":os.environ.get("USERNAME")}
        a.output.write_text(json.dumps(result,indent=2,default=str),encoding="utf-8")
        print(json.dumps(result,indent=2))
        raise
    a.output.write_text(json.dumps(result,indent=2,default=str),encoding="utf-8")
    print(json.dumps({"report":result["report"],"inventory":result["inventory"],
                      "tools":result["tools"],"warnings":result["warnings"]},indent=2))
    if result["report"]["recorded_jobs"]!=EXPECTED or result["report"]["unique_job_keys"]!=EXPECTED:
        raise ValueError("Final report identity mismatch")
    if not result["checks"].get("backup_report",{}).get("matches_original"):
        raise ValueError("Backup report checksum mismatch")


if __name__=="__main__":
    main()
