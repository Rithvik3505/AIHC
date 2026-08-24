from __future__ import annotations

from copy import deepcopy

from backend.schemas.models import TaxonomyDefinition


def _meaningful(risk: int, pain: int, reputation: int, benchmark: int, signal: int, feasibility: int) -> dict:
    return {
        "risk_criticality": risk,
        "founder_pain": pain,
        "investor_reputational_importance": reputation,
        "benchmark_density_potential": benchmark,
        "technical_signal_strength": signal,
        "mvp_feasibility": feasibility,
    }


TEST_PATTERNS = {
    "Bias mitigation": [
        ("Demographic Sensitivity Check", "Compare outcomes after controlled protected-attribute substitutions."),
        ("Proxy Attribute Detection", "Detect whether location, occupation, education, device, or language proxies influence outcomes."),
        ("Language Bias Detection", "Check whether tone, formality, or borrower wording changes the model response."),
        ("Counterfactual Fairness Evaluation", "Run controlled counterfactuals and measure decision or score flips."),
    ],
    "Fairness of model output": [
        ("Outcome Parity Check", "Compare output rates across relevant borrower, user, or document segments."),
        ("Segment Error Rate Comparison", "Measure whether false positives, false negatives, or unsafe outputs concentrate by segment."),
        ("Similar Applicant Consistency Check", "Compare outputs for near-identical cases with equivalent risk evidence."),
        ("Segment-Level Fairness Stress Evaluation", "Evaluate parity, consistency, and error concentration across segments."),
    ],
    "Harmful model output": [
        ("Toxicity and Offensiveness Screen", "Detect offensive, hostile, or stigmatizing model outputs."),
        ("Misleading Financial Content Check", "Identify incorrect, overconfident, or non-compliant financial guidance."),
        ("Vulnerable Customer Tone Check", "Check tone and empathy in financial distress or complaint scenarios."),
        ("Multi-Dimensional Harmful Output Stress Test", "Evaluate toxicity, misinformation, emotional sensitivity, and compliance under pressure."),
    ],
    "Model validation": [
        ("Validation Evidence Completeness Check", "Confirm that validation evidence exists for the model and use case."),
        ("Holdout Performance Sanity Check", "Compare declared performance against holdout or sample evidence."),
        ("Policy Edge Case Validation", "Test edge cases against product policy and lending rules."),
        ("Independent Validation Pack Review", "Evaluate validation coverage, policy traceability, and residual risk."),
    ],
    "Model accuracy": [
        ("Critical Field Accuracy Check", "Measure accuracy on high-impact fields, labels, predictions, or responses."),
        ("False Positive and False Negative Review", "Identify operationally costly errors and their concentration."),
        ("Confidence Calibration Check", "Compare model confidence against observed correctness or review outcomes."),
        ("Segmented Accuracy and Calibration Evaluation", "Evaluate accuracy and calibration across high-risk segments."),
    ],
    "Feature importance analysis": [
        ("Top Driver Plausibility Review", "Assess whether dominant drivers have a defensible business rationale."),
        ("Proxy Driver Detection", "Check whether sensitive proxies appear among high-importance features."),
        ("Local Explanation Stability Check", "Compare local explanations across similar cases."),
        ("Driver Stability and Proxy Influence Evaluation", "Evaluate global and local feature importance for stability and proxy risk."),
    ],
    "Data privacy / PII protection": [
        ("PII Exposure Scan", "Detect sensitive identifiers in inputs, prompts, outputs, and logs."),
        ("Redaction Coverage Check", "Verify masking of identifiers before external model or evaluator use."),
        ("Retention Risk Review", "Check whether unnecessary sensitive data is retained in diagnostic evidence."),
        ("End-to-End PII Leakage Evaluation", "Evaluate leakage across upload, evaluation, output, and replay artifacts."),
    ],
    "Model transparency": [
        ("Decision Rationale Completeness Check", "Verify that outputs include understandable reasons for the decision."),
        ("Policy Traceability Check", "Map stated reasons back to documented rules, data, or model evidence."),
        ("Ambiguity and Jargon Review", "Detect vague, circular, or non-actionable explanations."),
        ("Transparency Evidence Evaluation", "Evaluate completeness, traceability, and stakeholder readability."),
    ],
    "Glass box vs black box testing": [
        ("Interpretable Challenger Agreement Check", "Compare black-box outputs against a transparent challenger model or rule set."),
        ("Unexplained Variance Review", "Identify cases where the black-box model departs from transparent logic."),
        ("Override Candidate Detection", "Flag decisions that should be reviewed because the challenger disagrees."),
        ("Black-Box Challenger Evaluation", "Evaluate agreement, unexplained variance, and review candidates."),
    ],
    "Human-in-the-loop": [
        ("Escalation Coverage Check", "Verify that high-risk or low-confidence cases route to human review."),
        ("Override Pattern Review", "Analyze manual overrides for recurring model failure modes."),
        ("Missed Escalation Detection", "Find cases that should have been reviewed but were not."),
        ("Human Review Control Effectiveness Evaluation", "Evaluate escalation design, override learning, and review coverage."),
    ],
    "Documentation & compliance checklists": [
        ("Model Card Completeness Check", "Review whether model purpose, data, limitations, and owners are documented."),
        ("Compliance Evidence Mapping", "Map evidence to applicable lending, privacy, and governance controls."),
        ("Owner and Approval Traceability Check", "Verify accountability for model changes, approvals, and exceptions."),
        ("Governance Evidence Pack Review", "Evaluate documentation completeness, traceability, and audit readiness."),
    ],
    "Safety of model output": [
        ("Unsafe Action Recommendation Check", "Detect outputs that recommend unsafe, prohibited, or non-compliant actions."),
        ("Refusal Quality Check", "Assess whether the model refuses unsafe requests while remaining helpful."),
        ("High-Severity Scenario Screen", "Test outputs under borrower distress, fraud, identity, or complaint scenarios."),
        ("Safety Stress Evaluation", "Evaluate severe failure rates across realistic and adversarial scenarios."),
    ],
    "Counterfactual explanations": [
        ("Actionability Check", "Verify that explanations provide feasible user actions."),
        ("Protected Proxy Leakage Check", "Detect whether explanations reveal or rely on sensitive proxies."),
        ("Explanation Stability Check", "Compare counterfactuals for similar cases."),
        ("Counterfactual Explanation Quality Evaluation", "Evaluate actionability, stability, and proxy leakage."),
    ],
    "Stress testing": [
        ("Economic Downturn Simulation", "Simulate macroeconomic stress and observe risk or decision shifts."),
        ("Default Spike Simulation", "Inject worsening borrower behavior, delinquency, or fraud pressure."),
        ("Operational Shock Scenario", "Test noisy, sparse, delayed, or degraded input conditions."),
        ("Portfolio Stress Scenario Evaluation", "Evaluate model resilience across multi-factor Lendingtech stress scenarios."),
    ],
    "Residual analysis": [
        ("Residual Drift Check", "Measure whether prediction errors increase over time or cohorts."),
        ("Residual Distribution Shape Check", "Detect skew, heavy tails, or concentrated error pockets."),
        ("Segment Residual Concentration Check", "Find borrower or transaction segments with larger errors."),
        ("Multi-Dimensional Residual Drift Evaluation", "Evaluate residual variance, calibration drift, and temporal degradation."),
    ],
    "Outlier diagnostics": [
        ("High-Influence Outlier Detection", "Identify records that disproportionately affect outputs or risk scores."),
        ("Behavioral Deviation Check", "Detect transactions, documents, or identity records outside expected patterns."),
        ("Impossible Value and Format Check", "Flag implausible values, malformed fields, or document inconsistencies."),
        ("Multivariate Outlier Diagnostics Evaluation", "Evaluate anomaly severity, influence, and operational risk."),
    ],
    "Correlation analysis": [
        ("Sensitive Proxy Correlation Check", "Measure relationships between sensitive proxies and decision drivers."),
        ("Outcome Association Review", "Check whether correlated features have unexplained outcome impact."),
        ("Feature Redundancy and Leakage Check", "Detect duplicate, leaky, or circular predictors."),
        ("Proxy Correlation Risk Evaluation", "Evaluate correlation structure, proxy influence, and justification gaps."),
    ],
    "Adversarial testing": [
        ("Boundary Evasion Check", "Test whether small input shifts bypass thresholds or review triggers."),
        ("Synthetic Attack Pattern Injection", "Inject attack-like patterns and measure detection failure."),
        ("Input Manipulation Robustness Check", "Perturb key fields, prompts, or documents to test output stability."),
        ("Multi-Stage Adversarial Robustness Evaluation", "Evaluate evasion, threshold instability, and coordinated attack resistance."),
    ],
    "AI red teaming": [
        ("Abuse Path Discovery", "Probe misuse scenarios and identify exploitable workflow paths."),
        ("Policy Bypass Attempt", "Test whether prompts, records, or document manipulations bypass controls."),
        ("Coordinated Attack Scenario", "Simulate staged attacks across multiple records or interactions."),
        ("Red Team Attack Chain Evaluation", "Evaluate attack success, control gaps, and mitigation priority."),
    ],
    "Clustering / anomaly analysis": [
        ("Emerging Cluster Detection", "Identify new high-risk clusters in borrower, document, or transaction behavior."),
        ("Cluster Risk Concentration Check", "Measure whether failures concentrate inside specific clusters."),
        ("Novel Segment Drift Check", "Detect clusters that differ from known operating patterns."),
        ("Cluster-Based Failure Localization Evaluation", "Evaluate anomaly clusters, risk concentration, and segment drift."),
    ],
    "Time-series diagnostics": [
        ("Temporal Drift Check", "Detect time-based changes in predictions, errors, or outputs."),
        ("Seasonality and Cycle Review", "Assess sensitivity to repayment cycles, fraud windows, or market cycles."),
        ("Rolling Stability Check", "Measure rolling performance or risk-score stability."),
        ("Time-Series Stability Evaluation", "Evaluate drift, seasonality, and rolling degradation."),
    ],
}


