from __future__ import annotations

from typing import Any

from backend.benchmark_engine.distributions import benchmark_for_workflow
from backend.diagnostics_engine.pipeline import run_evaluation
from backend.evaluations.replay_store import write_replay
from backend.registries.loader import registry_items
from backend.report_generation.reports import generate_report
from backend.schemas.models import EvaluationRequest
from backend.synthetic_data.generators import (
    fairness_sensitive_samples,
    noisy_ocr_documents,
    support_policy_reference,
    support_safety_records,
    synthetic_fraud_attacks,
    synthetic_repayment_drift,
)


def list_workflows() -> list[dict[str, Any]]:
    return registry_items("workflow_registry.json", "workflows")


def get_workflow(workflow_id: str) -> dict[str, Any]:
    for workflow in list_workflows():
        if workflow["id"] == workflow_id:
            return workflow
    raise KeyError(f"Unknown workflow: {workflow_id}")


def demo_payload_for(workflow_id: str) -> dict[str, Any]:
    if workflow_id == "fraud_adversarial_testing":
        rows = synthetic_fraud_attacks()
        return {"records": rows, "predictions": [row["prediction"] for row in rows]}
    if workflow_id in {"credit_bias_mitigation", "loan_approval_counterfactual_fairness"}:
        records, decisions = fairness_sensitive_samples()
        return {"records": records, "decisions": decisions}
    if workflow_id == "support_llm_harmful_output":
        return {"records": support_safety_records(), **support_policy_reference()}
    if workflow_id == "default_residual_drift":
        predictions, actuals, records = synthetic_repayment_drift()
        return {"records": records, "predictions": predictions, "actuals": actuals}
    if workflow_id == "kyc_outlier_diagnostics":
        return {"records": noisy_ocr_documents()}
    raise KeyError(f"No demo payload registered for workflow: {workflow_id}")


def run_workflow(workflow_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    workflow = get_workflow(workflow_id)
    final_payload = payload or demo_payload_for(workflow_id)
    request = EvaluationRequest(
        ai_system=workflow["ai_system"],
        pillar=workflow["pillar"],
        practice=workflow["supporting_practice"],
        use_case=workflow["use_case"],
        payload=final_payload,
        run_strong_test=True,
    )
    evaluation = run_evaluation(request)
    benchmark = benchmark_for_workflow(workflow_id, evaluation.aggregate_score)
    report = generate_report(evaluation, company_name="Demo Lendingtech Startup")
    replay = write_replay(
        workflow_id,
        {
            "workflow": workflow,
            "inputs": final_payload,
            "perturbations": workflow["orchestration_logic"],
            "evaluator_decisions": [output.insight for output in evaluation.outputs],
            "scores": evaluation,
            "recommendations": report.recommended_next_steps,
            "benchmark_outputs": benchmark,
            "report": report,
        },
    )
    return {
        "workflow": workflow,
        "evaluation": evaluation,
        "benchmark": benchmark,
        "report": report,
        "replay": replay,
    }
