"""Fast source-only Experiment013 validation. These are NOT measured results."""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT=Path(__file__).resolve().parents[1]
E13=ROOT/"paper/benchmarks/experiment013"


def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


runner=load(E13/"run.py","experiment013_core")
analyzer=load(E13/"analyze.py","experiment013_aggregate")


def args(**kw):
    defaults=dict(phase="all",n=None,d="1,2,3",
                  criteria="cv,gcv,mle,aicc,bic",
                  seeds=100,max_candidates=10000,max_work=50_000_000,
                  dense_limit_n=512,max_dense_bytes=2*1024**3)
    defaults.update(kw)
    return SimpleNamespace(**defaults)


def test_all_requested_axes_and_difference_order_two():
    config=runner.configuration(args())
    assert config["n"]==[32,64,128,256,512,1024,2048]
    assert config["d"]==[1,2,3]
    assert config["criteria"]==["cv","gcv","mle","aicc","bic"]
    assert config["methods"]==["naive_inverse","banded_cholesky","spectral_svd"]
    assert config["checkpoints"]==[1,10,100,1000,10000]
    plan=runner.plan_rows(config)
    assert len(plan)==7*3*5*3*5
    assert sum(p["d"]==2 for p in plan)==7*5*3*5
    assert Counter(p["eligibility"] for p in plan)["eligible"]>0
    assert sum(p["n"]==2048 and p["method"]=="naive_inverse"
               and p["M"]==10000 for p in plan)==3*5
    assert all(p["eligibility"]!="eligible" for p in plan
               if p["n"]==2048 and p["method"]=="naive_inverse")


def test_cumulative_candidate_grid_and_resource_masks():
    import numpy as np
    assert runner.candidates(1000)[0]==pytest.approx(1.0)
    assert np.array_equal(runner.candidates(10),runner.candidates(10000)[:10])
    assert len(set(runner.candidates(10000).tolist()))==10000
    assert runner.seed_for(0,64,2)!=runner.seed_for(1,64,2)
    assert runner.seed_for(0,64,2)!=runner.seed_for(0,64,3)
    ok,_,_=runner.resource_status(32,2,"cv","naive_inverse",10,
                                  max_work=50_000_000,dense_limit_n=512,
                                  max_dense_bytes=2*1024**3)
    blocked,_,_=runner.resource_status(2048,2,"cv","naive_inverse",10000,
                                  max_work=50_000_000,dense_limit_n=512,
                                  max_dense_bytes=2*1024**3)
    assert ok=="eligible" and blocked!="eligible"
    assert runner.configuration(args(phase="small"))["n"]==[32,64]


def test_real_evaluators_include_second_differences():
    # Very small accuracy smoke; no timings claimed for the paper.
    source=ROOT/"paper/benchmarks/experiment006/run.py"
    sys.path.insert(0,str(source.parent))
    engine=load(source,"experiment006_real_backend")
    y=engine.sample(32,12345,"high")
    results=[]
    for method in runner.METHODS:
        evaluator=engine.Evaluator(32,2,method)
        coord=evaluator.prepare_series(y,0.0)
        results.append(float(evaluator.evaluate(
            y,0.0,0.1,"gcv",coordinates=coord,reuse_factor=False)))
    assert results[0]==pytest.approx(results[1],rel=1e-5,abs=1e-6)
    assert results[0]==pytest.approx(results[2],rel=1e-5,abs=1e-6)


def test_incremental_checkpoint_rows_do_not_make_up_skipped_times():
    class Fake:
        @staticmethod
        def sample(n,seed,amplitude):
            return [1.]*n
        class Evaluator:
            def __init__(self,n,d,method):
                pass
            def prepare_series(self,y,mu):
                return None
            def evaluate(self,y,mu,lam,criterion,coordinates,reuse_factor):
                return (lam-1.0)**2
    c=runner.configuration(args(n="32",d="2",criteria="gcv",seeds=1,
                               max_candidates=10))
    c.update(run_id="fake001",source_commit="demo")
    for method in runner.METHODS:
        rows=runner.run_method(Fake,c,32,2,"gcv",0,method,runner.candidates(10))
        assert [r["M"] for r in rows]==[1,10]
        assert all(r["status"]=="ok" for r in rows)
        assert rows[-1]["completed"]==10
        assert float(rows[-1]["total_cold_s"])==pytest.approx(
            float(rows[-1]["method_setup_s"])+
            float(rows[-1]["cumulative_evaluation_s"]))
        assert float(rows[0]["first_evaluation_s"])>0


def test_parser_aggregates_real_status_rows_and_rejects_tampering(tmp_path):
    c=runner.configuration(args(n="32",d="2",criteria="gcv",seeds=2,
                               max_candidates=10))
    c.update(run_id=tmp_path.name,source_commit="source-sha")
    (tmp_path/"metadata.json").write_text(json.dumps(c),encoding="utf8")
    with (tmp_path/"timings.csv").open("w",newline="",encoding="utf8") as f:
        wr=csv.DictWriter(f,fieldnames=runner.FIELDS)
        wr.writeheader()
        for idx in range(2):
            for method in runner.METHODS:
                for m in c["checkpoints"]:
                    row=runner.missing_record(c,32,2,"gcv",method,idx,m,"ok")
                    row.update(completed=m,method_setup_s=1.,
                               first_evaluation_s=.1,cumulative_evaluation_s=float(m),
                               total_cold_s=1.+m,selected_lambda=1.,
                               selected_score=0.05,error="")
                    wr.writerow(row)
    (tmp_path/"completion.json").write_text(json.dumps({
        "timings_sha256":hashlib.sha256(
            (tmp_path/"timings.csv").read_bytes()).hexdigest()
    }),encoding="utf8")
    summary=analyzer.analyze(tmp_path,bootstrap=10)
    assert summary["raw_rows"]==2*3*2
    assert summary["selected_parameter_disagreements"]==0
    assert summary["paired_contrasts"]==2*3
    assert (tmp_path/"paired_speedups.csv").exists()
    (tmp_path/"timings.csv").write_bytes(
        (tmp_path/"timings.csv").read_bytes()+b"tampered")
    with pytest.raises(ValueError,match="Expected|SHA-256"):
        analyzer.parse_data(tmp_path)


def test_power_shell_launcher_stages_and_pushes_without_overwriting_source():
    text=(E13/"Run-Grid.ps1").read_text(encoding="utf8")
    assert "-Execute -Archive" in text
    assert "git worktree add -b $resultBranch" in text
    assert "git push -u origin" in text
    assert "--resume" in text
    assert "git diff --quiet" in text
    assert "Get-FileHash" in text