def _test_metadata(ai_system: str, practice: str, test_type: str) -> dict:
    workflow_references = globals().get("WORKFLOW_REFERENCES", {})
    evaluator_references = globals().get("EVALUATOR_REFERENCES", {})
    evidence_types = globals().get("EVIDENCE_TYPES", {})
    dataset_sources = globals().get("DATASET_SOURCES", {})
    benchmarked_practices = globals().get("BENCHMARKED_PRACTICES", set())
    partial_practices = globals().get("PARTIAL_PRACTICES", set())
    implemented_evaluator_practices = globals().get("IMPLEMENTED_EVALUATOR_PRACTICES", set())
    dataset_references = globals().get("DATASET_REFERENCES", {})
    benchmark_references = globals().get("BENCHMARK_REFERENCES", {})
    workflow_reference = workflow_references.get((ai_system, practice))
    evaluator_reference = evaluator_references.get(practice, "Custom Rule Engine")
    evidence_type = evidence_types.get(practice, "CSV")
    dataset_source = dataset_sources.get(practice, "Customer Dataset")
    benchmark_available = practice in benchmarked_practices or workflow_reference is not None
    return {
        "implementation_status": "Ready" if workflow_reference else ("Partial" if practice in partial_practices else "Planned"),
        "workflow_status": "Implemented" if workflow_reference else "Planned",
        "workflow_reference": workflow_reference or "workflow_registry:planned",
        "evaluator_status": "Implemented" if practice in implemented_evaluator_practices else "Planned",
        "evaluator_reference": evaluator_reference,
        "evidence_type": evidence_type,
        "dataset_source": dataset_source,
        "dataset_reference": dataset_references.get(dataset_source, "dataset_registry:customer_dataset"),
        "benchmark_status": "Available" if benchmark_available else "Planned",
        "benchmark_reference": benchmark_references.get(practice, "benchmark_registry:planned"),
        "customer_upload": "Supported" if evidence_type in {"CSV", "Prediction Log", "Prompt Log", "Conversation Transcript", "Residual File", "Time Series", "Image", "PDF"} else "Planned",
        "automation_level": "Automated" if workflow_reference and test_type == "light" else "Assisted",
    }


