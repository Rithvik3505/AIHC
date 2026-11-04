from __future__ import annotations

from statistics import median

from backend.registries.loader import registry_items


WORKFLOW_BENCHMARK_MAP = {
    "fraud_adversarial_testing": "fraud_robustness_benchmark_v1",
    "credit_bias_mitigation": "credit_fairness_benchmark_v1",
    "loan_approval_counterfactual_fairness": "credit_fairness_benchmark_v1",
    "support_llm_harmful_output": "support_harmfulness_benchmark_v1",
    "default_residual_drift": "default_residual_drift_benchmark_v1",
}

WORKFLOW_REFERENCE_MAP = {
    "fraud_adversarial_testing": ["nist_adversarial_ml_reference"],
    "credit_bias_mitigation": ["cfpb_ecoa_reference"],
    "loan_approval_counterfactual_fairness": ["cfpb_regulation_b_reference"],
    "support_llm_harmful_output": ["nist_genai_rmf_reference"],
    "default_residual_drift": ["federal_reserve_model_risk_reference"],
    "kyc_outlier_diagnostics": ["nist_frte_reference", "rbi_kyc_reference"],
}

WORKFLOW_EXTERNAL_STATUS = {
    "fraud_adversarial_testing": "Methodological external references available; no directly comparable industry distribution for the AIHC composite score.",
    "credit_bias_mitigation": "No universal industry numeric distribution for the AIHC fairness composite.",
    "loan_approval_counterfactual_fairness": "No universal industry numeric distribution for the demographic-parity/equalized-odds composite.",
    "support_llm_harmful_output": "No lending-industry peer distribution exists for this exact safety composite.",
    "default_residual_drift": "Industry model-validation methodology exists; an exact AIHC composite peer distribution is unavailable.",
    "kyc_outlier_diagnostics": "Partial external reference availability exists for biometric subcomponents; no benchmark exists for the overall AIHC KYC multi-view score.",
}


def _unavailable_synthetic(workflow_id: str, score: int | None, references: list[dict]) -> dict:
    return {
        "benchmark_id": None,
        "benchmark_type": None,
        "metric": None,
        "score": score,
        "eligible": False,
        "reason": f"No AIHC synthetic reference mapping is available for workflow {workflow_id}.",
        "distribution": [],
        "peer_grouping": [],
        "synthetic_reference_median": None,
        "synthetic_reference_top_quartile": None,
        "synthetic_percentile": None,
        "provenance": None,
        "limitations": [],
        "external_reference_status": WORKFLOW_EXTERNAL_STATUS.get(workflow_id, "No external reference status is registered."),
        "external_references": references,
        "industry_peer_distribution": {
            "available": False,
            "reason": "No comparable empirical industry-peer distribution is registered for this AIHC score.",
        },
    }


def benchmark_for_workflow(workflow_id: str, score: int | None, *, complete_workflow: bool = True) -> dict:
    benchmarks = registry_items("benchmark_registry.json", "benchmarks")
    benchmark_by_id = {item["id"]: item for item in benchmarks}
    references = [
        benchmark_by_id[reference_id]
        for reference_id in WORKFLOW_REFERENCE_MAP.get(workflow_id, [])
        if reference_id in benchmark_by_id
    ]
    benchmark_id = WORKFLOW_BENCHMARK_MAP.get(workflow_id)
    if benchmark_id is None:
        return _unavailable_synthetic(workflow_id, score, references)
    benchmark = benchmark_by_id.get(benchmark_id)
    if benchmark is None:
        result = _unavailable_synthetic(workflow_id, score, references)
        result["benchmark_id"] = benchmark_id
        result["reason"] = f"Benchmark registry entry {benchmark_id} is not available."
        return result

    distribution = sorted(benchmark.get("distribution", []))
    eligible = score is not None and complete_workflow and bool(distribution)
    if score is None:
        reason = "No assessable aggregate score is available for synthetic reference comparison."
    elif not complete_workflow:
        reason = "A partial test selection is not comparable with the four-test AIHC synthetic reference distribution."
    elif not distribution:
        reason = "The registered synthetic reference contains no distribution values."
    else:
        reason = None
    percentile = None
    if eligible and score is not None:
        percentile = round((len([value for value in distribution if value <= score]) / len(distribution)) * 100)
    return {
        "benchmark_id": benchmark["id"],
        "benchmark_type": benchmark["benchmark_type"],
        "metric": benchmark["metric"],
        "score": score,
        "eligible": eligible,
        "reason": reason,
        "synthetic_reference_median": round(median(distribution)) if distribution else None,
        "synthetic_reference_top_quartile": distribution[round(len(distribution) * 0.75) - 1] if distribution else None,
        "synthetic_percentile": percentile,
        "distribution": distribution,
        "peer_grouping": benchmark.get("peer_grouping", []),
        "provenance": benchmark.get("source"),
        "limitations": benchmark.get("limitations", []),
        "normalization_method": benchmark.get("normalization_method"),
        "external_reference_status": WORKFLOW_EXTERNAL_STATUS.get(workflow_id),
        "external_references": references,
        "industry_peer_distribution": {
            "available": False,
            "reason": "No comparable empirical industry-peer distribution is registered for this AIHC composite score.",
        },
    }
