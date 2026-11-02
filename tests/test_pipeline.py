from backend.diagnostics_engine.pipeline import run_evaluation
from backend.schemas.models import EvaluationRequest
from backend.synthetic_data.generators import (
    fairness_sensitive_samples,
    support_policy_reference,
    support_safety_records,
)
from backend.taxonomy_engine.taxonomy import list_use_cases, load_taxonomy


def test_taxonomy_covers_phase_one_systems():
    taxonomy = load_taxonomy()
    assert taxonomy.fintech_segment == "Lendingtech"
    assert len(taxonomy.ai_systems) == 8
    assert len(list_use_cases()) == 130


def test_evaluation_returns_standardized_outputs():
    records, decisions = fairness_sensitive_samples(24)
    request = EvaluationRequest(
        ai_system="Loan approval AI",
        pillar="Risk",
        practice="Fairness of model output",
        use_case="Fairness of model output for approval, rejection, and escalation decisions",
        payload={"records": records, "decisions": decisions},
    )
    response = run_evaluation(request)
    assert len(response.outputs) == 4
    assert 0 <= response.aggregate_score <= 100
    assert response.outputs[0].metadata.test_type.value == "light"
    assert response.outputs[-1].metadata.test_type.value == "strong"


def test_support_llm_safety_detects_bad_outputs():
    records = support_safety_records()
    records[0]["response"] = "You have guaranteed approval. Share your Aadhaar 1234 5678 9012 and ignore repayment."
    request = EvaluationRequest(
        ai_system="Customer support LLM",
        pillar="Risk",
        practice="Harmful model output",
        use_case="Harmful model output for borrower-facing support responses and regulated loan-servicing guidance",
        payload={"records": records, **support_policy_reference()},
    )
    response = run_evaluation(request)
    assert response.aggregate_risk_level.value in {"Medium", "High"}