def _tests(prefix: str, topic: str, metrics: list[str], ai_system: str, practice: str) -> list[dict]:
    patterns = TEST_PATTERNS[practice]
    context_fn = globals().get("_system_context")
    context = context_fn(ai_system) if context_fn else topic
    tests: list[dict] = []
    for index, (name, objective) in enumerate(patterns, start=1):
        test_type = "strong" if index == 4 else "light"
        test_id = f"{prefix}-{'st1' if test_type == 'strong' else f'lt{index}'}"
        tests.append(
            {
                "id": test_id,
                "name": f"{name} for {context}",
                "test_type": test_type,
                "objective": objective,
                "inputs_required": globals().get("INPUT_REQUIREMENTS", {}).get(practice, ["customer evidence file", "model outputs"]),
                "method": globals().get("METHOD_STEPS", {}).get(practice, ["Normalize evidence", "run diagnostic evaluator", "score failures", "generate recommendations"]),
                "metrics": metrics if test_type == "strong" else metrics[:2],
                "implementation_metadata": _test_metadata(ai_system, practice, test_type),
            }
        )
    return tests


def _practice(name: str, category: str, meaningfulness: dict, use_case: str, description: str, prefix: str, metrics: list[str], ai_system: str | None = None) -> dict:
    return {
        "name": name,
        "category": category,
        "orientation": globals().get("PRACTICE_ORIENTATION", {}).get(name, "Horizontal" if category == "A" else "Hybrid"),
        "meaningfulness": meaningfulness,
        "use_cases": [
            {
                "id": prefix,
                "name": use_case,
                "description": description,
                "tests": _tests(prefix, use_case, metrics, ai_system or "Credit scoring AI", name),
            }
        ],
    }


