from __future__ import annotations

import csv
import io
import json
import math
from copy import deepcopy
from typing import Any

from backend.diagnostics_engine.test_specific import evaluate_test, evaluator_config_for
from backend.registries.loader import registry_items
from backend.schemas.models import EvidenceStatus, ExecutionStatus
from backend.synthetic_data.generators import (
    fairness_sensitive_samples,
    noisy_ocr_documents,
    support_policy_reference,
    support_safety_records,
    synthetic_fraud_attacks,
    synthetic_repayment_drift,
)
from backend.taxonomy_engine.taxonomy import find_use_case


MAX_UPLOAD_BYTES = 1_000_000
MAX_RECORDS = 500
MAX_TEXT_LENGTH = 10_000


def _field(
    key: str,
    label: str,
    kind: str,
    description: str,
    *,
    required_for: list[str] | None = None,
    options: list[str] | None = None,
    minimum: float | None = None,
    maximum: float | None = None,
) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "type": kind,
        "description": description,
        "required_for": required_for or [],
        "options": options or [],
        "minimum": minimum,
        "maximum": maximum,
    }


WORKFLOW_FIELDS: dict[str, list[dict[str, Any]]] = {
    "fraud_adversarial_testing": [
        _field("transaction_id", "Transaction ID", "text", "Stable synthetic or customer record identifier.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("baseline_prediction", "Baseline prediction", "number", "Fraud score before the attack.", required_for=["LT1", "LT2", "LT3", "ST1"], minimum=0, maximum=1),
        _field("prediction", "Attacked prediction", "number", "Fraud score after the attack.", required_for=["LT1", "LT2", "LT3", "ST1"], minimum=0, maximum=1),
        _field("decision_threshold", "Decision threshold", "number", "One threshold used for baseline and attacked decisions.", required_for=["LT1", "LT2", "LT3", "ST1"], minimum=0, maximum=1),
        _field("fraud_label", "Fraud label", "binary", "Optional reliable binary ground truth for FNR metrics.", required_for=["LT2"]),
        _field("attack_type", "Attack type", "text", "Attack family used for pattern coverage.", required_for=["LT2", "ST1"]),
        _field("manipulated_features", "Manipulated features", "list", "Feature names separated by semicolons in CSV.", required_for=["LT3", "ST1"]),
        _field("perturbation_magnitude", "Perturbation magnitude", "number", "Non-negative observed attack magnitude.", required_for=["LT3", "ST1"], minimum=0),
        _field("attack_budget", "Attack budget", "number", "Non-negative allowed perturbation budget.", required_for=["LT3", "ST1"], minimum=0),
        _field("attack_stage", "Attack stage", "text", "Single or coordinated attack stage.", required_for=["ST1"]),
        _field("constraint_violation", "Constraint violation", "boolean", "Marks an attack as invalid for robustness scoring."),
        _field("amount", "Amount", "number", "Optional transaction context."),
        _field("hour", "Hour", "number", "Optional transaction hour."),
        _field("merchant_category", "Merchant category", "text", "Optional merchant context."),
        _field("device_age_days", "Device age (days)", "number", "Optional device context."),
    ],
    "credit_bias_mitigation": [
        _field("record_id", "Record ID", "text", "Stable applicant record identifier.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("prediction_score", "Prediction score", "number", "Baseline credit score.", required_for=["LT1", "LT3"], minimum=0, maximum=1),
        _field("decision", "Decision", "binary", "Binary baseline decision.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("decision_threshold", "Decision threshold", "number", "Threshold shared by baseline and variants.", required_for=["LT1"], minimum=0, maximum=1),
        _field("counterfactual_score", "Counterfactual score", "number", "Score after protected-attribute substitution.", required_for=["LT1"], minimum=0, maximum=1),
        _field("counterfactual_decision", "Counterfactual decision", "binary", "Recorded counterfactual decision.", required_for=["LT1"]),
        _field("semantic_variant_valid", "Semantic variant valid", "boolean", "Explicit confirmation that the language variant is equivalent.", required_for=["LT3"]),
        _field("language_variant_score", "Language variant score", "number", "Score for the validated semantic variant.", required_for=["LT3"], minimum=0, maximum=1),
        _field("language_variant_decision", "Language variant decision", "binary", "Decision for the validated semantic variant.", required_for=["LT3"]),
        _field("gender", "Gender", "text", "Default protected attribute.", required_for=["LT1", "LT2"]),
        _field("geography", "Geography", "text", "Potential proxy category.", required_for=["LT2"]),
        _field("employment_type", "Employment type", "text", "Potential proxy category.", required_for=["LT2"]),
        _field("education", "Education", "text", "Potential proxy category.", required_for=["LT2"]),
        _field("device", "Device", "text", "Potential proxy category.", required_for=["LT2"]),
        _field("language", "Language", "text", "Potential proxy category.", required_for=["LT2", "LT3"]),
        _field("segment", "Segment", "text", "Applicant segment or comparison group.", required_for=["LT2"]),
        _field("proxy_variant_field", "Proxy variant field", "text", "Field changed for controlled sensitivity."),
        _field("proxy_variant_score", "Proxy variant score", "number", "Score after controlled proxy change.", minimum=0, maximum=1),
    ],
    "loan_approval_counterfactual_fairness": [
        _field("record_id", "Applicant ID", "text", "Stable applicant identifier.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("decision", "Decision", "binary", "Binary approval decision.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("label", "Reviewed outcome", "binary", "Ground truth or reviewed outcome.", required_for=["LT2"]),
        _field("gender", "Gender", "text", "Protected cohort used by error-rate analysis.", required_for=["LT1", "LT2"]),
        _field("segment", "Segment", "text", "Applicant segment used for within-attribute parity."),
        _field("geography", "Geography", "text", "Geographic cohort used for within-attribute parity."),
        _field("matched_pair_id", "Matched pair ID", "text", "Optional explicit comparable-applicant pair.", required_for=["LT3"]),
        _field("monthly_income", "Monthly income", "number", "Numeric matching feature.", required_for=["LT3"]),
        _field("debt_to_income", "Debt-to-income", "number", "Numeric matching feature.", required_for=["LT3"]),
        _field("credit_history_months", "Credit history months", "number", "Numeric matching feature.", required_for=["LT3"]),
        _field("risk_score", "Risk score", "number", "Compatible decision/risk score.", required_for=["LT3"]),
    ],
    "support_llm_harmful_output": [
        _field("response_id", "Response ID", "text", "Stable response identifier.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("prompt", "Prompt / scenario", "textarea", "Borrower prompt or scenario context.", required_for=["LT2", "LT3"]),
        _field("response", "Assistant response", "textarea", "Response being evaluated.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("scenario_tags", "Scenario tags", "list", "Tags such as financial_hardship or pii_safety.", required_for=["LT3"]),
    ],
    "default_residual_drift": [
        _field("record_id", "Record ID", "text", "Stable observation identifier.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("timestamp", "Timestamp", "text", "ISO timestamp; month or sequence may be used instead.", required_for=["LT1"]),
        _field("month", "Month", "number", "Numeric temporal order when timestamp is absent.", required_for=["LT1"]),
        _field("sequence", "Sequence", "number", "Numeric order when timestamp/month is absent.", required_for=["LT1"]),
        _field("prediction", "Prediction", "number", "Model prediction aligned to the actual value.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("actual", "Actual", "number", "Observed outcome aligned to prediction.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("segment", "Segment", "text", "Cohort used for residual concentration.", required_for=["LT3"]),
    ],
    "kyc_outlier_diagnostics": [
        _field("applicant_id", "Applicant ID", "text", "Stable applicant identifier for cross-detector overlap.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("document_id", "Document ID", "text", "Stable document identifier."),
        _field("document_type", "Document type", "select", "Supported type for deterministic field constraints.", required_for=["LT3"], options=["pan", "passport", "aadhaar", "bank_statement"]),
        _field("name", "Name", "text", "Synthetic or customer-provided identity name.", required_for=["LT3"]),
        _field("pan", "PAN", "text", "PAN structure: five letters, four digits, one letter.", required_for=["LT3"]),
        _field("income", "Income", "number", "Required for bank_statement records."),
        _field("confidence_score", "Confidence score", "number", "Document confidence/quality value.", required_for=["LT1", "LT2", "LT3", "ST1"]),
        _field("blur_score", "Blur score", "number", "Continuous image-quality value.", required_for=["LT1", "LT2"]),
        _field("face_match_score", "Face match score", "number", "Optional biometric match quality."),
        _field("document_authenticity_score", "Document authenticity", "number", "Optional authenticity quality score."),
        _field("liveness_score", "Liveness score", "number", "Optional biometric liveness quality."),
        _field("ocr_quality_score", "OCR quality score", "number", "Optional OCR quality value."),
    ],
}


TOP_LEVEL_FIELDS: dict[str, list[dict[str, Any]]] = {
    "fraud_adversarial_testing": [
        _field("allowed_perturbation_budget", "Default attack budget", "number", "Fallback budget when a record has no attack_budget.", minimum=0),
    ],
    "credit_bias_mitigation": [
        _field("protected_attribute", "Protected attribute", "select", "Protected field for proxy association.", options=["gender", "geography", "segment"]),
        _field("decision_threshold", "Default decision threshold", "number", "Fallback threshold for all paired comparisons.", minimum=0, maximum=1),
    ],
    "support_llm_harmful_output": [
        _field("policy_rules", "Policy rules", "json", "JSON array of deterministic prohibited-pattern rules.", required_for=["LT2"]),
        _field("reference_facts", "Reference facts", "json", "JSON array of deterministic contradiction-pattern facts.", required_for=["LT2"]),
    ],
}


def _workflow(workflow_id: str) -> dict[str, Any]:
    workflow = next((item for item in registry_items("workflow_registry.json", "workflows") if item["id"] == workflow_id), None)
    if workflow is None:
        raise KeyError(f"Unknown workflow: {workflow_id}")
    return workflow


def workflow_tests(workflow_id: str) -> list[dict[str, Any]]:
    workflow = _workflow(workflow_id)
    _, _, _, use_case = find_use_case(
        workflow["ai_system"], workflow["pillar"], workflow["supporting_practice"], workflow["use_case"]
    )
    return list(use_case["tests"])


def example_payload_for(workflow_id: str) -> dict[str, Any]:
    if workflow_id == "fraud_adversarial_testing":
        return {"records": synthetic_fraud_attacks(12)}
    if workflow_id in {"credit_bias_mitigation", "loan_approval_counterfactual_fairness"}:
        records, decisions = fairness_sensitive_samples(12)
        for record, decision in zip(records, decisions, strict=False):
            record["decision"] = decision
        return {"records": records, "decisions": decisions, "protected_attribute": "gender", "decision_threshold": 0.55}
    if workflow_id == "support_llm_harmful_output":
        return {"records": support_safety_records(), **support_policy_reference()}
    if workflow_id == "default_residual_drift":
        predictions, actuals, records = synthetic_repayment_drift(12)
        return {"records": records, "predictions": predictions, "actuals": actuals}
    if workflow_id == "kyc_outlier_diagnostics":
        return {"records": noisy_ocr_documents(12)}
    raise KeyError(f"No example payload for workflow: {workflow_id}")


def contract_for_workflow(workflow_id: str) -> dict[str, Any]:
    workflow = _workflow(workflow_id)
    tests = workflow_tests(workflow_id)
    return {
        "workflow_id": workflow_id,
        "workflow_name": workflow["name"],
        "supported_formats": workflow.get("supported_uploads", ["csv", "json"]),
        "record_fields": WORKFLOW_FIELDS[workflow_id],
        "top_level_fields": TOP_LEVEL_FIELDS.get(workflow_id, []),
        "tests": [
            {
                "id": test["id"],
                "name": test["name"],
                "test_type": test["test_type"],
                "purpose": test["objective"],
                "required_evidence": (evaluator_config_for(test["id"]).required_evidence if evaluator_config_for(test["id"]) else []),
            }
            for test in tests
        ],
        "example_payload": example_payload_for(workflow_id),
        "limits": {
            "maximum_file_bytes": MAX_UPLOAD_BYTES,
            "maximum_records": MAX_RECORDS,
            "maximum_prompt_or_response_characters": MAX_TEXT_LENGTH,
        },
        "privacy": {
            "processing": "Evidence is processed ephemerally for the current evaluation.",
            "replay": "Manual and uploaded evidence is not written to replay files.",
            "benchmark": "Raw evidence is never added to benchmark distributions.",
        },
        "raw_document_upload": {
            "supported": False,
            "status": "planned_not_operational",
            "reason": "No reliable PDF/image extraction or OCR implementation is present in the MVP.",
        },
    }


def _issue(message: str, *, field: str | None = None, row: int | None = None, severity: str = "error", fatal: bool = False) -> dict[str, Any]:
    return {"message": message, "field": field, "row": row, "severity": severity, "fatal": fatal}


def _number(value: Any) -> float | int | None:
    if isinstance(value, bool) or value in {None, ""}:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return int(number) if number.is_integer() else number


def _binary(value: Any) -> int | None:
    if isinstance(value, bool):
        return int(value)
    if value in {0, 1, "0", "1"}:
        return int(value)
    text = str(value).strip().lower()
    if text in {"true", "yes", "approve", "approved", "detected", "positive"}:
        return 1
    if text in {"false", "no", "reject", "rejected", "negative"}:
        return 0
    return None


def _boolean(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def _list_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value or "").strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass
    return [item.strip() for item in text.replace("|", ";").split(";") if item.strip()]


def normalize_workflow_evidence(workflow_id: str, payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    _workflow(workflow_id)
    issues: list[dict[str, Any]] = []
    normalized = deepcopy(payload) if isinstance(payload, dict) else {}
    if not isinstance(payload, dict):
        return {}, [_issue("Evidence payload must be a JSON object.", fatal=True)]
    records = payload.get("records")
    if not isinstance(records, list):
        return normalized, [_issue("Evidence must contain a records array.", field="records", fatal=True)]
    if not records:
        issues.append(_issue("Evidence contains no records.", field="records"))
    if len(records) > MAX_RECORDS:
        issues.append(_issue(f"Evidence exceeds the {MAX_RECORDS}-record limit.", field="records", fatal=True))

    specs = {item["key"]: item for item in WORKFLOW_FIELDS[workflow_id]}
    normalized_records: list[dict[str, Any]] = []
    for index, source in enumerate(records):
        if not isinstance(source, dict):
            issues.append(_issue("Record must be an object.", row=index + 1, fatal=True))
            continue
        record = dict(source)
        for key, spec in specs.items():
            if key not in record:
                continue
            value = record[key]
            kind = spec["type"]
            if kind == "number":
                converted = _number(value)
                if converted is None and value not in {None, ""}:
                    issues.append(_issue("Value must be a finite number.", field=key, row=index + 1))
                record[key] = converted
                if converted is not None and (spec["minimum"] is not None and converted < spec["minimum"] or spec["maximum"] is not None and converted > spec["maximum"]):
                    if workflow_id == "kyc_outlier_diagnostics":
                        issues.append(_issue("Value is outside the expected diagnostic range and will be evaluated as a constraint finding.", field=key, row=index + 1, severity="warning"))
                    else:
                        issues.append(_issue(f"Value must be between {spec['minimum']} and {spec['maximum']}.", field=key, row=index + 1))
                        record[key] = None
            elif kind == "binary":
                converted = _binary(value)
                if converted is None and value not in {None, ""}:
                    issues.append(_issue("Value must be valid binary evidence.", field=key, row=index + 1))
                record[key] = converted
            elif kind == "boolean":
                converted = _boolean(value)
                if converted is None and value not in {None, ""}:
                    issues.append(_issue("Value must be true or false.", field=key, row=index + 1))
                record[key] = converted
            elif kind == "list":
                record[key] = _list_value(value)
            elif kind in {"text", "textarea", "select"}:
                record[key] = str(value or "").strip()
                if kind == "textarea" and len(record[key]) > MAX_TEXT_LENGTH:
                    issues.append(_issue(f"Text exceeds the {MAX_TEXT_LENGTH}-character limit.", field=key, row=index + 1, fatal=True))
        normalized_records.append(record)
    normalized["records"] = normalized_records

    for spec in TOP_LEVEL_FIELDS.get(workflow_id, []):
        key = spec["key"]
        if key not in normalized:
            continue
        if spec["type"] == "number":
            converted = _number(normalized[key])
            if converted is None:
                issues.append(_issue("Value must be a finite number.", field=key))
            elif spec["minimum"] is not None and converted < spec["minimum"] or spec["maximum"] is not None and converted > spec["maximum"]:
                issues.append(_issue(f"Value must be between {spec['minimum']} and {spec['maximum']}.", field=key))
                converted = None
            normalized[key] = converted
        elif spec["type"] == "json" and not isinstance(normalized[key], list):
            issues.append(_issue("Reference value must be a JSON array.", field=key))
            normalized[key] = []

    if workflow_id == "credit_bias_mitigation":
        if not isinstance(normalized.get("decisions"), list) or len(normalized["decisions"]) != len(normalized_records):
            normalized["decisions"] = [record.get("decision") for record in normalized_records]
    elif workflow_id == "loan_approval_counterfactual_fairness":
        if not isinstance(normalized.get("decisions"), list) or len(normalized["decisions"]) != len(normalized_records):
            normalized["decisions"] = [record.get("decision") for record in normalized_records]
        if not isinstance(normalized.get("labels"), list) or len(normalized["labels"]) != len(normalized_records):
            normalized["labels"] = [record.get("label") for record in normalized_records]
    elif workflow_id == "default_residual_drift":
        normalized["predictions"] = [record.get("prediction") for record in normalized_records]
        normalized["actuals"] = [record.get("actual") for record in normalized_records]

    if workflow_id == "kyc_outlier_diagnostics":
        for index, record in enumerate(normalized_records):
            if not record.get("applicant_id") and not record.get("document_id"):
                issues.append(_issue("A stable applicant_id or document_id is required for cross-detector analysis.", field="applicant_id", row=index + 1))
            if not record.get("document_type"):
                issues.append(_issue("Missing document type will be reported separately by the field-constraint diagnostic.", field="document_type", row=index + 1, severity="warning"))
    return normalized, issues


def validate_workflow_evidence(
    workflow_id: str,
    payload: dict[str, Any],
    selected_test_ids: list[str] | None = None,
) -> dict[str, Any]:
    normalized, issues = normalize_workflow_evidence(workflow_id, payload)
    tests = workflow_tests(workflow_id)
    available_ids = {test["id"] for test in tests}
    selected = selected_test_ids or [test["id"] for test in tests]
    unknown = set(selected) - available_ids
    if unknown:
        issues.append(_issue(f"Unknown test selection: {', '.join(sorted(unknown))}", field="selected_test_ids", fatal=True))
    statuses = []
    for test in tests:
        if test["id"] not in selected:
            continue
        result = evaluate_test(test["id"], normalized)
        if result.execution_status == ExecutionStatus.completed:
            label = "Ready"
        elif result.evidence_status == EvidenceStatus.missing:
            label = "Missing evidence"
        elif result.evidence_status == EvidenceStatus.malformed:
            label = "Invalid evidence"
        elif result.evidence_status == EvidenceStatus.insufficient:
            label = "Insufficient sample"
        else:
            label = "Optional evidence unavailable"
        statuses.append(
            {
                "test_id": test["id"],
                "test_name": test["name"],
                "test_type": test["test_type"],
                "status": label,
                "evidence_status": result.evidence_status.value,
                "message": result.findings[0] if result.findings else "Evidence is assessable.",
                "required_evidence": evaluator_config_for(test["id"]).required_evidence if evaluator_config_for(test["id"]) else [],
            }
        )
    return {
        "workflow_id": workflow_id,
        "can_run": not any(issue["fatal"] for issue in issues),
        "normalized_payload": normalized,
        "issues": issues,
        "tests": statuses,
        "limits": contract_for_workflow(workflow_id)["limits"],
    }


def parse_uploaded_evidence(workflow_id: str, filename: str, content: bytes) -> dict[str, Any]:
    _workflow(workflow_id)
    if not content:
        raise ValueError("Uploaded file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError(f"Uploaded file exceeds the {MAX_UPLOAD_BYTES}-byte limit.")
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in {"csv", "json"}:
        raise ValueError("Unsupported file type. Upload a .csv or .json file.")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Uploaded evidence must be UTF-8 encoded.") from exc
    if suffix == "json":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON at line {exc.lineno}, column {exc.colno}.") from exc
        if isinstance(parsed, list):
            payload = {"records": parsed}
        elif isinstance(parsed, dict):
            payload = parsed
        else:
            raise ValueError("JSON evidence must be an object or an array of records.")
    else:
        try:
            reader = csv.DictReader(io.StringIO(text), strict=True)
            if not reader.fieldnames:
                raise ValueError("CSV evidence must include a header row.")
            rows = list(reader)
        except csv.Error as exc:
            raise ValueError(f"Malformed CSV: {exc}") from exc
        if not rows:
            raise ValueError("CSV evidence contains no data rows.")
        payload = {"records": rows}
    return validate_workflow_evidence(workflow_id, payload)
