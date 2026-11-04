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
from backend.workflows.evidence import validate_workflow_evidence


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


def run_workflow(
    workflow_id: str,
    payload: dict[str, Any] | None = None,
    *,
    evidence_mode: str | None = None,
    selected_test_ids: list[str] | None = None,
) -> dict[str, Any]:
    workflow = get_workflow(workflow_id)
    effective_mode = evidence_mode or ("demo" if payload is None else "manual")
    if effective_mode not in {"demo", "manual", "upload"}:
        raise ValueError(f"Unsupported evidence mode: {effective_mode}")
    final_payload = demo_payload_for(workflow_id) if effective_mode == "demo" and payload is None else (payload or {})
    validation = validate_workflow_evidence(workflow_id, final_payload, selected_test_ids)
    if not validation["can_run"]:
        messages = "; ".join(issue["message"] for issue in validation["issues"] if issue["fatal"])
        raise ValueError(messages or "Evidence cannot be evaluated.")
    final_payload = validation["normalized_payload"]
    request = EvaluationRequest(
        ai_system=workflow["ai_system"],
        pillar=workflow["pillar"],
        practice=workflow["supporting_practice"],
        use_case=workflow["use_case"],
        payload=final_payload,
        run_strong_test=True,
        selected_test_ids=selected_test_ids or [],
    )
    evaluation = run_evaluation(request)
    complete_workflow = evaluation.coverage.selected_test_count == 4
    benchmark = benchmark_for_workflow(workflow_id, evaluation.aggregate_score, complete_workflow=complete_workflow)
    report = generate_report(
        evaluation,
        company_name="Demo Lendingtech Startup" if effective_mode == "demo" else "Lendingtech User Evidence",
        assurance_scope=(
            "Synthetic demo evidence and deterministic MVP evaluators; not a certification."
            if effective_mode == "demo"
            else "User-provided evidence processed ephemerally by deterministic MVP evaluators; not a certification."
        ),
    )
    if effective_mode == "demo":
        replay = {
            **write_replay(
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
            ),
            "persisted": True,
            "reason": "Deterministic demo evidence is replayable.",
        }
    else:
        replay = {
            "replay_id": None,
            "path": None,
            "persisted": False,
            "reason": "Replay persistence is disabled for manual and uploaded evidence to avoid storing raw customer data.",
        }
    return {
        "workflow": workflow,
        "evidence_mode": effective_mode,
        "validation": validation,
        "evaluation": evaluation,
        "benchmark": benchmark,
        "report": report,
        "replay": replay,
    }