TAXONOMY: dict = {
    "fintech_segment": "Lendingtech",
    "product_phase": "Assisted Intelligence MVP",
    "ai_systems": [
        {
            "name": "Credit scoring AI",
            "typical_use": "Estimate creditworthiness and risk score.",
            "pillars": [
                {
                    "name": "Risk",
                    "practices": [
                        _practice("Bias mitigation", "A", _meaningful(5, 5, 5, 5, 5, 4), "Credit scoring bias detection", "Detect demographic and proxy-driven score distortion.", "credit-bias", ["fairness_score", "average_score_shift", "proxy_influence"]),
                        _practice("Stress testing", "B", _meaningful(5, 4, 5, 5, 5, 4), "Credit downturn stress response", "Simulate borrower income, delinquency, and macro-risk shocks.", "credit-stress", ["stress_resilience", "score_volatility", "decision_flip_rate"]),
                    ],
                },
                {
                    "name": "Explainability",
                    "practices": [
                        _practice("Feature importance analysis", "A", _meaningful(4, 4, 5, 4, 5, 5), "Credit score driver audit", "Verify whether top score drivers are plausible, stable, and non-proxy.", "credit-feature", ["driver_stability", "proxy_driver_rate", "local_explanation_quality"]),
                        _practice("Counterfactual explanations", "A", _meaningful(4, 4, 5, 4, 5, 4), "Actionable score improvement explanations", "Check if explanations give safe, achievable borrower actions.", "credit-counterfactual", ["actionability", "counterfactual_stability", "proxy_leakage"]),
                    ],
                },
            ],
        },
        {
            "name": "Loan approval AI",
            "typical_use": "Approve, reject, or escalate applications.",
            "pillars": [
                {
                    "name": "Risk",
                    "practices": [
                        _practice("Fairness of model output", "A", _meaningful(5, 5, 5, 5, 5, 5), "Loan approval fairness", "Ensure similar applicants receive consistent approval decisions.", "approval-fairness", ["approval_parity", "counterfactual_flip_rate", "segment_disparity"]),
                        _practice("Correlation analysis", "B", _meaningful(4, 4, 5, 4, 5, 4), "Approval proxy correlation audit", "Detect correlations between sensitive proxies and approval outcomes.", "approval-correlation", ["proxy_correlation", "outcome_association", "feature_justification_gap"]),
                    ],
                },
                {
                    "name": "Governance",
                    "practices": [
                        _practice("Human-in-the-loop", "A", _meaningful(5, 5, 5, 4, 4, 5), "Manual review escalation quality", "Check whether high-impact and low-confidence decisions are escalated.", "approval-hitl", ["escalation_coverage", "override_rate", "confidence_gap"]),
                        _practice("Documentation & compliance checklists", "A", _meaningful(4, 5, 5, 4, 4, 5), "Approval governance evidence pack", "Assess whether approval logic, thresholds, and sign-offs are documented.", "approval-docs", ["evidence_completeness", "owner_coverage", "policy_traceability"]),
                    ],
                },
            ],
        },
        {
            "name": "Fraud detection AI",
            "typical_use": "Detect suspicious transactions and borrower behavior.",
            "pillars": [
                {
                    "name": "Risk",
                    "practices": [
                        _practice("Adversarial testing", "B", _meaningful(5, 5, 5, 5, 5, 4), "Adversarial testing of fraud models", "Evaluate evasion through small input manipulation and coordinated attacks.", "fraud-adversarial", ["robustness_score", "evasion_success_rate", "threshold_instability"]),
                        _practice("AI red teaming", "B", _meaningful(5, 4, 5, 4, 5, 3), "Fraud abuse scenario red team", "Probe the system with staged fraud, account takeover, and synthetic identity scenarios.", "fraud-redteam", ["attack_success_rate", "detection_gap", "abuse_path_count"]),
                    ],
                },
                {
                    "name": "Reliability",
                    "practices": [
                        _practice("Outlier diagnostics", "B", _meaningful(5, 4, 4, 5, 5, 5), "Outlier detection in suspicious transactions", "Find anomalous and high-influence transaction patterns.", "fraud-outliers", ["outlier_risk_score", "anomalous_transaction_rate", "influence_count"]),
                        _practice("Clustering / anomaly analysis", "B", _meaningful(4, 4, 4, 5, 5, 4), "Emerging fraud cluster detection", "Identify concentrated fraud behavior by merchant, device, timing, or geography.", "fraud-clusters", ["cluster_purity", "novel_cluster_rate", "segment_risk"]),
                    ],
                },
            ],
        },
        {
            "name": "KYC verification AI",
            "typical_use": "Verify identity and reduce onboarding fraud.",
            "pillars": [
                {
                    "name": "Risk",
                    "practices": [
                        _practice("Safety of model output", "A", _meaningful(5, 4, 5, 4, 5, 4), "KYC false accept and false reject safety", "Assess whether KYC decisions avoid unsafe acceptance and unfair rejection.", "kyc-safety", ["false_accept_risk", "false_reject_risk", "review_gap"]),
                        _practice("Adversarial testing", "B", _meaningful(5, 4, 5, 4, 5, 3), "KYC spoofing robustness", "Simulate manipulated identity documents and replay-style attacks.", "kyc-adversarial", ["spoof_detection_rate", "evasion_success_rate", "document_tamper_sensitivity"]),
                    ],
                },
                {
                    "name": "Data Integrity",
                    "practices": [
                        _practice("Data privacy / PII protection", "A", _meaningful(5, 5, 5, 4, 4, 5), "KYC PII leakage check", "Detect unnecessary PII retention, prompt leakage, and unsafe logging.", "kyc-privacy", ["pii_exposure_rate", "masking_coverage", "retention_risk"]),
                    ],
                },
            ],
        },
        {
            "name": "Loan default prediction AI",
            "typical_use": "Predict delinquency or default probability.",
            "pillars": [
                {
                    "name": "Reliability",
                    "practices": [
                        _practice("Residual analysis", "B", _meaningful(5, 5, 5, 5, 5, 5), "Residual drift in default prediction", "Detect prediction error drift and calibration decay over time.", "default-residual", ["residual_risk_score", "variance_growth", "calibration_stability"]),
                        _practice("Time-series diagnostics", "B", _meaningful(5, 4, 5, 5, 5, 4), "Repayment behavior temporal drift", "Track seasonality, economic shifts, and repayment-pattern drift.", "default-timeseries", ["temporal_stability", "drift_index", "rolling_auc_change"]),
                    ],
                },
                {
                    "name": "Risk",
                    "practices": [
                        _practice("Stress testing", "B", _meaningful(5, 5, 5, 5, 5, 4), "Portfolio default stress test", "Simulate macro, unemployment, and repayment shocks.", "default-stress", ["stress_loss_delta", "risk_rank_stability", "segment_loss_concentration"]),
                    ],
                },
            ],
        },
        {
            "name": "Loan underwriting AI",
            "typical_use": "Combine documents, bureau data, policies, and judgment for underwriting.",
            "pillars": [
                {
                    "name": "Explainability",
                    "practices": [
                        _practice("Model transparency", "A", _meaningful(5, 5, 5, 4, 4, 5), "Underwriting decision transparency", "Evaluate whether underwriting outputs give clear decision rationale.", "underwriting-transparency", ["reason_completeness", "policy_traceability", "ambiguity_rate"]),
                        _practice("Glass box vs black box testing", "A", _meaningful(4, 4, 5, 4, 4, 4), "Underwriting challenger comparison", "Compare black-box underwriting decisions with interpretable challenger rules.", "underwriting-glassbox", ["challenger_agreement", "unexplained_variance", "override_candidates"]),
                    ],
                },
                {
                    "name": "Governance",
                    "practices": [
                        _practice("Model validation", "A", _meaningful(5, 5, 5, 5, 5, 5), "Underwriting model validation", "Validate underwriting decisions against policy, labels, and edge cases.", "underwriting-validation", ["validation_score", "policy_violation_rate", "edge_case_failure_rate"]),
                    ],
                },
            ],
        },
        {
            "name": "OCR document extraction",
            "typical_use": "Extract income, identity, and financial data from documents.",
            "pillars": [
                {
                    "name": "Data Integrity",
                    "practices": [
                        _practice("Model accuracy", "A", _meaningful(5, 5, 4, 5, 5, 5), "Document field extraction accuracy", "Measure extraction quality for income, ID, date, and account fields.", "ocr-accuracy", ["field_accuracy", "critical_field_error_rate", "confidence_calibration"]),
                        _practice("Outlier diagnostics", "B", _meaningful(4, 4, 4, 4, 5, 5), "OCR abnormal field detection", "Find impossible, inconsistent, or high-impact extracted fields.", "ocr-outliers", ["field_outlier_rate", "format_error_rate", "manual_review_need"]),
                    ],
                },
                {
                    "name": "Reliability",
                    "practices": [
                        _practice("Stress testing", "B", _meaningful(4, 4, 4, 4, 5, 5), "OCR perturbation robustness", "Test extraction under blur, rotation, compression, and noise.", "ocr-stress", ["perturbation_resilience", "field_drop_rate", "confidence_shift"]),
                    ],
                },
            ],
        },
        {
            "name": "Customer support LLM",
            "typical_use": "Automate borrower support and loan servicing conversations.",
            "pillars": [
                {
                    "name": "Risk",
                    "practices": [
                        _practice("Harmful model output", "A", _meaningful(5, 5, 5, 5, 5, 5), "Harmful content prevention in customer service", "Avoid offensive, misleading, or insensitive customer responses.", "support-harm", ["harm_score", "misleading_response_rate", "tone_failure_rate"]),
                        _practice("Safety of model output", "A", _meaningful(5, 5, 5, 4, 5, 5), "Regulated financial advice safety", "Check whether the LLM avoids unsafe loan, repayment, or eligibility advice.", "support-safety", ["unsafe_advice_rate", "refusal_quality", "grounding_gap"]),
                    ],
                },
                {
                    "name": "Governance",
                    "practices": [
                        _practice("Human-in-the-loop", "A", _meaningful(4, 5, 4, 4, 4, 5), "Sensitive support escalation", "Verify escalation for distress, complaints, and regulated topics.", "support-hitl", ["escalation_precision", "missed_escalation_rate", "handoff_quality"]),
                        _practice("Data privacy / PII protection", "A", _meaningful(5, 5, 5, 4, 4, 5), "Support conversation PII protection", "Detect PII leakage in prompts, logs, and responses.", "support-privacy", ["pii_leakage_rate", "redaction_coverage", "unsafe_memory_use"]),
                    ],
                },
            ],
        },
    ],
}


