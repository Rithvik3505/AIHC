from __future__ import annotations


BASE_RECOMMENDATIONS = {
    "Bias mitigation": [
        "Run counterfactual tests before launch and after major model changes.",
        "Audit sensitive attributes and high-risk proxy variables.",
    ],
    "Fairness of model output": [
        "Track approval, score, and error rates by borrower segment.",
        "Define fairness thresholds for manual review escalation.",
    ],
    "Harmful model output": [
        "Add pre-response and post-response guardrails for regulated topics.",
        "Route vulnerable customer scenarios to reviewed templates or humans.",
    ],
    "Model validation": [
        "Create a challenger validation set with edge cases and recent drift samples.",
        "Document validation acceptance thresholds and owner sign-off.",
    ],
    "Model accuracy": [
        "Track accuracy by segment, not only overall model quality.",
        "Investigate false positives and false negatives with business impact labels.",
    ],
    "Feature importance analysis": [
        "Review top drivers for proxy risk and operational plausibility.",
        "Compare global and local explanations for high-impact decisions.",
    ],
    "Data privacy / PII protection": [
        "Minimize PII exposure and mask sensitive values in logs and prompts.",
        "Add leakage scans before records enter LLM or external model workflows.",
    ],
    "Model transparency": [
        "Expose plain-language decision reasons for founder and advisor review.",
        "Maintain model cards for each deployed AI system.",
    ],
    "Glass box vs black box testing": [
        "Use interpretable challenger models for high-stakes decisions.",
        "Compare black-box outputs against rule-based sanity checks.",
    ],
    "Human-in-the-loop": [
        "Set review queues for low-confidence or high-impact outcomes.",
        "Log overrides and use them as validation feedback.",
    ],
    "Documentation & compliance checklists": [
        "Create evidence packs with dataset, validation, fairness, and approval records.",
        "Map every high-risk use case to an accountable owner.",
    ],
    "Safety of model output": [
        "Block unsafe actions and add refusal policies for regulated advice.",
        "Test failure modes with adverse borrower and fraud scenarios.",
    ],
    "Counterfactual explanations": [
        "Generate actionable counterfactuals without exposing protected-class proxies.",
        "Test whether explanations remain stable for similar applicants.",
    ],
    "Stress testing": [
        "Simulate downturn, fraud surge, and thin-file borrower scenarios.",
        "Report sensitivity of decisions to macro and behavioral shocks.",
    ],
    "Residual analysis": [
        "Monitor prediction errors over time and by borrower segment.",
        "Retrain or recalibrate when residual variance increases materially.",
    ],
    "Outlier diagnostics": [
        "Escalate high-influence anomalies before they distort decisions.",
        "Add robust handling for anomalous transactions or document fields.",
    ],
    "Correlation analysis": [
        "Check correlations between sensitive proxies and decision drivers.",
        "Remove or constrain features with weak business justification.",
    ],
    "Adversarial testing": [
        "Add adversarial perturbations to regression tests.",
        "Harden thresholds that can be gamed through small input changes.",
    ],
    "AI red teaming": [
        "Run abuse scenarios against customer-facing and fraud-facing systems.",
        "Document exploitable behaviors and mitigation owners.",
    ],
    "Clustering / anomaly analysis": [
        "Use clusters to localize failures, not just detect them.",
        "Create segment-level alerts for emerging borrower or fraud patterns.",
    ],
    "Time-series diagnostics": [
        "Track temporal drift and seasonality in risk, fraud, and repayment signals.",
        "Use rolling windows for benchmark and recalibration decisions.",
    ],
}


def recommendations_for(practice: str, fallback: list[str] | None = None) -> list[str]:
    return BASE_RECOMMENDATIONS.get(practice, fallback or ["Review the failed cases and define an owner for remediation."])

