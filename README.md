# 🚀 Dummy Kruize MCP Server

This project simulates a **Model Control Protocol (MCP) server** for Kruize HPO integration. It accepts inputs from an AI agent detecting JVM latency issues, simulates optimization trials, and returns the best JVM options.

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/bharathappali/dummy-kruize-mcp.git
cd dummy-kruize-mcp
```

### 2. (Optional) Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Run the Server

```bash
python -m uvicorn main:app
```

The server will be available at: http://localhost:8000

## 🧪 Test /mcp Endpoint

Send a `POST` request to `/mcp`:

**Request Content:**

```json
{
  "namespace": "java-ns",
  "deployment": "latency-app",
  "container": "java-container",
  "env_vars": {
    "JAVA_OPTIONS": "-Xmx2g -Xms1g"
  },
  "source_info": {
    "repo": "https://github.com/demo-org/latency-app",
    "image": "ghcr.io/demo-org/latency-app:latest"
  },
  "observed_issue": "latency_increase",
  "metrics_snapshot": {
    "latency_p95": "1300ms",
    "throughput_rps": 250,
    "cpu": "800m"
  }
}
```

**Sample Response:**

```json
{
    "experiment_id": "java-ns_latency-app_78eb1e",
    "workload": {
        "namespace": "java-ns",
        "deployment": "latency-app",
        "container": "java-container",
        "original_env": {
            "JAVA_OPTIONS": "-Xmx2g -Xms1g"
        },
        "observed_issue": "latency_increase",
        "source_repo": "https://github.com/demo-org/latency-app",
        "image": "ghcr.io/demo-org/latency-app:latest"
    },
    "hpo_experiment_config": {
        "experiment_name": "java-ns_latency-app_78eb1e",
        "experiment_id": "java-ns_latency-app_78eb1e",
        "total_trials": 5,
        "parallel_trials": 1,
        "objective_function": "1000 * (Throughput **1) / (Avg_Watts **2)",
        "value_type": "float",
        "hpo_algo_impl": "optuna_tpe",
        "direction": "maximize",
        "function_variables": [
            {
                "name": "Throughput",
                "value_type": "float"
            },
            {
                "name": "Avg_Watts",
                "value_type": "float"
            }
        ],
        "tunables": [
            {
                "name": "CompileThreshold",
                "value_type": "integer",
                "lower_bound": 1000,
                "upper_bound": 10000,
                "step": 100
            },
            {
                "name": "gc",
                "value_type": "categorical",
                "choices": [
                    "G1GC",
                    "ParallelGC",
                    "ZGC"
                ]
            },
            {
                "name": "TieredCompilation",
                "value_type": "categorical",
                "choices": [
                    "true",
                    "false"
                ]
            },
            {
                "name": "MinHeapFreeRatio",
                "value_type": "integer",
                "lower_bound": 5,
                "upper_bound": 70,
                "step": 5
            }
        ]
    },
    "final_best_score": 1582.89,
    "best_config": {
        "CompileThreshold": 9700,
        "gc": "G1GC",
        "TieredCompilation": "false",
        "MinHeapFreeRatio": 5
    },
    "agent_patch_action": {
        "update_env_var": {
            "JAVA_OPTIONS": "-XX:CompileThreshold=9700 -XX:gc=G1GC -XX:TieredCompilation=false -XX:MinHeapFreeRatio=5"
        },
        "yaml_patch_hint": "Update the container spec's env section with new JAVA_OPTIONS"
    },
    "trials": [
        {
            "trial": 1,
            "config": {
                "CompileThreshold": 8400,
                "gc": "ParallelGC",
                "TieredCompilation": "false",
                "MinHeapFreeRatio": 15
            },
            "score": 568.36,
            "metrics": {
                "Throughput": 145.42462249501614,
                "Avg_Watts": 15.995844719374555
            }
        },
        {
            "trial": 2,
            "config": {
                "CompileThreshold": 4700,
                "gc": "ParallelGC",
                "TieredCompilation": "true",
                "MinHeapFreeRatio": 45
            },
            "score": 121.56,
            "metrics": {
                "Throughput": 661.7937824780519,
                "Avg_Watts": 73.78399415810604
            }
        },
        {
            "trial": 3,
            "config": {
                "CompileThreshold": 9700,
                "gc": "G1GC",
                "TieredCompilation": "false",
                "MinHeapFreeRatio": 5
            },
            "score": 1582.89,
            "metrics": {
                "Throughput": 381.631703394046,
                "Avg_Watts": 15.527324697877802
            }
        },
        {
            "trial": 4,
            "config": {
                "CompileThreshold": 8800,
                "gc": "G1GC",
                "TieredCompilation": "false",
                "MinHeapFreeRatio": 60
            },
            "score": 298.3,
            "metrics": {
                "Throughput": 453.6033580380009,
                "Avg_Watts": 38.99512569761835
            }
        },
        {
            "trial": 5,
            "config": {
                "CompileThreshold": 8500,
                "gc": "ParallelGC",
                "TieredCompilation": "true",
                "MinHeapFreeRatio": 60
            },
            "score": 39.16,
            "metrics": {
                "Throughput": 261.7385162605008,
                "Avg_Watts": 81.75280327012476
            }
        }
    ],
    "explanation": "Recommended configuration improves throughput while reducing power consumption, optimizing the given objective function."
}
```