def load_taxonomy() -> TaxonomyDefinition:
    payload = deepcopy(TAXONOMY)
    if hasattr(TaxonomyDefinition, "model_validate"):
        return TaxonomyDefinition.model_validate(payload)
    return TaxonomyDefinition.parse_obj(payload)


def list_use_cases(ai_system: str | None = None) -> list[dict[str, str]]:
    taxonomy = load_taxonomy()
    rows: list[dict[str, str]] = []
    for system in taxonomy.ai_systems:
        if ai_system and system.name != ai_system:
            continue
        for pillar in system.pillars:
            for practice in pillar.practices:
                for use_case in practice.use_cases:
                    rows.append(
                        {
                            "ai_system": system.name,
                            "pillar": pillar.name,
                            "practice": practice.name,
                            "use_case": use_case.name,
                            "category": practice.category,
                            "meaningfulness_total": str(practice.meaningfulness.total),
                        }
                    )
    return rows


def find_use_case(ai_system: str, pillar: str, practice: str, use_case: str) -> tuple[dict, dict, dict, dict]:
    taxonomy = TAXONOMY
    for system in taxonomy["ai_systems"]:
        if system["name"] != ai_system:
            continue
        for pillar_item in system["pillars"]:
            if pillar_item["name"] != pillar:
                continue
            for practice_item in pillar_item["practices"]:
                if practice_item["name"] != practice:
                    continue
                for use_case_item in practice_item["use_cases"]:
                    if use_case_item["name"] == use_case:
                        return system, pillar_item, practice_item, use_case_item
    raise KeyError(f"No taxonomy use case found for {ai_system} / {pillar} / {practice} / {use_case}")


CATEGORY_A_PRACTICES = [
    "Bias mitigation",
    "Fairness of model output",
    "Harmful model output",
    "Model validation",
    "Model accuracy",
    "Feature importance analysis",
    "Data privacy / PII protection",
    "Model transparency",
    "Glass box vs black box testing",
    "Human-in-the-loop",
    "Documentation & compliance checklists",
    "Safety of model output",
    "Counterfactual explanations",
]

CATEGORY_B_PRACTICES = [
    "Stress testing",
    "Residual analysis",
    "Outlier diagnostics",
    "Correlation analysis",
    "Adversarial testing",
    "AI red teaming",
    "Clustering / anomaly analysis",
    "Time-series diagnostics",
]

PRACTICE_PILLARS = {
    "Bias mitigation": "Risk",
    "Fairness of model output": "Risk",
    "Harmful model output": "Risk",
    "Model validation": "Governance",
    "Model accuracy": "Reliability",
    "Feature importance analysis": "Explainability",
    "Data privacy / PII protection": "Data Integrity",
    "Model transparency": "Explainability",
    "Glass box vs black box testing": "Explainability",
    "Human-in-the-loop": "Governance",
    "Documentation & compliance checklists": "Governance",
    "Safety of model output": "Risk",
    "Counterfactual explanations": "Explainability",
    "Stress testing": "Risk",
    "Residual analysis": "Reliability",
    "Outlier diagnostics": "Data Integrity",
    "Correlation analysis": "Data Integrity",
    "Adversarial testing": "Risk",
    "AI red teaming": "Risk",
    "Clustering / anomaly analysis": "Reliability",
    "Time-series diagnostics": "Reliability",
}

SYSTEM_USES = {
    "Credit scoring AI": "Estimate creditworthiness and risk score.",
    "Loan approval AI": "Approve, reject, or escalate applications.",
    "Fraud detection AI": "Detect suspicious transactions and borrower behavior.",
    "KYC verification AI": "Verify identity and reduce onboarding fraud.",
    "Loan default prediction AI": "Predict delinquency or default probability.",
    "Loan underwriting AI": "Combine documents, bureau data, policies, and judgment for underwriting.",
    "OCR document extraction": "Extract income, identity, and financial data from documents.",
    "Customer support LLM": "Automate borrower support and loan servicing conversations.",
}

B_APPLICABILITY = {
    "Stress testing": [
        "Credit scoring AI",
        "Loan approval AI",
        "Loan default prediction AI",
        "Loan underwriting AI",
        "OCR document extraction",
    ],
    "Residual analysis": [
        "Credit scoring AI",
        "Loan default prediction AI",
        "Loan underwriting AI",
        "OCR document extraction",
    ],
    "Outlier diagnostics": [
        "Fraud detection AI",
        "KYC verification AI",
        "OCR document extraction",
        "Loan default prediction AI",
    ],
    "Correlation analysis": [
        "Credit scoring AI",
        "Loan approval AI",
        "Loan underwriting AI",
    ],
    "Adversarial testing": [
        "Fraud detection AI",
        "KYC verification AI",
        "Customer support LLM",
        "OCR document extraction",
    ],
    "AI red teaming": [
        "Fraud detection AI",
        "Customer support LLM",
    ],
    "Clustering / anomaly analysis": [
        "Fraud detection AI",
        "Loan default prediction AI",
    ],
    "Time-series diagnostics": [
        "Loan default prediction AI",
        "Fraud detection AI",
    ],
}

