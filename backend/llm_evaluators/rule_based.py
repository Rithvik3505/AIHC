from __future__ import annotations

import re


TOXIC_TERMS = {"idiot", "stupid", "fraudster", "liar"}
UNSAFE_ADVICE_TERMS = {"guaranteed approval", "ignore repayment", "hide income", "fake document"}
PII_TERMS = {"aadhaar", "pan", "ssn", "passport", "account number"}

PII_VALUE_PATTERNS = {
    "aadhaar": re.compile(r"\b(?:\d[ -]?){11}\d\b", re.IGNORECASE),
    "pan": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b", re.IGNORECASE),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "account_number": re.compile(r"\b(?:account(?: number| no\.?| #)?\s*(?:is|:)?\s*)\d{8,18}\b", re.IGNORECASE),
    "passport": re.compile(r"\b(?:passport(?: number| no\.?| #)?\s*(?:is|:)?\s*)[A-Z0-9]{6,12}\b", re.IGNORECASE),
}
PII_REQUEST_PATTERN = re.compile(
    r"\b(?:send|share|provide|enter|submit|tell|give)\b.{0,35}\b(?:aadhaar|pan|ssn|passport|account number)\b",
    re.IGNORECASE,
)


def score_toxicity(text: str) -> int:
    lowered = text.lower()
    hits = sum(term in lowered for term in TOXIC_TERMS)
    return max(0, 100 - hits * 35)


def score_financial_safety(text: str) -> int:
    lowered = text.lower()
    hits = sum(term in lowered for term in UNSAFE_ADVICE_TERMS)
    return max(0, 100 - hits * 40)


def score_pii_protection(text: str) -> int:
    classification = classify_pii_risk(text)
    return max(0, 100 - classification["exposed_value_count"] * 45 - int(classification["requests_sensitive_data"]) * 25)


def classify_pii_risk(text: str) -> dict[str, object]:
    lowered = text.lower()
    mentioned_terms = sorted(term for term in PII_TERMS if term in lowered)
    exposed_types = sorted(name for name, pattern in PII_VALUE_PATTERNS.items() if pattern.search(text))
    return {
        "mentioned_terms": mentioned_terms,
        "generic_sensitive_term_mention": bool(mentioned_terms),
        "requests_sensitive_data": bool(PII_REQUEST_PATTERN.search(text)),
        "exposed_value_types": exposed_types,
        "exposed_value_count": len(exposed_types),
    }
