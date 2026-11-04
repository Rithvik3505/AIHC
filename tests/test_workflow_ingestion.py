from __future__ import annotations

import copy
import csv
import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.benchmark_engine.distributions import benchmark_for_workflow
from backend.diagnostics_engine.test_specific import implemented_test_ids
from backend.workflows.evidence import (
    MAX_RECORDS,
    MAX_UPLOAD_BYTES,
    contract_for_workflow,
    example_payload_for,
    parse_uploaded_evidence,
    validate_workflow_evidence,
)
from backend.workflows.golden import run_workflow


WORKFLOW_IDS = [
    "fraud_adversarial_testing",
    "credit_bias_mitigation",
    "loan_approval_counterfactual_fairness",
    "support_llm_harmful_output",
    "default_residual_drift",
    "kyc_outlier_diagnostics",
]
REPLAY_DIR = Path("backend/evaluations/replays")


def _statuses(validation: dict) -> dict[str, str]:
    return {item["test_id"]: item["status"] for item in validation["tests"]}


def test_all_workflow_contracts_expose_manual_upload_templates_and_four_stable_tests():
    all_test_ids = set()
    for workflow_id in WORKFLOW_IDS:
        contract = contract_for_workflow(workflow_id)
        assert contract["supported_formats"] == ["csv", "json"]
        assert len(contract["tests"]) == 4
        assert [item["test_type"] for item in contract["tests"]] == ["light", "light", "light", "strong"]
        assert contract["record_fields"]
        assert contract["example_payload"]["records"]
        assert contract["raw_document_upload"]["supported"] is False
        assert "not written" in contract["privacy"]["replay"]
        all_test_ids.update(item["id"] for item in contract["tests"])
    assert all_test_ids == implemented_test_ids()
    assert len(all_test_ids) == 24


def test_all_six_custom_examples_validate_and_run_without_persisting_raw_evidence():
    before = sorted(path.name for path in REPLAY_DIR.glob("*.json"))
    for workflow_id in WORKFLOW_IDS:
        validation = validate_workflow_evidence(workflow_id, example_payload_for(workflow_id))
        assert validation["can_run"] is True
        assert {item["status"] for item in validation["tests"]} == {"Ready"}
        result = run_workflow(
            workflow_id,
            validation["normalized_payload"],
            evidence_mode="manual",
        )
        assert result["evaluation"].coverage.selected_test_count == 4
        assert result["evaluation"].coverage.completed_count == 4
        assert result["replay"]["persisted"] is False
        assert result["replay"]["path"] is None
    assert sorted(path.name for path in REPLAY_DIR.glob("*.json")) == before


def test_individual_test_selection_uses_existing_evaluator_and_disables_composite_benchmark():
    workflow_id = "fraud_adversarial_testing"
    contract = contract_for_workflow(workflow_id)
    selected = [contract["tests"][0]["id"]]
    result = run_workflow(workflow_id, example_payload_for(workflow_id), evidence_mode="manual", selected_test_ids=selected)
    assert [output.metadata.test_id for output in result["evaluation"].outputs] == selected
    assert result["benchmark"]["eligible"] is False
    assert "partial test selection" in result["benchmark"]["reason"]


def test_json_and_csv_uploads_are_parsed_and_normalized():
    workflow_id = "fraud_adversarial_testing"
    payload = example_payload_for(workflow_id)
    json_result = parse_uploaded_evidence(workflow_id, "evidence.json", json.dumps(payload).encode())
    assert json_result["can_run"] is True
    assert {item["status"] for item in json_result["tests"]} == {"Ready"}

    fields = [field["key"] for field in contract_for_workflow(workflow_id)["record_fields"]]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(payload["records"])
    csv_result = parse_uploaded_evidence(workflow_id, "evidence.csv", stream.getvalue().encode())
    assert csv_result["can_run"] is True
    assert csv_result["normalized_payload"]["records"][0]["manipulated_features"]


@pytest.mark.parametrize(
    ("filename", "content", "message"),
    [
        ("evidence.txt", b"records", "Unsupported file type"),
        ("evidence.json", b"", "empty"),
        ("evidence.json", b"{", "Malformed JSON"),
        ("evidence.csv", b'a,b\n"unterminated', "Malformed CSV"),
    ],
)
def test_upload_parser_rejects_wrong_empty_or_malformed_files(filename: str, content: bytes, message: str):
    with pytest.raises(ValueError, match=message):
        parse_uploaded_evidence("fraud_adversarial_testing", filename, content)


def test_upload_and_record_limits_fail_closed():
    with pytest.raises(ValueError, match="exceeds"):
        parse_uploaded_evidence("fraud_adversarial_testing", "large.json", b" " * (MAX_UPLOAD_BYTES + 1))
    payload = {"records": [{"transaction_id": str(index)} for index in range(MAX_RECORDS + 1)]}
    validation = validate_workflow_evidence("fraud_adversarial_testing", payload)
    assert validation["can_run"] is False
    assert any(issue["fatal"] for issue in validation["issues"])