PRACTICE_METRICS = {
    "Bias mitigation": ["fairness_score", "counterfactual_flip_rate", "proxy_influence"],
    "Fairness of model output": ["parity_gap", "segment_disparity", "outcome_consistency"],
    "Harmful model output": ["harm_score", "misleading_output_rate", "tone_failure_rate"],
    "Model validation": ["validation_score", "edge_case_failure_rate", "policy_violation_rate"],
    "Model accuracy": ["accuracy_score", "critical_error_rate", "calibration_gap"],
    "Feature importance analysis": ["driver_stability", "proxy_driver_rate", "local_explanation_quality"],
    "Data privacy / PII protection": ["pii_exposure_rate", "masking_coverage", "retention_risk"],
    "Model transparency": ["reason_completeness", "traceability_score", "ambiguity_rate"],
    "Glass box vs black box testing": ["challenger_agreement", "unexplained_variance", "override_candidates"],
    "Human-in-the-loop": ["escalation_coverage", "override_rate", "missed_escalation_rate"],
    "Documentation & compliance checklists": ["evidence_completeness", "owner_coverage", "policy_traceability"],
    "Safety of model output": ["unsafe_output_rate", "refusal_quality", "severity_weighted_failure_rate"],
    "Counterfactual explanations": ["actionability", "counterfactual_stability", "proxy_leakage"],
    "Stress testing": ["stress_resilience", "score_volatility", "decision_flip_rate"],
    "Residual analysis": ["residual_risk_score", "variance_growth", "calibration_stability"],
    "Outlier diagnostics": ["outlier_risk_score", "anomaly_rate", "influence_count"],
    "Correlation analysis": ["proxy_correlation", "outcome_association", "feature_justification_gap"],
    "Adversarial testing": ["robustness_score", "evasion_success_rate", "threshold_instability"],
    "AI red teaming": ["attack_success_rate", "detection_gap", "abuse_path_count"],
    "Clustering / anomaly analysis": ["cluster_risk_score", "novel_cluster_rate", "segment_concentration"],
    "Time-series diagnostics": ["temporal_stability", "drift_index", "rolling_performance_change"],
}

PRACTICE_ORIENTATION = {
    **{practice: "Horizontal" for practice in CATEGORY_A_PRACTICES},
    **{practice: "Hybrid" for practice in CATEGORY_B_PRACTICES},
}

PRACTICE_BASE_SCORES = {
    "Bias mitigation": _meaningful(5, 5, 5, 5, 5, 4),
    "Fairness of model output": _meaningful(5, 5, 5, 5, 5, 5),
    "Harmful model output": _meaningful(5, 5, 5, 4, 4, 5),
    "Model validation": _meaningful(4, 3, 5, 4, 4, 5),
    "Model accuracy": _meaningful(4, 5, 4, 5, 5, 5),
    "Feature importance analysis": _meaningful(4, 4, 5, 4, 5, 4),
    "Data privacy / PII protection": _meaningful(5, 4, 5, 4, 4, 5),
    "Model transparency": _meaningful(4, 4, 5, 4, 4, 5),
    "Glass box vs black box testing": _meaningful(4, 3, 4, 3, 4, 4),
    "Human-in-the-loop": _meaningful(5, 4, 5, 4, 3, 5),
    "Documentation & compliance checklists": _meaningful(3, 2, 5, 3, 2, 5),
    "Safety of model output": _meaningful(5, 5, 5, 4, 5, 5),
    "Counterfactual explanations": _meaningful(4, 4, 5, 4, 5, 4),
    "Stress testing": _meaningful(5, 4, 5, 5, 5, 4),
    "Residual analysis": _meaningful(4, 4, 4, 5, 5, 4),
    "Outlier diagnostics": _meaningful(4, 4, 4, 5, 5, 5),
    "Correlation analysis": _meaningful(4, 3, 4, 4, 4, 4),
    "Adversarial testing": _meaningful(5, 5, 5, 5, 5, 4),
    "AI red teaming": _meaningful(5, 4, 5, 4, 5, 3),
    "Clustering / anomaly analysis": _meaningful(4, 3, 4, 5, 4, 4),
    "Time-series diagnostics": _meaningful(4, 4, 4, 5, 5, 4),
}

HIGH_RISK_SYSTEM_ADJUSTMENTS = {
    "Credit scoring AI": {"risk_criticality": 1, "benchmark_density_potential": 1},
    "Loan approval AI": {"risk_criticality": 1, "investor_reputational_importance": 1},
    "Fraud detection AI": {"risk_criticality": 1, "technical_signal_strength": 1},
    "KYC verification AI": {"risk_criticality": 1},
    "Loan default prediction AI": {"benchmark_density_potential": 1, "technical_signal_strength": 1},
    "Customer support LLM": {"founder_pain": 1},
}

EVALUATOR_REFERENCES = {
    "Bias mitigation": "Fairlearn + Custom Rule Engine",
    "Fairness of model output": "Fairlearn",
    "Harmful model output": "Custom Rule Engine",
    "Model validation": "Custom Rule Engine",
    "Model accuracy": "Custom Rule Engine",
    "Feature importance analysis": "SHAP",
    "Data privacy / PII protection": "Great Expectations + Custom Rule Engine",
    "Model transparency": "Custom Rule Engine",
    "Glass box vs black box testing": "LIME + Custom Rule Engine",
    "Human-in-the-loop": "Custom Rule Engine",
    "Documentation & compliance checklists": "Custom Rule Engine",
    "Safety of model output": "Custom Rule Engine",
    "Counterfactual explanations": "DiCE + Custom Rule Engine",
    "Stress testing": "Custom Rule Engine",
    "Residual analysis": "Statistical Drift Engine",
    "Outlier diagnostics": "Great Expectations + Statistical Drift Engine",
    "Correlation analysis": "Statistical Drift Engine",
    "Adversarial testing": "ART + Custom Rule Engine",
    "AI red teaming": "ART + Custom Rule Engine",
    "Clustering / anomaly analysis": "Statistical Drift Engine",
    "Time-series diagnostics": "Statistical Drift Engine",
}

EVIDENCE_TYPES = {
    "Bias mitigation": "CSV",
    "Fairness of model output": "Prediction Log",
    "Harmful model output": "Conversation Transcript",
    "Model validation": "API Response",
    "Model accuracy": "Prediction Log",
    "Feature importance analysis": "Feature Importance Output",
    "Data privacy / PII protection": "Prompt Log",
    "Model transparency": "API Response",
    "Glass box vs black box testing": "Prediction Log",
    "Human-in-the-loop": "Prediction Log",
    "Documentation & compliance checklists": "PDF",
    "Safety of model output": "API Response",
    "Counterfactual explanations": "API Response",
    "Stress testing": "Synthetic Demo Dataset",
    "Residual analysis": "Residual File",
    "Outlier diagnostics": "CSV",
    "Correlation analysis": "CSV",
    "Adversarial testing": "Synthetic Demo Dataset",
    "AI red teaming": "Prompt Log",
    "Clustering / anomaly analysis": "CSV",
    "Time-series diagnostics": "Time Series",
}

