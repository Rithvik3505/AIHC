from __future__ import annotations

from copy import deepcopy
from typing import Any


SYSTEM_CONTEXT_PROFILES: dict[str, dict[str, str]] = {
    "Credit scoring AI": {
        "subject": "credit-scoring application records",
        "outcome": "credit score, rank, approval recommendation, or risk band",
        "required_fields": "application_id, model_version, score, decision or rank, decision_threshold, timestamp, segment fields, and key credit-risk features",
        "segments": "protected or comparison-group attributes plus approved proxy candidates such as geography, employment type, education, device, and language",
        "perturbables": "protected attribute labels, approved proxy fields, income, debt-to-income, bureau attributes, and thin-file indicators within documented business constraints",
        "baseline": "prior model version, holdout cohort, challenger scorecard, or customer historical monitoring window",
        "artifact": "score explanation, feature-importance output, model card, and validation pack",
    },
    "Loan approval AI": {
        "subject": "loan-approval application records",
        "outcome": "approve, reject, escalate, approval probability, or manual-review routing decision",
        "required_fields": "application_id, model_version, decision, decision_score, threshold, timestamp, segment fields, review flag, and core affordability features",
        "segments": "protected or comparison-group attributes plus location, employment, language, channel, device, and affordability proxy candidates",
        "perturbables": "protected attribute labels, proxy fields, income, obligation, tenure, collateral, and threshold-near affordability fields within policy constraints",
        "baseline": "previous approval model, policy rule baseline, internal approval cohort, or manual-review outcome set",
        "artifact": "approval rationale, policy trace, review log, model card, and validation evidence",
    },
    "Fraud detection AI": {
        "subject": "fraud transaction or account-behavior records",
        "outcome": "fraud score, alert decision, case priority, or block/escalate action",
        "required_fields": "transaction_id or account_id, model_version, fraud_score, alert_threshold, alert decision, timestamp, attack or merchant segment, and device/network indicators",
        "segments": "merchant category, device age, transaction channel, geography, customer tenure, fraud scenario, and account-risk cohort",
        "perturbables": "amount, timing, velocity, device age, merchant category, channel, and identity consistency features within an explicit attack budget",
        "baseline": "clean transaction cohort, previous model version, analyst-reviewed labels, or synthetic fraud robustness reference",
        "artifact": "alert rationale, rule overlay, analyst outcome, fraud typology notes, and incident review evidence",
    },
    "KYC verification AI": {
        "subject": "KYC identity-verification and onboarding records",
        "outcome": "verified, rejected, manual-review decision, identity confidence, or document authenticity score",
        "required_fields": "applicant_id, document_type, model_version, verification decision, confidence score, timestamp, segment fields, document-quality metadata, and review outcome when available",
        "segments": "document type, country or region, language, image quality, channel, applicant tenure, and identity-risk cohort",
        "perturbables": "document quality, field formatting, name order, address formatting, image blur, crop, and device/channel fields while preserving identity semantics",
        "baseline": "manual-review sample, previous KYC model, clean document cohort, or fraud-typology reference set",
        "artifact": "verification rationale, extracted identity fields, document metadata, review queue logs, and policy checklist",
    },
    "Loan default prediction AI": {
        "subject": "loan-performance and default-prediction records",
        "outcome": "probability of default, delinquency risk band, portfolio-risk score, or collection-priority decision",
        "required_fields": "loan_id, borrower_id, model_version, prediction, actual delinquency or default label, prediction timestamp, performance timestamp, segment fields, and macro or repayment features",
        "segments": "vintage, product, borrower segment, geography, employment type, repayment behavior, and macro-stress cohort",
        "perturbables": "income stress, repayment delay, utilization, macro variables, vintage mix, and delinquency indicators within documented scenario ranges",
        "baseline": "prior monitoring window, backtest cohort, previous model version, or internal portfolio performance baseline",
        "artifact": "backtest report, residual file, calibration plot, monitoring dashboard, and model validation pack",
    },
    "Loan underwriting AI": {
        "subject": "underwriting recommendation and policy-check records",
        "outcome": "underwriting recommendation, risk tier, policy exception, stipulation, or manual-review decision",
        "required_fields": "application_id, model_version, underwriting recommendation, risk tier, policy checks, threshold or cutoff, timestamp, segment fields, and reviewer outcome where available",
        "segments": "product, collateral type, employment type, geography, channel, exception type, reviewer cohort, and borrower segment",
        "perturbables": "income, collateral, obligations, document confidence, exception flags, and policy-boundary fields within underwriting policy constraints",
        "baseline": "policy rule baseline, senior-underwriter review sample, previous model version, or customer historical underwriting cohort",
        "artifact": "underwriting rationale, policy checklist, exception log, feature-importance output, and review evidence",
    },
    "OCR document extraction": {
        "subject": "OCR document-extraction records",
        "outcome": "extracted field value, field confidence, document-level confidence, validation decision, or manual-review flag",
        "required_fields": "document_id, document_type, model_version, extracted fields, field-level confidence, timestamp, document-quality metadata, and ground-truth or reviewed values when available",
        "segments": "document type, language, image quality, scan channel, field type, template family, and downstream workflow",
        "perturbables": "blur, crop, rotation, compression, field formatting, template variation, and missing-page indicators while preserving document semantics",
        "baseline": "reviewed extraction sample, template-specific holdout set, previous OCR model, or clean document cohort",
        "artifact": "field-level extraction output, confidence trace, validation rules, document metadata, and reviewer correction log",
    },
    "Customer support LLM": {
        "subject": "borrower-support prompt and response records",
        "outcome": "assistant response, refusal, escalation recommendation, safety label, or policy-compliance decision",
        "required_fields": "conversation_id, model_version, prompt, response, timestamp, policy label, user-intent label, segment or vulnerability flag where available, and escalation outcome",
        "segments": "intent, regulated topic, borrower vulnerability, language, channel, complaint state, account status, and severity cohort",
        "perturbables": "prompt phrasing, urgency, emotion, policy-bypass instruction, PII content, language, and context ordering while preserving the borrower request",
        "baseline": "approved response template, human-reviewed transcript set, prior model version, or synthetic safety reference prompts",
        "artifact": "prompt/output log, policy rubric, escalation rule, refusal guideline, and review annotation",
    },
}


