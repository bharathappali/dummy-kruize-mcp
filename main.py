from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uuid
import random

app = FastAPI(title="Dummy Kruize MCP Server")

class AgentRequest(BaseModel):
    namespace: str
    deployment: str
    container: str
    env_vars: Dict[str, str]
    source_info: Optional[Dict[str, str]] = Field(default_factory=dict)  # repo, image, etc.
    observed_issue: Optional[str] = "latency_increase"
    metrics_snapshot: Optional[Dict[str, Any]] = Field(default_factory=dict)

TUNABLES = [
    {"name": "CompileThreshold", "value_type": "integer", "lower_bound": 1000, "upper_bound": 10000, "step": 100},
    {"name": "gc", "value_type": "categorical", "choices": ["G1GC", "ParallelGC", "ZGC"]},
    {"name": "TieredCompilation", "value_type": "categorical", "choices": ["true", "false"]},
    {"name": "MinHeapFreeRatio", "value_type": "integer", "lower_bound": 5, "upper_bound": 70, "step": 5}
]

TRIALS = 5

def fetch_metrics():
    return {"Throughput": random.uniform(100.0, 1000.0), "Avg_Watts": random.uniform(10.0, 100.0)}

def build_hpo_experiment(req: AgentRequest, experiment_id: str):
    return {
        "experiment_name": experiment_id,
        "experiment_id": experiment_id,
        "total_trials": TRIALS,
        "parallel_trials": 1,
        "objective_function": "1000 * (Throughput **1) / (Avg_Watts **2)",
        "value_type": "float",
        "hpo_algo_impl": "optuna_tpe",
        "direction": "maximize",
        "function_variables": [
            {"name": "Throughput", "value_type": "float"},
            {"name": "Avg_Watts", "value_type": "float"}
        ],
        "tunables": TUNABLES
    }

def run_dummy_trial(tunable_set):
    metrics = fetch_metrics()
    score = 1000 * metrics["Throughput"] / (metrics["Avg_Watts"] ** 2)
    return score, metrics

def generate_random_config():
    config = {}
    for t in TUNABLES:
        if t["value_type"] == "categorical":
            config[t["name"]] = random.choice(t["choices"])
        else:
            config[t["name"]] = random.randrange(t["lower_bound"], t["upper_bound"] + 1, t["step"])
    return config


@app.post("/mcp")
def run_hpo_loop(agent_req: AgentRequest):
    experiment_id = f"{agent_req.namespace}_{agent_req.deployment}_{str(uuid.uuid4())[:6]}"
    hpo_exp = build_hpo_experiment(agent_req, experiment_id)

    source_repo = agent_req.source_info.get("repo", f"https://github.com/demo-org/{agent_req.deployment}")
    image = agent_req.source_info.get("image", f"ghcr.io/demo-org/{agent_req.deployment}:latest")

    trial_results = []
    best_score = -1
    best_config = None

    for i in range(TRIALS):
        config = generate_random_config()
        score, metrics = run_dummy_trial(config)
        trial_results.append({
            "trial": i + 1,
            "config": config,
            "score": round(score, 2),
            "metrics": metrics
        })
        if score > best_score:
            best_score = score
            best_config = config

    java_opts_str = " ".join([f"-XX:{k}={v}" for k, v in best_config.items()])

    return {
        "experiment_id": experiment_id,
        "workload": {
            "namespace": agent_req.namespace,
            "deployment": agent_req.deployment,
            "container": agent_req.container,
            "original_env": agent_req.env_vars,
            "observed_issue": agent_req.observed_issue,
            "source_repo": source_repo,
            "image": image,
        },
        "hpo_experiment_config": hpo_exp,
        "final_best_score": round(best_score, 2),
        "best_config": best_config,
        "agent_patch_action": {
            "update_env_var": {
                "JAVA_OPTIONS": java_opts_str
            },
            "yaml_patch_hint": "Update the container spec's env section with new JAVA_OPTIONS",
        },
        "trials": trial_results,
        "explanation": "Recommended configuration improves throughput while reducing power consumption, optimizing the given objective function."
    }
