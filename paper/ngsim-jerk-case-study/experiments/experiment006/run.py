"""Experiment006: joint Gaussian REML and forecast-shrinkage comparisons.

Reuses *exactly* the Experiment005 saved analytic trajectories or the
Experiment004 saved real vehicle episodes. No regenerated historical data.
All reference estimation and rolling-origin validation use training only.

Examples:
 python run.py --mode synthetic --stage pilot --source /path/pilot/trajectories.jsonl.gz \
   --archived-forecasts /path/pilot/forecast_rows.csv --output-dir /new/exp006/pilot
 python run.py --mode real --source /path/experiment004/data \
   --archived-forecasts /path/experiment004/results/forecast_rows.csv \
   --output-dir /new/exp006/real
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import time

import numpy as np
from scipy import __version__ as scipy_version

PAPER = Path(__file__).resolve().parents[2]
REPO = PAPER.parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))
from trendestimation import TrendSmoother  # noqa: E402
from reml import DifferenceLikelihood  # noqa: E402
from analyze import produce as produce_diagnostics  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp006_ngsim_case", PAPER / "run_case.py")
assert _spec is not None and _spec.loader is not None
_case = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_case)

CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
N = 80
HORIZONS = (5, 10, 20)
RULES = ("guerrero_last3", "local25")
DT = 0.1
ALPHAS = (0.0, 0.5, 1.0)
METHODS = ("joint_reml_continuous", "joint_reml_grid",
           "fixed_zero_continuous", "plugin_sample_continuous",
           "plugin_global_ols_continuous")
FOLDS = {5: (45, 55, 65), 10: (45, 55, 65), 20: (40, 50, 60)}


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def load_synthetic(path: Path, stage: str):
    if path.suffix != ".gz" or not path.is_file():
        raise FileNotFoundError(f"Missing archived Experiment005 simulation: {path}")
    episodes = []
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            if not item["trial_id"].startswith(stage+"_"):
                raise ValueError("Stage/source record mismatch")
            truth = np.asarray(item["clean_position_m"], dtype=float)
            observed = np.asarray(item["observed_noisy_position_m"], dtype=float)
            if len(observed) != 100 or len(truth) != 100:
                raise ValueError("Unexpected archived simulation observation length")
            if not np.isfinite(truth).all() or not np.isfinite(observed).all():
                raise ValueError("Nonfinite historic simulation dataset")
            episodes.append({
                "id":item["trial_id"],"stratum":item["scenario_key"],
                "site":"simulation","session":item["scenario_key"],
                "train":observed[:N], "future":truth[N:N+20],
                "truth_train":truth[:N], "noise":item["noise_model"],
            })
    expected = {"pilot":96,"confirm":1296}[stage]
    if len(episodes) != expected:
        raise ValueError(f"Expected {expected} preserved trials, got {len(episodes)}")
    return episodes, sha256(path)


def load_real(path: Path):
    raw = path / "selected_positions.csv"
    manifest = path / "download_manifest.json"
    catalog = path / "episode_catalog.json"
    for p in (raw, manifest, catalog):
        if not p.exists():
            raise FileNotFoundError(f"Missing original Experiment004 source: {p}")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if sha256(raw) != data["selected_positions_csv_sha256"]:
        raise ValueError("NGSIM source positions do not match original manifest")
    episodes_meta = json.loads(catalog.read_text(encoding="utf-8"))
    groups = defaultdict(list)
    with raw.open(encoding="utf-8",newline="") as stream:
        for row in csv.DictReader(stream):
            groups[row["episode_id"]].append((
                int(row["timestamp_ms"]),int(row["frame_id"]),
                float(row["longitudinal_m"])
            ))
    episodes = []
    for meta in episodes_meta:
        rows = groups[meta["episode_id"]]
        if len(rows) != meta["n_frames"]:
            raise ValueError("Source episode length changed")
        timestamps = np.array([x[0] for x in rows])
        frames = np.array([x[1] for x in rows])
        if np.any(np.diff(timestamps)!=100) or np.any(np.diff(frames)!=1):
            raise ValueError("Source episode lost time/frame continuity")
        positions = np.array([x[2] for x in rows],dtype=float)
        if len(positions) < 120 or not np.isfinite(positions).all():
            raise ValueError("Missing observed future or invalid real positions")
        positions -= positions[0]
        episodes.append({
            "id":meta["episode_id"],"stratum":meta["session_proxy"],
            "site":meta["site"],"session":meta["session_proxy"],
            "train":positions[20:100],"future":positions[100:120],
            "truth_train":None,"noise":"recorded",
        })
    if len(episodes) != data["episode_count"] or len(episodes)!=200:
        raise ValueError("Original Experiment004 catalog has changed")
    return episodes, sha256(raw)


class CachedModels:
    def __init__(self):
        self.values = {}

    def get(self, n):
        if n not in self.values:
            smoother = TrendSmoother(n, order=3)
            self.values[n] = (smoother, DifferenceLikelihood(smoother))
        return self.values[n]


def raw_mu(y):
    return float(np.mean(np.diff(y,n=3)))


def cubic_ols_mu(y):
    t = np.arange(len(y),dtype=float)*DT
    coefs = np.polynomial.Polynomial.fit(t,y,3).convert().coef
    return float(6.0*coefs[3]*DT**3)


def continuation(trend, mu, rule, horizon=20):
    if rule=="guerrero_last3":
        return np.asarray(
            _case.continuation_guerrero_d3(trend,mu,horizon),dtype=float
        )
    if rule=="local25":
        return np.asarray(
            _case.continuation(trend,order=3,mu=mu,horizon=horizon),dtype=float
        )
    raise ValueError("Unknown continuation: "+rule)


def prepared_folds(train, cache: CachedModels):
    """For each fold refit lambda AND mu using ONLY its historical prefix.

    PLS and continuation are affine in mu for fixed lambda. Two endpoint
    forecasts therefore permit exact interpolation for alpha in [0,1].
    """
    result = {}
    for origin in sorted(set(x for origins in FOLDS.values() for x in origins)):
        prefix = train[:origin]
        smoother, reml = cache.get(origin)
        fit = reml.optimize(prefix)
        trend_zero = smoother.fit(prefix,lambda_=fit.lambda_,mu=0).trend
        trend_full = smoother.fit(prefix,lambda_=fit.lambda_,mu=fit.mu).trend
        forecasts = {}
        for rule in RULES:
            forecasts[(rule,"zero")] = continuation(trend_zero,0,rule,20)
            forecasts[(rule,"full")] = continuation(trend_full,fit.mu,rule,20)
        result[origin] = forecasts
    return result


def choose_shrinkage(train, folds, horizon, rule):
    scores = []
    for alpha in ALPHAS:
        risks = []
        for origin in FOLDS[horizon]:
            f = folds[origin]
            forecast = ((1-alpha)*f[(rule,"zero")][:horizon]
                        +alpha*f[(rule,"full")][:horizon])
            diff = forecast - train[origin:origin+horizon]
            risks.append(float(np.mean(diff**2)))
        scores.append(float(np.mean(risks)))
    # Equal CV scores prefer more shrinkage (smaller alpha).
    chosen = int(np.argmin(scores))
    return ALPHAS[chosen], scores


def estimate_methods(train, cache):
    smoother, solver = cache.get(len(train))
    grid = tuple(smoother.lambda_for_smoothness(v)
                 for v in CONFIG["smoothness_grid"])
    policies = {
        "joint_reml_continuous":(None,"continuous"),
        "joint_reml_grid":(None,"grid"),
        "fixed_zero_continuous":(0.0,"continuous"),
        "plugin_sample_continuous":(raw_mu(train),"continuous"),
        "plugin_global_ols_continuous":(cubic_ols_mu(train),"continuous"),
    }
    choices={}
    fitted={}
    for name,(mu,search) in policies.items():
        result = solver.optimize(train,fixed_mu=mu,
                                 search=search,grid=grid if search=="grid" else None)
        choices[name]=result
        fitted[name]=np.asarray(
            smoother.fit(train,lambda_=result.lambda_,mu=result.mu).trend,dtype=float
        )
    return choices,fitted


def evaluate_one(episode, cache):
    y = episode["train"]
    future = episode["future"]
    if y.shape!=(N,) or future.shape!=(20,):
        raise ValueError("Malformed training or future windows")
    choices, trends = estimate_methods(y,cache)
    rows = {"selections":[],"forecasts":[],"jerk":[],"cv":[]}
    source_id = episode["id"]
    shared = {"sample_id":source_id,"stratum":episode["stratum"],
              "site":episode["site"],"session_proxy":episode["session"]}
    truth = episode["truth_train"]
    known = np.diff(truth,n=3)/(DT**3) if truth is not None else None

    def jerk_metric(method, trend, mu, horizon=None):
        result={**shared,"method":method,
                "horizon_frames":horizon if horizon is not None else "",
                "reference_mu_discrete_m":float(mu),
                "status":"ok"}
        if known is not None:
            e = (np.diff(trend,n=3)/(DT**3)) - known
            result.update({"jerk_mse_m2_s6":float(np.mean(e*e)),
                           "historical_position_mse_m2":float(np.mean((trend-truth)**2))})
        else:
            result.update({"jerk_mse_m2_s6":"","historical_position_mse_m2":""})
        rows["jerk"].append(result)

    def forecast_metric(name, pred, h, alpha=""):
        delta = pred[:h]-future[:h]
        if not np.all(np.isfinite(delta)):
            raise ValueError(f"Nonfinite prediction: {name}")
        rows["forecasts"].append({
            **shared,"method":name,"horizon_frames":h,"alpha":alpha,
            "mse_m2":float(np.mean(delta**2)),
            "mae_m":float(np.mean(np.abs(delta))),
            "final_error_m":float(delta[-1]),"status":"ok",
        })

    for name,fit in choices.items():
        rows["selections"].append({
            **shared,"method":name,"selector":fit.selector,
            "selection_policy":fit.position,
            "lambda":fit.lambda_,"smoothness":fit.smoothness,
            "reference_mu_discrete_m":fit.mu,
            "reference_jerk_m_s3":fit.mu/DT**3,
            "criterion_score":fit.score,
            "evaluations":fit.n_evaluations,"status":"ok",
        })
        jerk_metric(name,trends[name],fit.mu)
        for rule in RULES:
            pred = continuation(trends[name],fit.mu,rule)
            for h in HORIZONS:
                forecast_metric(name+"_"+rule,pred,h)

    # Nested training-only CV: each inner fold chooses its own REML lambda.
    folds = prepared_folds(y,cache)
    j = choices["joint_reml_continuous"]
    smoother,_ = cache.get(N)
    trend_zero = smoother.fit(y,lambda_=j.lambda_,mu=0.0).trend
    trend_full = trends["joint_reml_continuous"]
    for rule in RULES:
        p0 = continuation(trend_zero,0.0,rule)
        p1 = continuation(trend_full,j.mu,rule)
        for h in HORIZONS:
            alpha,cv_scores = choose_shrinkage(y,folds,h,rule)
            pname="shrink_tscv_"+rule
            rows["cv"].append({
                **shared,"method":pname,"horizon_frames":h,
                "selected_alpha":alpha,
                "alpha_grid":json.dumps(ALPHAS),
                "fold_origins":json.dumps(FOLDS[h]),
                "inner_cv_mse_m2":json.dumps(cv_scores),
                "lambda_source":"full_window_joint_reml",
                "alpha_selection":"nested_training_only_rolling_origin",
                "status":"ok",
            })
            pred=(1-alpha)*p0+alpha*p1
            forecast_metric(pname,pred,h,alpha)
            trend=(1-alpha)*trend_zero+alpha*trend_full
            jerk_metric(pname,trend,alpha*j.mu,horizon=h)

    return rows


def csv_write(path,rows):
    if not rows:
        raise ValueError(f"Empty experimental data: {path}")
    with path.open("x",encoding="utf-8",newline="") as handle:
        w=csv.DictWriter(handle,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def load_archived(path: Path, mode: str, episodes):
    if path is None:
        return []
    allowed = {ep["id"] for ep in episodes}
    source = []
    with path.open(encoding="utf-8",newline="") as handle:
        for row in csv.DictReader(handle):
            sample_id = row["trial_id"] if mode=="synthetic" else row["episode_id"]
            if sample_id not in allowed:
                continue
            if row["status"]!="ok":
                continue
            source.append({
                "sample_id":sample_id,
                "method":"archived:"+row["method"],
                "horizon_frames":int(row["horizon_frames"]),
                "mse_m2":float(row["mse_m2"]),
                "status":"ok",
            })
    return source


def summarize(rows,archived,episodes,mode):
    expanded=rows+archived
    group=defaultdict(list)
    for row in expanded:
        if row["status"]=="ok":
            group[(row["method"],int(row["horizon_frames"]))].append(
                float(row["mse_m2"])
            )
    summary=[
        {"method":method,"horizon_frames":h,"n_valid":len(vals),
         "rmse_m":float(math.sqrt(np.mean(vals))),
         "mean_mse_m2":float(np.mean(vals))}
        for (method,h),vals in sorted(group.items())
    ]
    # Predeclared paired comparisons against the same archived GCV spline.
    baseline="archived:spline_gcv_taylor2"
    alternatives=("joint_reml_continuous_local25",
                  "joint_reml_continuous_guerrero_last3",
                  "joint_reml_grid_local25",
                  "fixed_zero_continuous_local25",
                  "plugin_sample_continuous_local25",
                  "plugin_global_ols_continuous_local25",
                  "shrink_tscv_local25",
                  "shrink_tscv_guerrero_last3",
                  "archived:pls_mle_zero_local25",
                  "archived:pls_mle_ols_global_local25")
    bykey={(r["sample_id"],r["method"],int(r["horizon_frames"])):r
           for r in expanded}
    epbyid={e["id"]:e for e in episodes}
    comparison=[]
    rng=np.random.default_rng(20261109)
    n_resamples=int(CONFIG["validation"]["bootstrap_repetitions"])
    for method in alternatives:
        for h in HORIZONS:
            strata=defaultdict(list)
            for sample_id, ep in epbyid.items():
                x=bykey.get((sample_id,method,h))
                b=bykey.get((sample_id,baseline,h))
                if x is None or b is None:
                    continue
                if mode=="synthetic":
                    group_key=ep["stratum"]
                else:
                    group_key=ep["site"]+"|"+ep["session"]
                strata[group_key].append(float(x["mse_m2"])-float(b["mse_m2"]))
            n=sum(len(x) for x in strata.values())
            result={"method":method,"reference":baseline,"horizon_frames":h,
                    "n_paired":n}
            if n<12:
                result.update({"mean_delta_mse_m2":"","ci_low_m2":"","ci_high_m2":"",
                               "status":"insufficient_matched_rows"})
            else:
                values=np.concatenate([np.asarray(v) for v in strata.values()])
                result["mean_delta_mse_m2"]=float(np.mean(values))
                boots=[]
                if mode=="synthetic":
                    # Independent generated trial is the resampling unit.
                    arrays=[np.asarray(v,dtype=float) for v in strata.values()]
                    for _ in range(n_resamples):
                        boots.append(sum(float(a[rng.integers(len(a),size=len(a))].sum())
                                         for a in arrays)/n)
                    result["resampling_unit"]="independent_trial_within_scenario"
                else:
                    # Five session proxy groups only: block-level resampling,
                    # NOT a valid population-level 95% confidence statement.
                    sites=sorted({e["site"] for e in episodes})
                    block_by_site={
                        site:[np.asarray(v,dtype=float) for key,v in strata.items()
                              if key.startswith(site+"|")] for site in sites
                    }
                    for _ in range(n_resamples):
                        sampled=[]
                        for site,groups in block_by_site.items():
                            if groups:
                                sampled.extend(groups[rng.integers(len(groups))]
                                               for _ in range(len(groups)))
                        boots.append(float(np.mean(np.concatenate(sampled))))
                    result["resampling_unit"]="five_coarse_capture_blocks_exploratory"
                a,b=np.quantile(boots,[.025,.975])
                result.update({"ci_low_m2":float(a),"ci_high_m2":float(b),
                               "status":"exploratory_interval"})
            comparison.append(result)
    return summary,comparison


def run(mode,source,output,stage,archived_path=None):
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing experiment: {output}")
    started=time.perf_counter()
    if mode=="synthetic":
        episodes,source_hash=load_synthetic(source,stage)
    elif mode=="real":
        episodes,source_hash=load_real(source)
    else:
        raise ValueError("Unknown mode")
    cache=CachedModels()
    data={"forecasts":[],"jerk":[],"selections":[],"cv":[]}
    errors=[]
    for k,episode in enumerate(episodes,1):
        try:
            result=evaluate_one(episode,cache)
            for label,rows in result.items():
                data[label].extend(rows)
        except (ValueError, ArithmeticError, FloatingPointError,
                np.linalg.LinAlgError) as error:
            errors.append({"sample_id":episode["id"],"reason":repr(error)})
        if k%25==0 or k==len(episodes):
            print(f"Experiment006 {mode}/{stage} {k}/{len(episodes)}",flush=True)
    if errors:
        # No fake data. Preserve full explicit failure report.
        output.mkdir(parents=True,exist_ok=False)
        (output/"errors.json").write_text(json.dumps(errors,indent=2)+"\n",encoding="utf-8")
        raise RuntimeError(f"{len(errors)} samples failed; see {output/'errors.json'}")
    old=load_archived(archived_path,mode,episodes)
    summary,paired=summarize(data["forecasts"],old,episodes,mode)
    output.mkdir(parents=True,exist_ok=False)
    for label,rows in data.items():
        csv_write(output/(label+"_rows.csv"),rows)
    csv_write(output/"summary.csv",summary)
    csv_write(output/"paired_comparisons.csv",paired)
    diagnostics = produce_diagnostics(output, mode)
    count=Counter()
    for row in data["cv"]:
        count[str(row["selected_alpha"])]+=1
    manifest={
        "schema":1,"experiment":"experiment006","mode":mode,
        "stage":stage,"status":"completed",
        "source_path":str(source.resolve()),"source_sha256":source_hash,
        "archived_baselines_path":str(archived_path.resolve()) if archived_path else None,
        "archived_baselines_sha256":sha256(archived_path) if archived_path else None,
        "n_samples":len(episodes),"n_real_jerk_labels":sum(e["truth_train"] is not None
                                                        for e in episodes),
        "forecast_count":len(data["forecasts"]),"selection_count":len(data["selections"]),
        "historical_jerk_records":len(data["jerk"]),
        "cv_rule_horizon_records":len(data["cv"]),"archived_forecast_records":len(old),
        "alpha_counts":dict(count),
        "diagnostics":diagnostics,
        "output_dir":str(output.resolve()),
        "source_commit":os.environ.get("GITHUB_SHA","manual"),
        "runner_name":os.environ.get("RUNNER_NAME","manual"),
        "runner_id":os.environ.get("GITHUB_RUN_ID",""),
        "elapsed_seconds":time.perf_counter()-started,
        "numpy_version":np.__version__,"scipy_version":scipy_version,
        "method_estimators":list(METHODS),
        "continuations":list(RULES),"horizons_frames":list(HORIZONS),
        "time_cv_origins":FOLDS,"alpha_candidates":list(ALPHAS),
        "likelihood":"mean-adjusted Gaussian REML with GLS mu(lambda), fixed-mu comparator",
        "parameter_search":"61 fixed log-lambda mesh, all observed local minima refined, plus exact 0/infinity limits",
        "mean_reference_units":"discrete D3 position, physical jerk = mu/0.1^3",
        "inferential_scope":"simulation-conditional" if mode=="synthetic" else
            "only five coarse recording-session proxies, descriptive not population CI",
        "existing_archives_preserved":True,
    }
    (output/"run_manifest.json").write_text(json.dumps(
        manifest,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    top=sorted((r for r in summary if r["horizon_frames"]==10),
               key=lambda r:r["rmse_m"])
    text=[
        f"# Experiment006 {mode} {stage}: unknown-mu REML and forecast shrinkage",
        "",
        f"**Completed samples:** {len(episodes)}; full source SHA-256: {source_hash}.",
        "All selections and inner rolling-origin validation use historical data only.",
        "Joint REML eliminates one unknown mean coefficient; the fixed-mu selectors",
        "profile the nuisance variance but condition on a prechosen mean.",
        "",
        "## One-second future-position RMSE (lower is better)",
        "",
        "| Method | Matched windows | RMSE (m) |",
        "| --- | ---: | ---: |",
    ]
    for row in top:
        text.append(f"| {row['method']} | {row['n_valid']} | {row['rmse_m']:.6f} |")
    text += ["","## Scientific limits",
             "- Real data target is future recorded camera position; true jerk is unavailable.",
             "- Synthetic target is future clean analytic position and exact D3 jerk.",
             "- Older PLS/spline baselines are read-only, from the archived original runs.",
             "- Continuous optimization checks a 61-point logarithmic lattice and its",
             "  observed minima and boundaries; it is not a certified globally optimal solver.",
             "- Shrinkage alpha uses nested historical rolling-origin folds and",
             "  a full-window REML penalty; it is forecast-targeted, not pure REML.",
             "- Real bootstrap samples only five coarse capture blocks; no population",
             "  significance claim. Simulation intervals condition on the chosen DGP.",
             "- No future truth enters reference or smoothing-parameter selection.",
             ""]
    (output/"RESULTS.md").write_text("\n".join(text),encoding="utf-8")
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=("synthetic","real"),required=True)
    p.add_argument("--stage",choices=("pilot","confirm","real"),required=True)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--archived-forecasts",type=Path)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    if (args.mode=="real")!=(args.stage=="real"):
        p.error("mode real requires stage real; synthetic requires pilot or confirm")
    run(args.mode,args.source,args.output_dir,args.stage,args.archived_forecasts)


if __name__=="__main__":
    main()