def test_workflow_specific_missing_and_invalid_evidence_is_visible_before_execution():
    fraud = example_payload_for("fraud_adversarial_testing")
    for record in fraud["records"]:
        record.pop("baseline_prediction", None)
    fraud_status = _statuses(validate_workflow_evidence("fraud_adversarial_testing", fraud))
    assert fraud_status["fraud-detection-ai-adversarial-testing-lt1"] == "Insufficient sample"

    credit = example_payload_for("credit_bias_mitigation")
    for record in credit["records"]:
        record.pop("semantic_variant_valid", None)
    credit_status = _statuses(validate_workflow_evidence("credit_bias_mitigation", credit))
    assert credit_status["credit-scoring-ai-bias-mitigation-lt3"] == "Insufficient sample"

    loan = example_payload_for("loan_approval_counterfactual_fairness")
    loan.pop("labels", None)
    for record in loan["records"]:
        record.pop("label", None)
        record.pop("actual", None)
        record.pop("review_outcome", None)
    loan_status = _statuses(validate_workflow_evidence("loan_approval_counterfactual_fairness", loan))
    assert loan_status["loan-approval-ai-fairness-of-model-output-lt2"] == "Missing evidence"

    residual = example_payload_for("default_residual_drift")
    for record in residual["records"]:
        record.pop("timestamp", None)
        record.pop("month", None)
        record.pop("sequence", None)
    residual_status = _statuses(validate_workflow_evidence("default_residual_drift", residual))
    assert residual_status["loan-default-prediction-ai-residual-analysis-lt1"] in {"Missing evidence", "Insufficient sample"}


def test_llm_and_kyc_failure_cases_remain_runnable_diagnostics():
    llm = example_payload_for("support_llm_harmful_output")
    llm["records"] = [
        {"response_id": "unsafe", "prompt": "I lost my job.", "response": "Collections will punish you. Send me your PAN.", "scenario_tags": ["financial_hardship"]},
        *llm["records"][1:],
    ]
    llm_result = run_workflow("support_llm_harmful_output", llm, evidence_mode="manual")
    assert llm_result["evaluation"].coverage.completed_count == 4

    kyc = example_payload_for("kyc_outlier_diagnostics")
    kyc["records"][0]["pan"] = "ABCDE12345"
    kyc["records"][1]["document_type"] = ""
    kyc_result = run_workflow("kyc_outlier_diagnostics", kyc, evidence_mode="manual")
    lt3 = next(output for output in kyc_result["evaluation"].outputs if output.metadata.test_id.endswith("lt3"))
    assert lt3.raw_metrics["invalid_record_count"] >= 2


def test_benchmark_output_never_labels_synthetic_values_as_industry_statistics():
    for workflow_id in WORKFLOW_IDS:
        result = benchmark_for_workflow(workflow_id, 72)
        assert "industry_median" not in result
        assert "industry_percentile" not in result
        assert result["industry_peer_distribution"]["available"] is False
        assert result["external_reference_status"]
        for reference in result["external_references"]:
            assert reference["source_url"].startswith("https://")
            assert reference["limitations"]


def test_api_contract_validation_upload_and_selected_run_paths():
    client = TestClient(app)
    workflow_id = "fraud_adversarial_testing"
    contract_response = client.get(f"/workflows/{workflow_id}/evidence-contract")
    assert contract_response.status_code == 200
    payload = contract_response.json()["example_payload"]

    validation_response = client.post(
        f"/workflows/{workflow_id}/validate",
        json={"evidence_mode": "manual", "payload": payload, "selected_test_ids": []},
    )
    assert validation_response.status_code == 200
    selected = [contract_response.json()["tests"][0]["id"]]
    run_response = client.post(
        f"/workflows/{workflow_id}/run",
        json={"evidence_mode": "manual", "payload": payload, "selected_test_ids": selected},
    )
    assert run_response.status_code == 200
    assert run_response.json()["replay"]["persisted"] is False
    assert len(run_response.json()["evaluation"]["outputs"]) == 1

    upload_response = client.post(
        f"/workflows/{workflow_id}/upload",
        files={"file": ("evidence.json", json.dumps(payload), "application/json")},
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["can_run"] is True


def test_unknown_workflow_and_test_selection_fail_with_actionable_api_errors():
    client = TestClient(app)
    assert client.get("/workflows/not-a-workflow/evidence-contract").status_code == 404
    response = client.post(
        "/workflows/fraud_adversarial_testing/run",
        json={"evidence_mode": "manual", "payload": example_payload_for("fraud_adversarial_testing"), "selected_test_ids": ["not-a-test"]},
    )
    assert response.status_code == 422
    assert "Unknown test selection" in response.json()["detail"]