DATASET_SOURCES = {
    "Bias mitigation": "Customer Dataset",
    "Fairness of model output": "Customer Dataset",
    "Harmful model output": "Synthetic Demo",
    "Model validation": "Customer Dataset",
    "Model accuracy": "Customer Dataset",
    "Feature importance analysis": "Customer Dataset",
    "Data privacy / PII protection": "Customer Dataset",
    "Model transparency": "Customer Dataset",
    "Glass box vs black box testing": "Customer Dataset",
    "Human-in-the-loop": "Customer Dataset",
    "Documentation & compliance checklists": "None",
    "Safety of model output": "Generated Perturbation",
    "Counterfactual explanations": "Generated Perturbation",
    "Stress testing": "Generated Perturbation",
    "Residual analysis": "Customer Dataset",
    "Outlier diagnostics": "Customer Dataset",
    "Correlation analysis": "Customer Dataset",
    "Adversarial testing": "Generated Perturbation",
    "AI red teaming": "Generated Perturbation",
    "Clustering / anomaly analysis": "Customer Dataset",
    "Time-series diagnostics": "Customer Dataset",
}

DATASET_REFERENCES = {
    "Synthetic Demo": "dataset_registry:synthetic_demo",
    "Public Dataset": "dataset_registry:public_dataset",
    "Customer Dataset": "dataset_registry:customer_dataset",
    "Benchmark Dataset": "dataset_registry:benchmark_dataset",
    "Generated Perturbation": "dataset_registry:generated_perturbation",
    "None": "dataset_registry:none",
}

WORKFLOW_REFERENCES = {
    ("Fraud detection AI", "Adversarial testing"): "workflow_registry:fraud_adversarial_testing",
    ("Credit scoring AI", "Bias mitigation"): "workflow_registry:credit_bias_mitigation",
    ("Loan approval AI", "Fairness of model output"): "workflow_registry:loan_approval_counterfactual_fairness",
    ("Customer support LLM", "Harmful model output"): "workflow_registry:support_llm_harmful_output",
    ("Loan default prediction AI", "Residual analysis"): "workflow_registry:default_residual_drift",
    ("KYC verification AI", "Outlier diagnostics"): "workflow_registry:kyc_outlier_diagnostics",
}

IMPLEMENTED_EVALUATOR_PRACTICES = {
    "Bias mitigation",
    "Fairness of model output",
    "Harmful model output",
    "Safety of model output",
    "Adversarial testing",
    "Residual analysis",
    "Outlier diagnostics",
}

PARTIAL_PRACTICES = {
    "Model accuracy",
    "Data privacy / PII protection",
    "Stress testing",
    "Correlation analysis",
    "Time-series diagnostics",
    "Feature importance analysis",
    "Model transparency",
    "Human-in-the-loop",
}

BENCHMARKED_PRACTICES = {
    "Bias mitigation",
    "Fairness of model output",
    "Harmful model output",
    "Safety of model output",
    "Adversarial testing",
    "Residual analysis",
    "Outlier diagnostics",
    "Stress testing",
}

BENCHMARK_REFERENCES = {
    "Bias mitigation": "benchmark_registry:credit_fairness_benchmark_v1",
    "Fairness of model output": "benchmark_registry:credit_fairness_benchmark_v1",
    "Harmful model output": "benchmark_registry:support_harmfulness_benchmark_v1",
    "Safety of model output": "benchmark_registry:support_harmfulness_benchmark_v1",
    "Adversarial testing": "benchmark_registry:fraud_robustness_benchmark_v1",
    "Residual analysis": "benchmark_registry:default_residual_drift_benchmark_v1",
    "Outlier diagnostics": "benchmark_registry:fraud_robustness_benchmark_v1",
    "Stress testing": "benchmark_registry:default_residual_drift_benchmark_v1",
}

INPUT_REQUIREMENTS = {
    "Bias mitigation": ["CSV borrower/application records", "model scores or decisions", "segment or protected-attribute fields where available"],
    "Fairness of model output": ["prediction log", "segment labels", "approval, score, flag, or response outputs"],
    "Harmful model output": ["conversation transcript", "AI response samples", "regulated topic labels where available"],
    "Model validation": ["validation report or API response", "holdout performance summary", "policy edge-case file"],
    "Model accuracy": ["prediction log", "actual labels or review outcomes", "confidence scores where available"],
    "Feature importance analysis": ["feature importance output", "model feature list", "sample local explanations"],
    "Data privacy / PII protection": ["prompt log or evidence file", "response samples", "PII redaction policy"],
    "Model transparency": ["API response examples", "decision reasons", "policy or rule references"],
    "Glass box vs black box testing": ["prediction log", "challenger model output or rule output", "review outcomes where available"],
    "Human-in-the-loop": ["prediction log", "review queue records", "override or escalation logs"],
    "Documentation & compliance checklists": ["model card PDF", "validation checklist", "owner and approval records"],
    "Safety of model output": ["API response samples", "unsafe scenario prompts or records", "policy labels"],
    "Counterfactual explanations": ["API response explanations", "baseline records", "counterfactual variants"],
    "Stress testing": ["synthetic demo dataset", "baseline predictions", "stress scenario parameters"],
    "Residual analysis": ["residual file", "predictions", "actual outcomes", "timestamps"],
    "Outlier diagnostics": ["CSV records", "model outputs or confidence scores", "field constraints where available"],
    "Correlation analysis": ["CSV feature matrix", "decision outputs", "sensitive proxy candidates"],
    "Adversarial testing": ["synthetic demo dataset", "baseline outputs", "generated perturbations"],
    "AI red teaming": ["prompt log or attack scenario file", "model responses", "policy controls"],
    "Clustering / anomaly analysis": ["CSV records", "embedding or feature vectors", "model outputs"],
    "Time-series diagnostics": ["time series", "rolling predictions", "actual outcomes or review labels"],
}

