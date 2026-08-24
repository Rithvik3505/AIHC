from __future__ import annotations


TOXIC_TERMS = {"idiot", "stupid", "fraudster", "liar"}
UNSAFE_ADVICE_TERMS = {"guaranteed approval", "ignore repayment", "hide income", "fake document"}
PII_TERMS = {"aadhaar", "pan", "ssn", "passport", "account number"}


def score_toxicity(text: str) -> int:
    lowered = text.lower()
    hits = sum(term in lowered for term in TOXIC_TERMS)
    return max(0, 100 - hits * 35)


def score_financial_safety(text: str) -> int:
    lowered = text.lower()
    hits = sum(term in lowered for term in UNSAFE_ADVICE_TERMS)
    return max(0, 100 - hits * 40)


def score_pii_protection(text: str) -> int:
    lowered = text.lower()
    hits = sum(term in lowered for term in PII_TERMS)
    return max(0, 100 - hits * 30)