COMMON_PREPROCESSING = [
    "Validate the evidence schema, required identifiers, model version, timestamps, and outcome fields before scoring.",
    "Coerce numeric scores, thresholds, probabilities, dates, and confidence values without imputing values that are evidence for the tested failure.",
    "Deduplicate records by stable identifier and keep an audit trail of removed duplicates, invalid rows, and not-assessable cases.",
]


BENCHMARK_POLICIES = {
    "synthetic": "Compare only with illustrative synthetic reference distributions until comparable evaluator versions, evidence contracts, cohort definitions, anonymization, jurisdiction/product segmentation, time windows, minimum cohort size, and uncertainty reporting exist.",
    "internal": "Compare with a customer-internal historical baseline or challenger baseline that used the same evidence contract, model version scope, time window definition, and scoring implementation.",
    "policy": "Compare with policy-defined tolerance or configured MVP default; this is not a regulatory or industry threshold unless the policy itself provides the bound.",
    "public": "Compare with public-dataset reference only when labels, features, population, preprocessing, and evaluator version are documented as comparable.",
}


def _artifact(profile: dict[str, str], name: str) -> str:
    return f"{name} evidence for {profile['subject']}: {profile['required_fields']}."


def _standard_inputs(profile: dict[str, str], extra: list[str]) -> list[str]:
    return [
        _artifact(profile, "Primary diagnostic"),
        f"Context fields for cohorting: {profile['segments']}.",
        f"Baseline or comparator: {profile['baseline']}.",
        *extra,
    ]


def _standard_preprocessing(profile: dict[str, str], extra: list[str]) -> list[str]:
    return [
        *COMMON_PREPROCESSING,
        f"Construct analysis cohorts for {profile['segments']} and verify minimum group sizes before interpreting stable population differences.",
        *extra,
    ]


def _observational(profile: dict[str, str], procedure: str) -> list[str]:
    return [
        f"No synthetic perturbation. Evaluate observed {profile['subject']} against {profile['baseline']}.",
        procedure,
        "Retain not-assessable cases separately instead of converting missing evidence into a favorable score.",
    ]


def _controlled(profile: dict[str, str], procedure: str) -> list[str]:
    return [
        f"Generate paired variants by changing only the specified controlled attribute or feature for {profile['subject']}.",
        f"Keep legitimate risk variables, timestamps, model version, policy context, and non-target fields invariant; allowed changes are limited to {profile['perturbables']}.",
        procedure,
        "Use deterministic variant IDs and fixed scenario definitions so the paired comparison is replayable.",
    ]


def _benchmark(policy_key: str, detail: str) -> list[str]:
    return [BENCHMARK_POLICIES[policy_key], detail]


def _metric(name: str, definition: str, direction: str) -> str:
    return f"{name}: {definition}. Direction: {direction}."


def _if(condition: str, action: str) -> str:
    return f"If {condition}: {action}"


def _apply_context(items: list[str], profile: dict[str, str]) -> list[str]:
    return [item.format(**profile) for item in items]


