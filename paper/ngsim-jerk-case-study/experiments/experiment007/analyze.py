"""Experiment007 paired factorial diagnostics and cluster-aware uncertainty.

The independent stochastic unit is the PARENT replicate, not each of
its 27 coupled parameter/noise conditions. All inference resamples
whole parents. Interventions are predeclared in config.json.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


def read_csv(path: Path):
    with path.open("r",encoding="utf-8",newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows):
    if not rows:
        raise ValueError("Cannot write empty table: "+str(path))
    with path.open("x",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def method_cell_rows(rows):
    cells=defaultdict(list)
    for row in rows:
        key=(row["method"],row["dynamics"],row["noise_type"],
             float(row["sigma_e_m"]),float(row["sigma_j_m_s3"]))
        cells[key].append(row)
    result=[]
    for key,group in sorted(cells.items()):
        good=[r for r in group if r["status"]=="ok"]
        if not good:
            raise ValueError("Method has zero valid cells: "+repr(key))
        selected=np.asarray([float(r["S_selected"]) for r in good])
        covariance=np.asarray([float(r["S_true_covariance"]) for r in good])
        nominal=np.asarray([float(r["S_nominal_iid"]) for r in good])
        jerkerr=np.asarray([float(r["historical_jerk_mse_m2_s6"]) for r in good])
        zeros=sum(r["selection_policy"]=="zero_limit" for r in good)
        infinities=sum(r["selection_policy"]=="infinity_limit" for r in good)
        components=[r for r in good
                    if r["estimated_observation_variance_m2"] not in ("",None)
                    and math.isfinite(float(r["estimated_observation_variance_m2"]))]
        varratios=np.asarray([
            float(r["estimated_observation_variance_m2"])/
            float(r["true_observation_variance_m2"]) for r in components
        ],dtype=float)
        method,dynamics,noise,sige,sigj=key
        result.append({
            "method":method,"dynamics":dynamics,"noise_type":noise,
            "sigma_e_m":sige,"sigma_j_m_s3":sigj,
            "model_correct":dynamics=="iid" and noise=="iid",
            "n_total":len(group),"n_ok":len(good),
            "n_invalid":len(group)-len(good),
            "mean_S":float(np.mean(selected)),
            "median_S":float(np.median(selected)),
            "sd_S":float(np.std(selected,ddof=1)) if len(selected)>1 else 0.0,
            "true_S_covariance":float(np.mean(covariance)),
            "true_S_nominal":float(np.mean(nominal)),
            "S_bias":float(np.mean(selected-covariance)),
            "S_mae":float(np.mean(np.abs(selected-covariance))),
            "S_rmse":float(np.sqrt(np.mean((selected-covariance)**2))),
            "n_lambda_zero":zeros,"n_lambda_inf":infinities,
            "known_jerk_rmse_m_s3":float(np.sqrt(np.mean(jerkerr))),
            "n_estimated_observation_variance":len(varratios),
            "mean_observation_variance_ratio":float(np.mean(varratios))
                if len(varratios) else "",
            "median_observation_variance_ratio":float(np.median(varratios))
                if len(varratios) else "",
        })
    return result


def effect_pairs(rows, config):
    factors=config["factors"]
    noises=tuple(float(v) for v in factors["position_noise_sd_m"])
    jerks=tuple(float(v) for v in factors["latent_jerk_innovation_sd_m_s3"])
    bykey={}
    for row in rows:
        if row["status"]!="ok":
            continue
        key=(row["method"],row["parent_id"],row["dynamics"],
             row["noise_type"],float(row["sigma_e_m"]),
             float(row["sigma_j_m_s3"]))
        if key in bykey:
            raise ValueError("Duplicate factorial treatment: "+repr(key))
        bykey[key]=row

    effects=[]
    def add(method,parent,dyn,noise,treatment,fixed,value,truth,rank=None):
        effects.append({
            "method":method,"parent_id":parent,"dynamics":dyn,"noise_type":noise,
            "intervention":treatment,"fixed_factor_value":fixed,
            "delta_estimated_S":float(value),"delta_true_covariance_S":float(truth),
            "triple_level_spearman":float(rank) if rank is not None
                and np.isfinite(rank) else "",
            "model_correct":dyn=="iid" and noise=="iid",
        })

    groups=sorted({(r["method"],r["parent_id"],r["dynamics"],
                    r["noise_type"]) for r in rows})
    for method,parent,dyn,noise in groups:
        def get(e,j):
            return bykey.get((method,parent,dyn,noise,e,j))
        for j in jerks:
            levels=[get(e,j) for e in noises]
            if any(row is None for row in levels):
                continue
            vals=[float(r["S_selected"]) for r in levels]
            truths=[float(r["S_true_covariance"]) for r in levels]
            rho=(spearmanr(noises,vals).statistic
                 if len(set(vals))>1 else float("nan"))
            add(method,parent,dyn,noise,"noise_increase",j,
                vals[-1]-vals[0],truths[-1]-truths[0],rho)
        for e in noises:
            levels=[get(e,j) for j in jerks]
            if any(row is None for row in levels):
                continue
            vals=[float(r["S_selected"]) for r in levels]
            truths=[float(r["S_true_covariance"]) for r in levels]
            rho=(spearmanr(jerks,vals).statistic
                 if len(set(vals))>1 else float("nan"))
            add(method,parent,dyn,noise,"jerk_variability_increase",e,
                vals[-1]-vals[0],truths[-1]-truths[0],rho)
        # Equal ratio = sigma_e/sigma_j = 0.025, but sigma_e differs
        # 4x and observation precision 16x. S should be invariant.
        smaller=get(.05,2.0)
        bigger=get(.2,8.0)
        if smaller is not None and bigger is not None:
            add(method,parent,dyn,noise,"same_ratio_precision_change",.025,
                float(bigger["S_selected"])-float(smaller["S_selected"]),
                float(bigger["S_true_covariance"])-
                float(smaller["S_true_covariance"]))
    return effects


def effect_summaries(effects,config):
    """Aggregate paired contrasts within independent parents before bootstrap."""
    values=defaultdict(lambda:defaultdict(list))
    for row in effects:
        key=(row["method"],row["intervention"],row["dynamics"],
             row["noise_type"])
        values[key][row["parent_id"]].append(row)
    results=[]
    rng=np.random.default_rng(int(config["analysis"]["bootstrap_seed"]))
    n_boot=int(config["analysis"]["bootstrap_reps"])
    for key,parents in sorted(values.items()):
        observed=np.asarray([
            np.mean([float(x["delta_estimated_S"]) for x in rows])
            for _,rows in sorted(parents.items())
        ],dtype=float)
        theoretical=np.asarray([
            np.mean([float(x["delta_true_covariance_S"]) for x in rows])
            for _,rows in sorted(parents.items())
        ],dtype=float)
        triple=[float(x["triple_level_spearman"])
                for group in parents.values()
                for x in group if x["triple_level_spearman"]!=""]
        bootstrap=np.mean(
            observed[rng.integers(len(observed),size=(n_boot,len(observed)))],
            axis=1
        )
        lo,hi=np.quantile(bootstrap,[.025,.975])
        method,intervention,dyn,noise=key
        target_sign=(
            "positive" if intervention=="noise_increase" else
            "negative" if intervention=="jerk_variability_increase" else
            "zero"
        )
        expected_pass=(
            float(np.mean(observed>0)) if target_sign=="positive" else
            float(np.mean(observed<0)) if target_sign=="negative" else
            float(np.mean(np.abs(observed)<0.02))
        )
        results.append({
            "method":method,"intervention":intervention,
            "dynamics":dyn,"noise_type":noise,
            "model_correct":dyn=="iid" and noise=="iid",
            "n_independent_parents":len(parents),
            "mean_delta_selected_S":float(np.mean(observed)),
            "ci_95_low_cluster":float(lo),
            "ci_95_high_cluster":float(hi),
            "mean_delta_true_S":float(np.mean(theoretical)),
            "fraction_parent_effect_correct_sign_or_near_zero":expected_pass,
            "mean_within_parent_spearman":float(np.mean(triple))
                if triple else "",
            "n_three_level_ranks_computable":len(triple),
            "bootstrap":"resample independent parent IDs; paired factorial outcomes together",
        })
    return results


def calibration_summary(rows):
    groups=defaultdict(list)
    for row in rows:
        groups[(row["method"],row["dynamics"],row["noise_type"])].append(row)
    summaries=[]
    for key,group in sorted(groups.items()):
        valid=[x for x in group if x["status"]=="ok"]
        estimates=np.asarray([float(x["S_selected"]) for x in valid])
        truth=np.asarray([float(x["S_true_covariance"]) for x in valid])
        if not len(valid):
            continue
        rank=float(spearmanr(estimates,truth).statistic) if (
            len(set(estimates))>1 and len(set(truth))>1
        ) else float("nan")
        method,dyn,noise=key
        summaries.append({
            "method":method,"dynamics":dyn,"noise_type":noise,
            "model_correct":dyn=="iid" and noise=="iid",
            "n_valid":len(valid),"n_invalid":len(group)-len(valid),
            "spearman_selected_vs_true_S":rank if np.isfinite(rank) else "",
            "mean_bias_S":float(np.mean(estimates-truth)),
            "mae_S":float(np.mean(np.abs(estimates-truth))),
            "rmse_S":float(np.sqrt(np.mean((estimates-truth)**2))),
            "fraction_lambda_zero":float(np.mean([
                x["selection_policy"]=="zero_limit" for x in valid
            ])),
            "fraction_lambda_infinity":float(np.mean([
                x["selection_policy"]=="infinity_limit" for x in valid
            ])),
        })
    return summaries


def plot_report(root: Path,per_cell,calibration):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as e:
        return {"created":False,"reason":str(e)}
    figdir=root/"figures"
    figdir.mkdir(exist_ok=False)
    files=[]
    focused=[x for x in per_cell
             if x["dynamics"]=="iid" and x["noise_type"]=="iid"]
    methods=sorted({x["method"] for x in focused})
    for method in methods:
        fig,ax=plt.subplots(figsize=(8,5))
        data=[x for x in focused if x["method"]==method]
        for j in sorted({x["sigma_j_m_s3"] for x in data}):
            sub=sorted([x for x in data if x["sigma_j_m_s3"]==j],
                       key=lambda x:x["sigma_e_m"])
            xs=[x["sigma_e_m"] for x in sub]
            ax.plot(xs,[x["mean_S"] for x in sub],marker="o",
                    label=f"selected S; jerk SD={j:g} m/s³")
            ax.plot(xs,[x["true_S_covariance"] for x in sub],
                    linestyle="--",label=f"theory; jerk SD={j:g}")
        ax.set_xscale("log")
        ax.set_ylim(-.03,1.03)
        ax.set(xlabel="Known position-noise SD (m)",
               ylabel="Normalized smoothness / spectral noise fraction",
               title=f"Noise intervention, correct covariance model: {method}")
        ax.grid(alpha=.2);ax.legend(fontsize=7)
        fig.tight_layout()
        filename=f"S_vs_observation_noise_{method}.png"
        fig.savefig(figdir/filename,dpi=170)
        plt.close(fig)
        files.append("figures/"+filename)

    fig,ax=plt.subplots(figsize=(7,6))
    for method in methods:
        sub=[x for x in focused if x["method"]==method]
        ax.scatter([x["true_S_covariance"] for x in sub],
                   [x["mean_S"] for x in sub],label=method)
    ax.plot([0,1],[0,1],linestyle="--",label="ideal calibration")
    ax.set(xlabel="True relative spectral noise fraction",
           ylabel="Mean selected S",
           title="S as noise attribution: paired factorial calibration")
    ax.set_xlim(0,1);ax.set_ylim(0,1);ax.grid(alpha=.2)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(figdir/"S_calibration_iid.png",dpi=180)
    plt.close(fig)
    files.append("figures/S_calibration_iid.png")
    return {"created":True,"files":files}


def produce(root:Path,config:dict,stage:str):
    rows=read_csv(root/"selections.csv")
    theory=read_csv(root/"theory_cells.csv")
    expected_trials=int(config["stages"][stage+"_cases"])
    assert len(rows)==expected_trials*len(config["selection"]["gcv_s_grid"])*0 + expected_trials*4
    if len(theory)!=(
        len(config["factors"]["position_noise_sd_m"])
        *len(config["factors"]["latent_jerk_innovation_sd_m_s3"])
        *len(config["factors"]["jerk_structures"])
        *len(config["factors"]["observation_noise_models"])
    ):
        raise AssertionError("Theory-cell size mismatch")
    cells=method_cell_rows(rows)
    effects=effect_pairs(rows,config)
    effect_summary=effect_summaries(effects,config)
    cal=calibration_summary(rows)
    write_csv(root/"per_cell.csv",cells)
    write_csv(root/"interventions.csv",effects)
    write_csv(root/"effects_summary.csv",effect_summary)
    write_csv(root/"calibration_summary.csv",cal)
    plots=plot_report(root,cells,cal)
    model_correct=[x for x in cal if x["model_correct"]]
    target_effects=[x for x in effect_summary if x["model_correct"]]
    count=Counter(row["status"] for row in rows)
    summary={
        "stage":stage,
        "n_trials":expected_trials,"n_selections":len(rows),
        "n_model_correct_methods":len(model_correct),
        "n_method_cells":len(cells),
        "n_paired_interventions":len(effects),
        "n_parent_cluster_effect_estimates":len(effect_summary),
        "n_valid_selection":count["ok"],"n_invalid_selection":count["invalid"],
        "correct_model_calibration":model_correct,
        "correct_model_paired_effects":target_effects,
        "plots":plots,
        "scientific_limitations":[
            "S is relative noise attribution, not absolute observation precision",
            "A fixed variance ratio cannot identify absolute observation noise SD",
            "Correlated noise and AR1 jerk violate the scalar covariance model",
            "Terminal random sign spike is non-Gaussian and adds rank-one covariance",
            "Nonstationary jerk reversal violates constant reference mean",
            "Inference resamples independent parent innovations, not correlated cells",
            "Synthetic evidence is conditional on the registered data-generating processes",
            "Boundary selection and finite n can break empirical monotonicity",
        ],
    }
    (root/"summary.json").write_text(
        json.dumps(summary,indent=2,allow_nan=False)+"\n",encoding="utf-8"
    )
    lines=[
        f"# Experiment007 {stage}: Does PLS smoothness indicate relative noise?",
        "",
        f"**Cases:** {expected_trials}; **selected S values:** {len(rows)};",
        f"**invalid selections:** {count['invalid']}.",
        f"**Paired interventions:** {len(effects)}, clustered at parent innovations.",
        "",
        "## Calibration when Gaussian iid jerk and iid measurement assumptions hold",
        "",
        "| Selector | Spearman(selected S, theoretical noise fraction) | MAE(S) | Zero-boundary share |",
        "| --- | ---: | ---: | ---: |",
    ]
    for r in model_correct:
        rank=r["spearman_selected_vs_true_S"]
        lines.append(
            f"| {r['method']} | {float(rank):.3f} | {r['mae_S']:.4f} "
            f"| {r['fraction_lambda_zero']:.1%} |"
            if rank!="" else
            f"| {r['method']} | NA (constant) | {r['mae_S']:.4f} | {r['fraction_lambda_zero']:.1%} |"
        )
    lines += [
        "",
        "## Paired interventions under the model-correct Gaussian iid case",
        "",
        "| Selector | Intervention | Mean estimated ΔS | Cluster bootstrap 95% interval | Mean true ΔS |",
        "| --- | --- | ---: | --- | ---: |",
    ]
    for r in target_effects:
        lines.append(
            f"| {r['method']} | {r['intervention']} "
            f"| {r['mean_delta_selected_S']:+.4f}"
            f" | [{r['ci_95_low_cluster']:+.4f}, {r['ci_95_high_cluster']:+.4f}] "
            f"| {r['mean_delta_true_S']:+.4f} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "The reference theory is the unconditional covariance-trace fraction.",
        "When both observation and jerk innovation disturbances are iid and Gaussian,",
        "this agrees exactly with Guerrero-style normalized S at the TRUE variance ratio.",
        "Estimated S comes from likelihood/GCV selection and is not guaranteed",
        "unbiased or monotone in finite samples. Results must report departures.",
        "Increasing measurement noise at fixed latent jerk SD should increase true S;",
        "increasing latent jerk variability at fixed observation noise should decrease it.",
        "Scaling BOTH observation and jerk SD by the same factor leaves true S unchanged,",
        "even though absolute observation precision changes. Hence S cannot on its own",
        "measure sensor precision. Correlated noise, endpoint contamination and",
        "nonstationary jerk are deliberately included as model stress tests.",
        "",
        "All individual known true jerk, position, observation errors, selected",
        "penalties, lambda, mu, component variance estimates and treatment seeds",
        "are archived with independent source commit, configs and hashes.",
        "",
    ]
    (root/"RESULTS.md").write_text("\n".join(lines),encoding="utf-8")
    return {
        "n_per_cell":len(cells),
        "n_paired_interventions":len(effects),
        "n_cluster_effects":len(effect_summary),
        "n_calibration_rows":len(cal),
        "plots":plots
    }