METHOD_STEPS = {
    "Bias mitigation": ["Generate controlled demographic or proxy variants", "compare outputs", "compute flip and disparity rates", "summarize affected segments"],
    "Fairness of model output": ["Group outputs by segment", "compute parity and error gaps", "rank high-disparity segments", "generate fairness recommendations"],
    "Harmful model output": ["Classify safety dimensions", "score harmfulness", "identify failure category", "recommend guardrails"],
    "Model validation": ["Check evidence completeness", "compare declared metrics to evidence", "run policy edge-case review", "score validation readiness"],
    "Model accuracy": ["Join predictions with outcomes", "compute critical error rates", "check calibration", "summarize high-cost errors"],
    "Feature importance analysis": ["Parse importance output", "flag proxy drivers", "compare local and global explanations", "score driver stability"],
    "Data privacy / PII protection": ["Scan evidence for PII", "check masking coverage", "flag retention risks", "score leakage exposure"],
    "Model transparency": ["Parse decision rationale", "map reasons to policy or evidence", "flag ambiguity", "score explanation quality"],
    "Glass box vs black box testing": ["Run challenger comparison", "measure agreement", "flag unexplained divergence", "identify review candidates"],
    "Human-in-the-loop": ["Review escalation rules", "compare confidence and risk to review routing", "analyze overrides", "score control effectiveness"],
    "Documentation & compliance checklists": ["Map evidence to checklist", "check ownership and approvals", "flag missing controls", "score audit readiness"],
    "Safety of model output": ["Run unsafe scenario checks", "score refusal quality", "rank severity of failures", "recommend safety controls"],
    "Counterfactual explanations": ["Generate or ingest counterfactuals", "check feasibility", "detect proxy leakage", "score explanation stability"],
    "Stress testing": ["Create stress scenarios", "run baseline and stressed cases", "measure score shifts", "aggregate resilience score"],
    "Residual analysis": ["Compute residuals", "analyze distribution and time drift", "find segment concentration", "score residual risk"],
    "Outlier diagnostics": ["Validate field constraints", "compute anomaly indicators", "rank high-influence records", "score outlier risk"],
    "Correlation analysis": ["Compute feature correlations", "test proxy associations", "review outcome linkage", "score correlation risk"],
    "Adversarial testing": ["Generate perturbations", "run baseline and attacked cases", "measure evasion and instability", "score robustness"],
    "AI red teaming": ["Run abuse scenarios", "record control bypasses", "classify attack paths", "score red-team risk"],
    "Clustering / anomaly analysis": ["Cluster records or embeddings", "rank cluster risk", "detect novel clusters", "localize failure modes"],
    "Time-series diagnostics": ["Create rolling windows", "measure temporal drift", "check seasonality", "score rolling stability"],
}


def _system_context(ai_system: str) -> str:
    return {
        "Credit scoring AI": "credit score assignment and borrower ranking",
        "Loan approval AI": "approval, rejection, and escalation decisions",
        "Fraud detection AI": "fraud scoring, alerting, and suspicious behavior detection",
        "KYC verification AI": "identity verification, document checks, and onboarding decisions",
        "Loan default prediction AI": "default probability and repayment-risk forecasts",
        "Loan underwriting AI": "underwriting recommendations, policy checks, and decision rationale",
        "OCR document extraction": "extracted document fields used in identity, income, and underwriting workflows",
        "Customer support LLM": "borrower-facing support responses and regulated loan-servicing guidance",
    }[ai_system]


def _use_case_name(ai_system: str, practice: str) -> str:
    return f"{practice} for {_system_context(ai_system)}"


def _description(ai_system: str, practice: str) -> str:
    return (
        f"Evaluate {practice.lower()} for {_system_context(ai_system)} with Lendingtech-specific "
        "trust, reliability, safety, governance, and benchmark signals."
    )


def _score_for(ai_system: str, practice: str, category: str) -> dict:
    base = deepcopy(PRACTICE_BASE_SCORES[practice])
    for key, increment in HIGH_RISK_SYSTEM_ADJUSTMENTS.get(ai_system, {}).items():
        base[key] = min(5, base[key] + increment)
    if category == "B":
        base["mvp_feasibility"] = max(3, base["mvp_feasibility"] - 1)
    return base


def _expanded_practice(ai_system: str, practice: str, category: str) -> dict:
    slug = (
        ai_system.lower()
        .replace(" / ", "-")
        .replace(" ", "-")
        .replace("_", "-")
        .replace("ai", "ai")
        + "-"
        + practice.lower().replace(" / ", "-").replace(" ", "-")
    )
    return _practice(
        practice,
        category,
        _score_for(ai_system, practice, category),
        _use_case_name(ai_system, practice),
        _description(ai_system, practice),
        slug,
        PRACTICE_METRICS[practice],
        ai_system,
    )


def _build_expanded_taxonomy() -> dict:
    systems = []
    for ai_system, typical_use in SYSTEM_USES.items():
        pillar_map: dict[str, list[dict]] = {pillar: [] for pillar in ["Risk", "Reliability", "Data Integrity", "Explainability", "Governance"]}
        for practice in CATEGORY_A_PRACTICES:
            pillar_map[PRACTICE_PILLARS[practice]].append(_expanded_practice(ai_system, practice, "A"))
        for practice, applicable_systems in B_APPLICABILITY.items():
            if ai_system in applicable_systems:
                pillar_map[PRACTICE_PILLARS[practice]].append(_expanded_practice(ai_system, practice, "B"))
        systems.append(
            {
                "name": ai_system,
                "typical_use": typical_use,
                "pillars": [
                    {"name": pillar, "practices": practices}
                    for pillar, practices in pillar_map.items()
                    if practices
                ],
            }
        )
    return {
        "fintech_segment": "Lendingtech",
        "product_phase": "Assisted Intelligence MVP",
        "ai_systems": systems,
    }


# Expanded MVP taxonomy: 104 Category A horizontal intersections +
# 26 Category B Lendingtech-depth intersections = 130 meaningful use cases.
TAXONOMY = _build_expanded_taxonomy()