PRACTICE_DIAGNOSTIC_BLUEPRINTS: dict[str, list[dict[str, Any]]] = {
    "Bias mitigation": [
        {
            "objective": "Detect whether changing only protected or comparison-group attributes changes {outcome} beyond configured tolerance.",
            "technique": "paired counterfactual consistency and demographic parity difference",
            "inputs": ["Protected or comparison-group attribute dictionary and approved proxy list."],
            "preprocessing": ["Create matched pairs and verify that non-target risk variables remain unchanged."],
            "perturbation": "Create one variant per controlled attribute value and one unchanged baseline record per evaluated case.",
            "method": ["Run or ingest baseline and paired-variant outcomes.", "Calculate pair-level outcome flips and score shifts by controlled attribute.", "Localize flips by segment, model version, and risk-band boundary."],
            "primary_metrics": [_metric("counterfactual_flip_rate", "number of paired variants with changed outcome divided by valid paired variants", "lower is better"), _metric("average_score_shift", "mean absolute change in score or probability after only the controlled attribute changes", "lower is better")],
            "secondary_metrics": [_metric("valid_pair_count", "number of baseline/variant pairs that passed invariant checks", "higher improves confidence"), _metric("boundary_flip_share", "flips occurring within the configured decision-boundary band divided by all flips", "lower is better")],
            "benchmark": _benchmark("policy", "Use configured MVP default tolerance only as an internal decision aid; report confidence intervals when sample size allows."),
            "failure": [_if("counterfactual flip rate or score shift exceeds the configured tolerance", "flag protected-attribute sensitivity for review"), _if("valid paired evidence is below the minimum group size", "mark the test insufficient evidence rather than treating disparity as stable")],
            "recommendation": [_if("paired flips exceed tolerance", "inspect drivers for proxy leakage, constrain or retrain affected features, and rerun the paired evaluation"), _if("sample size is insufficient", "collect representative evidence before drawing population-level fairness conclusions")],
        },
        {
            "objective": "Detect whether approved proxy candidates disproportionately influence {outcome} after legitimate risk variables are held constant.",
            "technique": "proxy sensitivity analysis with conditional outcome comparison",
            "inputs": ["Proxy-candidate dictionary, feature lineage, and business justification for each proxy field."],
            "preprocessing": ["Normalize proxy values and stratify by comparable risk bands before measuring proxy effects."],
            "perturbation": "Vary one proxy candidate at a time inside documented business-plausible ranges while holding protected attributes and core risk variables invariant.",
            "method": ["Rank proxy candidates by conditional association with outcomes.", "Run paired proxy substitutions for high-risk proxies.", "Compare proxy-driven score shifts against policy tolerance and segment concentration."],
            "primary_metrics": [_metric("proxy_influence_rate", "proxy substitutions that materially change the outcome divided by valid proxy variants", "lower is better"), _metric("conditional_disparity_gap", "largest outcome-rate difference across proxy values inside comparable risk strata", "lower is better")],
            "secondary_metrics": [_metric("proxy_coverage", "share of records with populated proxy candidates", "higher improves confidence"), _metric("segment_contribution", "share of total disparity attributable to each proxy/segment pair", "lower concentration is better")],
            "benchmark": _benchmark("policy", "Compare against documented feature-use policy and internal historical proxy-sensitivity results."),
            "failure": [_if("a proxy has material outcome influence without documented business justification", "flag proxy-bias risk"), _if("proxy coverage is too sparse for a stable estimate", "mark affected proxy findings not assessable")],
            "recommendation": [_if("unjustified proxy influence is detected", "remove, transform, constrain, or document the proxy and rerun sensitivity tests"), _if("coverage is sparse", "improve feature lineage and data capture before using the result for model changes")],
        },
        {
            "objective": "Detect whether tone, language, formality, or borrower wording changes {outcome} when financial facts are unchanged.",
            "technique": "semantic-preserving text counterfactual consistency",
            "inputs": ["Original text fields, normalized semantic labels, language/formality labels, and unchanged structured risk features."],
            "preprocessing": ["Separate semantic content from style attributes and reject variants that change financial facts."],
            "perturbation": "Generate language, tone, spelling, or formality variants that preserve borrower facts, requested product, and policy context.",
            "method": ["Create semantic-preserving wording variants.", "Compare model outputs between original and variants.", "Group failures by language, style, segment, and model version."],
            "primary_metrics": [_metric("language_style_flip_rate", "wording variants that change the outcome divided by valid wording variants", "lower is better"), _metric("semantic_consistency_score", "one minus the share of semantically equivalent variants with materially different outcomes", "higher is better")],
            "secondary_metrics": [_metric("variant_rejection_rate", "generated variants rejected for changing facts divided by proposed variants", "lower indicates cleaner perturbations"), _metric("language_group_failure_count", "number of failures per language or style cohort", "lower is better")],
            "benchmark": _benchmark("internal", "Compare with previous model or template baseline evaluated on the same semantic-preserving variant set."),
            "failure": [_if("semantically equivalent variants produce inconsistent outcomes beyond tolerance", "flag language-bias risk"), _if("variants cannot be verified as fact-preserving", "mark affected cases not assessable")],
            "recommendation": [_if("language/style inconsistency is material", "add style-invariant training or constraints and retest with verified semantic pairs"), _if("variant quality is weak", "tighten variant review before interpreting model sensitivity")],
        },
        {
            "objective": "Evaluate protected-attribute, proxy, and language sensitivity together to identify worst-case fairness failures in {outcome}.",
            "technique": "multi-factor paired counterfactual fairness evaluation with uncertainty reporting",
            "inputs": ["Joined evidence containing baseline records, controlled variants, proxy dictionary, segment labels, decision thresholds, and model version."],
            "preprocessing": ["Build a reproducible paired evaluation matrix and compute uncertainty only for cohorts meeting minimum size."],
            "perturbation": "Combine protected-attribute, proxy, and language/style variants under a fixed scenario matrix while preserving legitimate risk variables and business plausibility.",
            "method": ["Run paired comparisons across all scenario families.", "Estimate worst-case and average flip rates with bootstrap confidence intervals where sample size permits.", "Assess interaction effects between protected attributes, proxies, and boundary proximity.", "Produce severity-weighted fairness findings by cohort."],
            "primary_metrics": [_metric("worst_case_counterfactual_flip_rate", "maximum valid flip rate across scenario families and cohorts", "lower is better"), _metric("severity_weighted_bias_score", "weighted failure score combining flip rate, score shift, boundary proximity, and affected-record count", "lower is better")],
            "secondary_metrics": [_metric("bootstrap_interval_width", "confidence interval width for key disparity estimates", "lower improves certainty"), _metric("interaction_failure_count", "number of failures caused only by combined protected/proxy/style perturbations", "lower is better")],
            "benchmark": _benchmark("synthetic", "Illustrative synthetic reference distributions may contextualize severity, but not as verified Lendingtech industry percentiles."),
            "failure": [_if("worst-case or severity-weighted bias exceeds configured tolerance", "flag strong fairness failure"), _if("confidence intervals are too wide", "label population inference uncertain even if directional risk is visible")],
            "recommendation": [_if("strong fairness failure is confirmed", "prioritize affected cohorts, adjust feature constraints or model training, document residual risk, and rerun the full scenario matrix"), _if("uncertainty is high", "expand labeled evidence before using the finding as a benchmarkable result")],
        },
    ],
}


