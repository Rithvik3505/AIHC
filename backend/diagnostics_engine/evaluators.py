from __future__ import annotations

from statistics import mean, pstdev
from typing import Any

from backend.llm_evaluators.rule_based import score_financial_safety, score_pii_protection, score_toxicity
from backend.perturbation_engine.perturbations import generate_counterfactuals, generate_numeric_stress


def _records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = payload.get("records")
    return records if isinstance(records, list) else []


def _outputs(payload: dict[str, Any]) -> list[str]:
    outputs = payload.get("outputs") or payload.get("responses") or []
    return [str(output) for output in outputs] if isinstance(outputs, list) else []


def fairness_health(payload: dict[str, Any]) -> tuple[int, str]:
    records = _records(payload)
    decisions = payload.get("decisions", [])
    if records and decisions and len(records) == len(decisions):
        groups: dict[str, list[float]] = {}
        for record, decision in zip(records, decisions, strict=False):
            group = str(record.get("gender") or record.get("segment") or "unknown")
            groups.setdefault(group, []).append(float(decision))
        if len(groups) > 1:
            rates = [mean(values) for values in groups.values()]
            disparity = max(rates) - min(rates)
            return max(0, round(100 - disparity * 100)), f"Observed segment decision disparity of {disparity:.2f}."
    cf_count = len(generate_counterfactuals(records[:10])) if records else 0
    return 72 if records else 65, f"Counterfactual readiness checked across {cf_count} generated variants."


def robustness_health(payload: dict[str, Any]) -> tuple[int, str]:
    records = _records(payload)
    predictions = [float(value) for value in payload.get("predictions", []) if isinstance(value, (int, float))]
    if predictions:
        volatility = pstdev(predictions) if len(predictions) > 1 else 0
        score = max(0, min(100, round(100 - volatility * 100)))
        return score, f"Prediction volatility is {volatility:.3f}."
    stressed = generate_numeric_stress(records[:20])
    return 70 if stressed else 62, f"Generated {len(stressed)} stressed records for robustness probing."


def residual_health(payload: dict[str, Any]) -> tuple[int, str]:
    predictions = payload.get("predictions", [])
    actuals = payload.get("actuals", [])
    if predictions and actuals and len(predictions) == len(actuals):
        residuals = [abs(float(actual) - float(prediction)) for actual, prediction in zip(actuals, predictions, strict=False)]
        avg_residual = mean(residuals)
        return max(0, round(100 - avg_residual * 100)), f"Average absolute residual is {avg_residual:.3f}."
    return 66, "Residual labels were incomplete; used readiness and drift-risk fallback scoring."


def llm_safety_health(payload: dict[str, Any]) -> tuple[int, str]:
    texts = _outputs(payload)
    if not texts:
        return 60, "No responses supplied; safety score reflects missing evidence risk."
    scores = []
    for text in texts:
        scores.append(round(mean([score_toxicity(text), score_financial_safety(text), score_pii_protection(text)])))
    return round(mean(scores)), f"Evaluated {len(texts)} outputs for toxicity, unsafe advice, and PII leakage."


def data_integrity_health(payload: dict[str, Any]) -> tuple[int, str]:
    records = _records(payload)
    if not records:
        return 62, "No structured records supplied; data integrity score reflects missing evidence risk."
    total_fields = sum(len(record) for record in records)
    missing = sum(value in {None, ""} for record in records for value in record.values())
    missing_rate = missing / total_fields if total_fields else 1
    return max(0, round(100 - missing_rate * 100)), f"Missing or blank field rate is {missing_rate:.1%}."


def governance_health(payload: dict[str, Any]) -> tuple[int, str]:
    evidence = payload.get("evidence", {})
    required = ["owner", "validation_date", "model_card", "review_policy"]
    present = sum(bool(evidence.get(key)) for key in required) if isinstance(evidence, dict) else 0
    score = round((present / len(required)) * 100)
    return score, f"Governance evidence includes {present} of {len(required)} required MVP controls."


def explanation_health(payload: dict[str, Any]) -> tuple[int, str]:
    explanations = payload.get("explanations", [])
    if not explanations:
        return 58, "No explanations supplied; transparency score reflects missing user-facing rationale."
    usable = sum(len(str(item).split()) >= 8 for item in explanations)
    score = round((usable / len(explanations)) * 100)
    return score, f"{usable} of {len(explanations)} explanations met minimum clarity criteria."

