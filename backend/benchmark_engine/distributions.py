from __future__ import annotations

from statistics import median

from backend.registries.loader import registry_items


WORKFLOW_BENCHMARK_MAP = {
    "fraud_adversarial_testing": "fraud_robustness_benchmark_v1",
    "credit_bias_mitigation": "credit_fairness_benchmark_v1",
    "loan_approval_counterfactual_fairness": "credit_fairness_benchmark_v1",
    "support_llm_harmful_output": "support_harmfulness_benchmark_v1",
    "default_residual_drift": "default_residual_drift_benchmark_v1",
    "kyc_outlier_diagnostics": "fraud_robustness_benchmark_v1",
}


def benchmark_for_workflow(workflow_id: str, score: int) -> dict:
    benchmark_id = WORKFLOW_BENCHMARK_MAP.get(workflow_id)
    benchmarks = registry_items("benchmark_registry.json", "benchmarks")
    benchmark = next((item for item in benchmarks if item["id"] == benchmark_id), benchmarks[0])
    distribution = sorted(benchmark["synthetic_benchmark_distribution"])
    below_or_equal = len([value for value in distribution if value <= score])
    percentile = round((below_or_equal / len(distribution)) * 100)
    return {
        "benchmark_id": benchmark["id"],
        "metric": benchmark["benchmark_metric"],
        "score": score,
        "industry_median": round(median(distribution)),
        "top_quartile": distribution[round(len(distribution) * 0.75) - 1],
        "percentile": percentile,
        "distribution": distribution,
        "peer_grouping": benchmark["peer_grouping"],
    }