PRACTICE_DIAGNOSTIC_BLUEPRINTS.update(
    {
        "Fairness of model output": [
            {
                "objective": "Detect unequal observed outcome rates for {outcome} across borrower or operational segments.",
                "technique": "demographic parity difference with minimum-cohort checks",
                "inputs": ["Segment labels, outcome labels, thresholds, and denominator definition for eligible cases."],
                "preprocessing": ["Normalize outcome labels and remove records outside the eligible denominator with reasons retained."],
                "perturbation": "No synthetic perturbation. Evaluate observed segment-level outcomes against the configured reference cohort and policy tolerance.",
                "method": ["Compute outcome rates by segment.", "Compare each segment with the reference cohort.", "Report disparity direction, sample size, and affected-record counts."],
                "primary_metrics": [_metric("approval_parity_difference", "absolute difference between segment outcome rate and reference-cohort outcome rate", "lower is better"), _metric("minimum_segment_rate", "lowest valid segment outcome rate among eligible cohorts", "interpret relative to policy context")],
                "secondary_metrics": [_metric("segment_sample_size", "eligible record count per segment", "higher improves confidence"), _metric("affected_record_count", "estimated count of records associated with material disparity", "lower is better")],
                "benchmark": _benchmark("policy", "Use policy-defined tolerance or configurable MVP default; standards inform review discipline but do not supply peer percentiles."),
                "failure": [_if("a valid segment exceeds configured parity tolerance", "flag outcome fairness risk"), _if("a segment is below minimum sample size", "mark that segment insufficient evidence")],
                "recommendation": [_if("outcome parity failure is detected", "review thresholds and feature effects for affected segments and rerun fairness monitoring"), _if("sample size is insufficient", "collect more representative outcomes before escalating the disparity as stable")],
            },
            {
                "objective": "Detect whether prediction errors for {outcome} concentrate in specific segments.",
                "technique": "equalized-odds difference and segment error-rate comparison",
                "inputs": ["Predictions, decisions, ground-truth labels or reviewed outcomes, segment labels, and model version."],
                "preprocessing": ["Join predictions to actual labels and normalize false-positive and false-negative definitions."],
                "perturbation": "No synthetic perturbation. Compare observed error rates across segments using the same label and threshold definitions.",
                "method": ["Calculate false-positive and false-negative rates by segment.", "Compare segment error rates to the reference cohort.", "Rank segments by operational harm and label uncertainty."],
                "primary_metrics": [_metric("equalized_odds_gap", "maximum absolute segment gap across false-positive and false-negative rates", "lower is better"), _metric("segment_error_rate_gap", "largest difference between a segment error rate and reference error rate", "lower is better")],
                "secondary_metrics": [_metric("label_coverage", "records with valid ground-truth labels divided by scored records", "higher improves confidence"), _metric("error_harm_count", "number of high-impact false positives or false negatives by segment", "lower is better")],
                "benchmark": _benchmark("internal", "Compare against prior monitoring windows or challenger model results with the same labels and threshold."),
                "failure": [_if("equalized-odds gap exceeds configured tolerance", "flag segment error concentration"), _if("label coverage is incomplete", "mark missing-label cohorts not assessable")],
                "recommendation": [_if("segment error concentration is material", "inspect training coverage and threshold calibration for affected cohorts"), _if("labels are missing", "improve outcome-label capture before benchmark interpretation")],
            },
            {
                "objective": "Detect inconsistent {outcome} for near-identical cases with equivalent risk evidence.",
                "technique": "nearest-neighbor consistency analysis",
                "inputs": ["Feature vectors, outcome labels, similarity keys, thresholds, and excluded protected/proxy fields."],
                "preprocessing": ["Scale comparable numeric fields and define a documented similarity distance that excludes target protected fields."],
                "perturbation": "No synthetic perturbation. Compare observed nearest-neighbor records that are equivalent under documented business similarity rules.",
                "method": ["Construct nearest-neighbor pairs within each eligible risk band.", "Measure outcome disagreement among similar cases.", "Inspect disagreements by segment, threshold proximity, and model version."],
                "primary_metrics": [_metric("similar_case_disagreement_rate", "near-neighbor pairs with different outcomes divided by valid near-neighbor pairs", "lower is better"), _metric("risk_equivalent_consistency_score", "one minus disagreement among risk-equivalent pairs", "higher is better")],
                "secondary_metrics": [_metric("valid_neighbor_pair_count", "number of pairs satisfying similarity constraints", "higher improves confidence"), _metric("boundary_pair_share", "near-neighbor pairs close to the decision threshold", "contextual")],
                "benchmark": _benchmark("internal", "Compare with prior model version or rule baseline built with the same similarity definition."),
                "failure": [_if("similar-case disagreement exceeds tolerance outside documented policy exceptions", "flag inconsistent treatment"), _if("neighbor construction produces too few valid pairs", "mark consistency not assessable")],
                "recommendation": [_if("inconsistent treatment is detected", "review model monotonicity, policy exceptions, and threshold handling for paired cases"), _if("valid pairs are scarce", "define a richer similarity cohort before drawing conclusions")],
            },
            {
                "objective": "Evaluate parity, error concentration, and similar-case consistency together for {outcome}.",
                "technique": "multi-metric segment fairness stress evaluation with uncertainty reporting",
                "inputs": ["Predictions, decisions, ground-truth labels, segment labels, thresholds, similarity features, and model version."],
                "preprocessing": ["Create aligned denominators for parity, error, and similarity analyses and document exclusions separately."],
                "perturbation": "No synthetic perturbation. Integrate observed segment, label, and similarity evidence into one reproducible fairness review.",
                "method": ["Compute parity, equalized-odds, and similar-case consistency metrics.", "Estimate uncertainty for valid segment comparisons.", "Identify cohorts failing multiple fairness criteria.", "Assign severity using affected-record count, decision impact, and statistical confidence."],
                "primary_metrics": [_metric("multi_metric_fairness_failure_rate", "segments failing at least one primary fairness criterion divided by assessable segments", "lower is better"), _metric("severity_weighted_segment_disparity", "weighted disparity score combining parity, error gaps, consistency, and impact", "lower is better")],
                "secondary_metrics": [_metric("criteria_overlap_count", "segments failing more than one fairness criterion", "lower is better"), _metric("uncertainty_flag_count", "segment findings with wide confidence intervals or weak labels", "lower improves confidence")],
                "benchmark": _benchmark("synthetic", "Illustrative synthetic fairness distributions can be used for demos only; future peer benchmarking requires comparable evaluator version and cohort segmentation."),
                "failure": [_if("a segment fails multiple fairness criteria or severity exceeds tolerance", "flag strong fairness risk"), _if("uncertainty prevents stable inference", "separate directional risk from benchmarkable finding")],
                "recommendation": [_if("strong fairness risk is confirmed", "prioritize remediation for overlapping failures and retest after threshold or model changes"), _if("uncertainty is high", "expand labels and cohorts before comparing externally")],
            },
        ],
    }
)


def _make_generic_practice(
    practice: str,
    *,
    modes: list[tuple[str, str, str]],
    benchmark_key: str,
    evidence_extra: list[str],
    preprocessing_extra: list[str],
    recommendations: list[str],
) -> list[dict[str, Any]]:
    blueprints = []
    for index, (focus, technique, perturbation_kind) in enumerate(modes, start=1):
        strong = index == 4
        if perturbation_kind == "controlled":
            perturbation = f"Target {focus}. Create controlled scenario variants for {{subject}}; keep model version, timestamps, policy context, and unrelated fields invariant while changing only {{perturbables}}."
        else:
            perturbation = f"No synthetic perturbation. Evaluate observed {{subject}} for {focus} against the comparator, policy, or historical baseline using the same evidence contract."
        depth = "Use multi-source evidence, segment interaction analysis, bootstrap confidence intervals where sample size permits, and severity-weighted findings." if strong else "Keep the procedure directional and low-cost while retaining not-assessable cases separately."
        metric_base = focus.lower().replace(" ", "_").replace("-", "_")
        blueprints.append(
            {
                "objective": f"Detect {focus} affecting {{outcome}} in {{subject}}.",
                "technique": technique,
                "inputs": evidence_extra,
                "preprocessing": preprocessing_extra,
                "perturbation": perturbation,
                "method": [
                    f"Prepare the evidence slice needed to assess {focus}.",
                    f"Calculate the primary {technique} result for {{outcome}}.",
                    "Localize failures by segment, model version, threshold proximity, evidence quality, and operational impact.",
                    depth,
                ],
                "primary_metrics": [
                    _metric(f"{metric_base}_rate", f"records, pairs, or scenarios failing the {focus} criterion divided by assessable records, pairs, or scenarios", "lower is better"),
                    _metric(f"{metric_base}_severity", f"impact-weighted severity of {focus} using configured MVP default weights, not regulatory thresholds", "lower is better"),
                ],
                "secondary_metrics": [
                    _metric(f"{metric_base}_coverage", f"assessable evidence count for {focus} divided by submitted evidence count", "higher improves confidence"),
                    _metric(f"{metric_base}_concentration", f"share of failures concentrated in the largest affected segment or scenario", "lower is better"),
                ],
                "benchmark": _benchmark(benchmark_key, f"Interpret {focus} against comparable internal evidence or illustrative synthetic reference distributions only when the same evaluator version and evidence contract are used."),
                "failure": [
                    _if(f"{focus} exceeds configured MVP default or documented policy tolerance", f"flag {practice} failure"),
                    _if("required evidence is missing or below minimum sample size", "mark the finding insufficient evidence or not assessable"),
                ],
                "recommendation": [
                    _if(f"{focus} exceeds tolerance", recommendations[min(index - 1, len(recommendations) - 1)]),
                    _if("the finding is not assessable", "collect the missing evidence contract before using the result for benchmarking or remediation sign-off"),
                ],
            }
        )
    return blueprints


PRACTICE_DIAGNOSTIC_BLUEPRINTS.update(
    {
        "Harmful model output": _make_generic_practice(
            "Harmful model output",
            modes=[
                ("toxic or stigmatizing language", "lexicon-assisted toxicity rubric with human-review labels", "observational"),
                ("misleading regulated financial guidance", "rule-based policy and factual-consistency review", "observational"),
                ("unsafe tone for vulnerable borrower situations", "scenario-labeled empathy and escalation rubric", "observational"),
                ("combined harmful-output exposure under pressure scenarios", "severity-weighted multi-dimensional safety evaluation", "controlled"),
            ],
            benchmark_key="synthetic",
            evidence_extra=["Input/output samples, regulated-topic labels, safety labels, refusal labels where applicable, and reviewed failure annotations."],
            preprocessing_extra=["Normalize prompts and responses, preserve full text for review, and separate PII redaction from safety scoring."],
            recommendations=["tighten response policy, add reviewed templates, and rerun harmful-output tests", "ground regulated guidance in approved policy content and block unsupported claims", "route vulnerable-customer scenarios to escalation or reviewed responses", "prioritize high-severity safety failures before expanding automation"],
        ),
        "Model validation": _make_generic_practice(
            "Model validation",
            modes=[
                ("missing validation evidence", "structured validation-evidence completeness review", "observational"),
                ("unsupported holdout performance claims", "holdout metric reproducibility check", "observational"),
                ("policy edge-case validation gaps", "rule-based policy edge-case coverage review", "observational"),
                ("independent validation-pack weakness", "multi-artifact validation pack review with residual-risk scoring", "observational"),
            ],
            benchmark_key="policy",
            evidence_extra=["Validation report, holdout definition, metric calculation notes, policy edge-case inventory, owner approval, and model version."],
            preprocessing_extra=["Map validation artifacts to model version and use case, then separate missing evidence from failed evidence."],
            recommendations=["complete the missing validation artifacts and assign owners", "recompute holdout metrics from traceable evidence before relying on claims", "add policy edge cases to validation gates", "obtain independent review and document residual risk before launch"],
        ),
        "Model accuracy": _make_generic_practice(
            "Model accuracy",
            modes=[
                ("critical-field or label accuracy loss", "accuracy and critical-error-rate analysis", "observational"),
                ("false-positive and false-negative operational harm", "confusion-matrix error concentration review", "observational"),
                ("miscalibrated confidence or probability scores", "calibration curve and expected calibration error", "observational"),
                ("segment-level accuracy and calibration degradation", "stratified accuracy and calibration evaluation with uncertainty reporting", "observational"),
            ],
            benchmark_key="internal",
            evidence_extra=["Predictions, actual labels or review outcomes, confidence scores, decision thresholds, error-cost labels, and model version."],
            preprocessing_extra=["Join predictions to actuals, normalize label definitions, and verify that missing labels are not scored as correct."],
            recommendations=["inspect failed fields or labels and retrain after label-quality review", "rebalance thresholds or review queues around costly error types", "calibrate probabilities before confidence-based automation", "remediate segment-specific accuracy gaps before external comparison"],
        ),
        "Feature importance analysis": _make_generic_practice(
            "Feature importance analysis",
            modes=[
                ("implausible top decision drivers", "global feature-importance plausibility review", "observational"),
                ("sensitive-proxy drivers in high-importance features", "proxy-driver detection and feature-lineage review", "observational"),
                ("unstable local explanations for similar cases", "local explanation stability comparison", "observational"),
                ("driver instability and proxy influence across cohorts", "global/local explanation consistency evaluation", "observational"),
            ],
            benchmark_key="internal",
            evidence_extra=["Feature-importance output, feature dictionary, local explanations, sensitive/proxy field list, and business justification notes."],
            preprocessing_extra=["Normalize feature names, join aliases to the data dictionary, and separate missing lineage from low-importance fields."],
            recommendations=["document or remove implausible drivers", "review proxy drivers and constrain unsupported features", "stabilize local explanations before user-facing deployment", "compare explanations across cohorts and document residual proxy risk"],
        ),
        "Data privacy / PII protection": _make_generic_practice(
            "Data privacy / PII protection",
            modes=[
                ("PII exposure in evidence or outputs", "pattern and dictionary based PII exposure scan", "observational"),
                ("incomplete redaction before model or evaluator use", "redaction coverage and masking consistency check", "observational"),
                ("unnecessary sensitive-data retention", "data-minimization and retention-risk review", "observational"),
                ("end-to-end PII leakage across diagnostic artifacts", "multi-stage privacy leakage evaluation", "observational"),
            ],
            benchmark_key="policy",
            evidence_extra=["Prompt logs, response samples, record fields, redaction policy, retention policy, and approved sensitive-field dictionary."],
            preprocessing_extra=["Classify sensitive fields before masking and keep raw/derived evidence boundaries explicit."],
            recommendations=["remove or mask exposed PII and rerun leakage scans", "apply redaction before external model or evaluator boundaries", "shorten retention or remove nonessential sensitive fields", "review the full diagnostic path for leakage before sharing reports"],
        ),
        "Model transparency": _make_generic_practice(
            "Model transparency",
            modes=[
                ("missing decision rationale", "rationale completeness review", "observational"),
                ("rationale not traceable to policy or evidence", "policy traceability mapping", "observational"),
                ("ambiguous or jargon-heavy explanation language", "plain-language explanation rubric", "observational"),
                ("weak stakeholder transparency evidence", "multi-stakeholder transparency pack evaluation", "observational"),
            ],
            benchmark_key="policy",
            evidence_extra=["Decision reasons, policy references, model output samples, stakeholder explanation requirements, and reviewed explanation labels."],
            preprocessing_extra=["Normalize rationale fields and map each reason to available evidence without rewriting the explanation."],
            recommendations=["add complete reasons for high-impact decisions", "link reasons to policy and evidence references", "rewrite ambiguous explanations using approved plain-language templates", "maintain transparency evidence for founder, reviewer, and borrower audiences"],
        ),
        "Glass box vs black box testing": _make_generic_practice(
            "Glass box vs black box testing",
            modes=[
                ("low agreement with interpretable challenger", "challenger-model agreement analysis", "observational"),
                ("unexplained black-box variance", "residual disagreement and variance review", "observational"),
                ("cases requiring override review", "override-candidate detection from challenger disagreement", "observational"),
                ("black-box divergence from transparent logic", "multi-scenario challenger evaluation", "observational"),
            ],
            benchmark_key="internal",
            evidence_extra=["Black-box outputs, challenger model or rule outputs, shared feature set, thresholds, and reviewed outcomes."],
            preprocessing_extra=["Align black-box and challenger records by identifier and verify both saw the same eligible features."],
            recommendations=["investigate large challenger disagreement before high-impact use", "document black-box variance that cannot be justified", "route disagreement cases to review", "calibrate or constrain the black-box model where transparent logic is more reliable"],
        ),
        "Human-in-the-loop": _make_generic_practice(
            "Human-in-the-loop",
            modes=[
                ("missing escalation for high-risk or low-confidence cases", "escalation coverage analysis", "observational"),
                ("unmonitored override patterns", "manual override concentration review", "observational"),
                ("missed escalation against review policy", "missed-review rule comparison", "observational"),
                ("weak human-review control effectiveness", "end-to-end human-control effectiveness evaluation", "observational"),
            ],
            benchmark_key="policy",
            evidence_extra=["Review queue logs, confidence scores, risk scores, escalation rules, override reasons, reviewer identifiers, and final outcomes."],
            preprocessing_extra=["Normalize review statuses and preserve override reason text without collapsing distinct reviewer actions."],
            recommendations=["route high-risk or low-confidence cases to review", "analyze override clusters and feed lessons into validation", "repair review rules that miss policy-required escalations", "monitor reviewer workload, override quality, and model feedback loops"],
        ),
        "Documentation & compliance checklists": _make_generic_practice(
            "Documentation & compliance checklists",
            modes=[
                ("incomplete model-card evidence", "model-card completeness checklist review", "observational"),
                ("missing compliance evidence mapping", "control-to-evidence traceability review", "observational"),
                ("unclear ownership and approval traceability", "owner and approval lineage review", "observational"),
                ("weak governance evidence pack", "structured governance pack audit-readiness review", "observational"),
            ],
            benchmark_key="policy",
            evidence_extra=["Model card, data sheet, validation checklist, approvals, owners, exception logs, policy mapping, and version history."],
            preprocessing_extra=["Map artifacts to model version and use case and mark missing documents as evidence gaps, not low-risk findings."],
            recommendations=["complete model cards for high-impact systems", "map controls to evidence before audits or investor diligence", "assign accountable owners and approval records", "assemble a versioned governance pack with residual-risk sign-off"],
        ),
        "Safety of model output": _make_generic_practice(
            "Safety of model output",
            modes=[
                ("unsafe action recommendations", "policy-prohibited action detection", "observational"),
                ("poor refusal quality for unsafe requests", "refusal helpfulness and policy compliance rubric", "controlled"),
                ("high-severity scenario failure", "severity-labeled scenario safety screen", "controlled"),
                ("severe output failure under realistic and adversarial scenarios", "multi-scenario safety stress evaluation", "controlled"),
            ],
            benchmark_key="synthetic",
            evidence_extra=["Input/output samples, unsafe scenario labels, refusal labels where applicable, policy rubric, escalation rule, and severity labels."],
            preprocessing_extra=["Normalize scenario labels and preserve original prompt/output text for reviewer traceability."],
            recommendations=["block prohibited actions and retest affected scenarios", "improve refusal templates while preserving useful safe guidance", "escalate high-severity topics to reviewed flows", "prioritize severe safety failures before expanding automation"],
        ),
        "Counterfactual explanations": _make_generic_practice(
            "Counterfactual explanations",
            modes=[
                ("inactionable explanation recommendations", "counterfactual actionability review", "observational"),
                ("protected-proxy leakage in explanations", "explanation proxy leakage detection", "observational"),
                ("unstable explanations for similar cases", "counterfactual explanation stability comparison", "observational"),
                ("poor counterfactual explanation quality", "multi-criterion counterfactual explanation evaluation", "observational"),
            ],
            benchmark_key="policy",
            evidence_extra=["Counterfactual explanations, baseline records, feasibility constraints, protected/proxy dictionary, and similar-case groups."],
            preprocessing_extra=["Normalize counterfactual actions and reject suggestions that change immutable or prohibited attributes."],
            recommendations=["replace infeasible actions with policy-approved actionable guidance", "remove protected-proxy leakage from explanation generation", "stabilize explanations for similar borrowers or records", "validate actionability, stability, and proxy safety before user-facing release"],
        ),
        "Stress testing": _make_generic_practice(
            "Stress testing",
            modes=[
                ("economic downturn sensitivity", "macro-scenario stress simulation", "controlled"),
                ("default or fraud spike sensitivity", "event-rate shock simulation", "controlled"),
                ("operational noisy-input shock sensitivity", "data degradation stress scenario", "controlled"),
                ("portfolio-level multi-factor stress weakness", "multi-factor scenario stress evaluation", "controlled"),
            ],
            benchmark_key="synthetic",
            evidence_extra=["Baseline records, baseline predictions, scenario parameters, decision thresholds, model version, and stress severity definitions."],
            preprocessing_extra=["Freeze the baseline cohort and validate scenario ranges before applying stress changes."],
            recommendations=["recalibrate or add controls for downturn-sensitive decisions", "test resilience against elevated event rates", "harden preprocessing and review queues for degraded inputs", "document portfolio resilience and residual stress risk"],
        ),
        "Residual analysis": _make_generic_practice(
            "Residual analysis",
            modes=[
                ("temporal residual drift", "rolling residual drift analysis", "observational"),
                ("skewed or heavy-tailed residual distribution", "residual distribution shape review", "observational"),
                ("segment residual concentration", "segment residual concentration analysis", "observational"),
                ("multi-dimensional residual drift", "residual drift evaluation with calibration and uncertainty reporting", "observational"),
            ],
            benchmark_key="synthetic",
            evidence_extra=["Predictions, actual labels, residuals or sufficient fields to compute residuals, timestamps, segments, and model version."],
            preprocessing_extra=["Sort by prediction/performance time and compute residuals without clipping large errors."],
            recommendations=["investigate drifted windows and recalibrate or retrain", "review large residual tails for data or model failure", "prioritize segments with concentrated residuals", "separate calibration drift from random residual noise before remediation"],
        ),
        "Outlier diagnostics": _make_generic_practice(
            "Outlier diagnostics",
            modes=[
                ("high-influence outlier records", "robust z-score and influence ranking", "observational"),
                ("behavioral deviation from expected patterns", "multivariate anomaly detection review", "observational"),
                ("impossible values or malformed formats", "field-constraint validation", "observational"),
                ("multivariate outlier risk", "combined anomaly and influence evaluation", "observational"),
            ],
            benchmark_key="synthetic",
            evidence_extra=["Structured records, field constraints, confidence scores, model outputs, review labels, and data dictionary."],
            preprocessing_extra=["Validate field types and constraints while preserving impossible values as failures rather than imputing them away."],
            recommendations=["review high-influence outliers before using outputs", "add controls for anomalous behavior patterns", "repair data capture or validation for impossible values", "route severe multivariate outliers to human review or data-quality remediation"],
        ),
        "Correlation analysis": _make_generic_practice(
            "Correlation analysis",
            modes=[
                ("sensitive-proxy feature correlation", "correlation and mutual-association proxy screen", "observational"),
                ("unexplained outcome association", "conditional outcome association review", "observational"),
                ("feature redundancy or leakage", "redundancy and target-leakage diagnostics", "observational"),
                ("proxy correlation risk", "multi-feature proxy risk evaluation", "observational"),
            ],
            benchmark_key="policy",
            evidence_extra=["Feature matrix, outcome labels, sensitive/proxy candidates, feature lineage, timestamps, and model version."],
            preprocessing_extra=["Normalize numeric and categorical encodings and remove target-derived fields only after documenting leakage evidence."],
            recommendations=["review or constrain sensitive proxy features", "document business justification for outcome-associated features", "remove redundant or leaky predictors", "prioritize high-correlation proxies for validation and monitoring"],
        ),
        "Adversarial testing": _make_generic_practice(
            "Adversarial testing",
            modes=[
                ("threshold-boundary evasion", "threshold-boundary perturbation and decision-flip measurement", "controlled"),
                ("known attack-pattern detection loss", "attack-pattern injection and detection-retention analysis", "controlled"),
                ("high-impact-field manipulation sensitivity", "constrained feature manipulation robustness check", "controlled"),
                ("multi-stage adversarial robustness weakness", "coordinated attack-budget evaluation", "controlled"),
            ],
            benchmark_key="synthetic",
            evidence_extra=["Baseline records, baseline predictions, post-perturbation predictions, thresholds, attack labels, scenario severity, and model version."],
            preprocessing_extra=["Pair baseline and attacked records by stable ID and validate attack-budget constraints before scoring."],
            recommendations=["harden decision boundaries and add adversarial regression cases", "improve controls for known attack patterns", "constrain high-impact manipulable fields or add review triggers", "prioritize coordinated attack scenarios by severity and rerun robustness tests"],
        ),
        "AI red teaming": _make_generic_practice(
            "AI red teaming",
            modes=[
                ("abuse paths through the workflow", "structured abuse-path discovery", "controlled"),
                ("policy bypass attempts", "policy-bypass scenario testing", "controlled"),
                ("coordinated attack chain exposure", "multi-step attack-chain simulation", "controlled"),
                ("red-team control gap severity", "severity-weighted red-team evaluation", "controlled"),
            ],
            benchmark_key="synthetic",
            evidence_extra=["Attack scenarios, prompts or records, model responses or decisions, control expectations, policy labels, and reviewer annotations."],
            preprocessing_extra=["Classify attack intent and severity before scoring and preserve full scenario trace for replayability."],
            recommendations=["close exploitable workflow paths and retest", "strengthen policy enforcement for bypass prompts or records", "add controls across coordinated attack stages", "assign mitigation owners for high-severity red-team findings"],
        ),
        "Clustering / anomaly analysis": _make_generic_practice(
            "Clustering / anomaly analysis",
            modes=[
                ("emerging anomalous clusters", "cluster drift and novelty detection", "observational"),
                ("risk concentration inside clusters", "cluster-level failure concentration analysis", "observational"),
                ("novel segment drift", "cluster distribution shift review", "observational"),
                ("cluster-based failure localization weakness", "multi-cluster anomaly localization evaluation", "observational"),
            ],
            benchmark_key="internal",
            evidence_extra=["Feature vectors or embeddings, cluster assignment method, model outputs, timestamps, segment labels, and reviewed failures."],
            preprocessing_extra=["Scale features or embeddings consistently and keep the reference/current cohort split explicit."],
            recommendations=["review emerging clusters before they become blind spots", "target remediation at high-risk clusters", "monitor novel segments with separate thresholds or review", "use cluster findings to localize data or model fixes"],
        ),
        "Time-series diagnostics": _make_generic_practice(
            "Time-series diagnostics",
            modes=[
                ("temporal drift in outputs or errors", "rolling-window drift analysis", "observational"),
                ("seasonality or cycle sensitivity", "seasonality and cycle decomposition review", "observational"),
                ("rolling performance instability", "rolling stability and degradation analysis", "observational"),
                ("time-series stability degradation", "multi-window temporal stability evaluation", "observational"),
            ],
            benchmark_key="internal",
            evidence_extra=["Timestamped predictions, actual outcomes or review labels, window definitions, segment fields, thresholds, and model version."],
            preprocessing_extra=["Sort events by time, validate window boundaries, and avoid smoothing away abrupt failures before analysis."],
            recommendations=["investigate drift windows and recalibrate monitoring", "account for repayment, fraud, or market cycles in validation", "set alerts for rolling degradation", "document temporal failure modes and retest after recalibration"],
        ),
    }
)


def build_diagnostic_spec(ai_system: str, practice: str, test_index: int) -> dict[str, Any]:
    profile = SYSTEM_CONTEXT_PROFILES[ai_system]
    blueprint = deepcopy(PRACTICE_DIAGNOSTIC_BLUEPRINTS[practice][test_index - 1])
    perturbation_text = blueprint["perturbation"].format(**profile)
    return {
        "objective": blueprint["objective"].format(**profile),
        "inputs_required": _standard_inputs(profile, _apply_context(blueprint["inputs"], profile)),
        "preprocessing_steps": _standard_preprocessing(profile, _apply_context(blueprint["preprocessing"], profile)),
        "perturbation_strategy": [perturbation_text],
        "technique": blueprint["technique"],
        "method": _apply_context(blueprint["method"], profile),
        "primary_metrics": blueprint["primary_metrics"],
        "secondary_metrics": blueprint["secondary_metrics"],
        "benchmark_interpretation": blueprint["benchmark"],
        "failure_criteria": blueprint["failure"],
        "recommendation_logic": blueprint["recommendation"],
    }
