import type { WorkflowRun } from "@/schemas/types";

export const demoRun: WorkflowRun = {
  workflow: {
    id: "fraud_adversarial_testing",
    name: "Fraud Detection AI - Adversarial Testing",
    ai_system: "Fraud detection AI",
    pillar: "Risk",
    supporting_practice: "Adversarial testing",
    use_case: "Fraud Detection AI Adversarial Testing",
    orchestration_logic: ["Generate deterministic fraud demo payload", "Run implemented Phase 2C adversarial evaluators", "Return synthetic reference benchmark and report"],
    supported_uploads: ["Synthetic transaction evidence contract"],
    customer_upload_supported: false,
    execution_mode: "synthetic_demo",
    evidence_source: "backend.synthetic_data.generators.generate_fraud_adversarial_payload",
    replay_behavior: "writes replay artifacts during normal workflow runs",
    frontend_routing: "/evaluate?workflow=fraud_adversarial_testing",
    report_template: "standard_health_check",
    implementation_status: "Ready",
    automation_level: "Assisted"
  },
  evaluation: {
    aggregate_score: 58,
    aggregate_risk_level: "High",
    coverage: {
      selected_test_count: 2,
      completed_count: 2,
      insufficient_evidence_count: 0,
      not_implemented_count: 0,
      failed_count: 0,
      score_coverage_percentage: 100
    },
    benchmark_indicator: {eligible: true},
    outputs: [
      {
        score: 55,
        risk_level: "High",
        execution_status: "completed",
        evidence_status: "valid",
        evaluator_id: "phase2c_fraud_adversarial_attack_budget_v1",
        raw_metrics: {severity_weighted_robustness_loss: 0.45},
        metric_interpretation: {severity_weighted_robustness_loss: "Lower is better."},
        sample_size: 30,
        coverage: {records_evaluated: 30, scoreable: true},
        thresholds: {decision_threshold: 0.5},
        findings: ["Adversarial perturbation succeeded near the fraud threshold."],
        insight: "High Risk because adversarial perturbation succeeded near the fraud threshold.",
        recommendation: ["Harden fraud thresholds with adversarial regression tests."],
        limitations: ["Demo data is static and illustrative."],
        execution_metadata: {deterministic: true},
        metadata: {pillar: "Risk", practice: "Adversarial testing", ai_system: "Fraud detection AI", test_type: "strong", test_id: "fraud-detection-ai-adversarial-testing-st1", evaluator_id: "phase2c_fraud_adversarial_attack_budget_v1", diagnostic_family: "adversarial_robustness"}
      },
      {
        score: 64,
        risk_level: "Medium",
        execution_status: "completed",
        evidence_status: "valid",
        evaluator_id: "phase2c_fraud_adversarial_threshold_evasion_v1",
        raw_metrics: {decision_flip_rate: 0.22},
        metric_interpretation: {decision_flip_rate: "Lower is better."},
        sample_size: 30,
        coverage: {records_evaluated: 30, scoreable: true},
        thresholds: {decision_threshold: 0.5},
        findings: ["Threshold instability detected across amount fragmentation scenarios."],
        insight: "Threshold instability detected across amount fragmentation scenarios.",
        recommendation: ["Add secondary review for low-confidence boundary cases."],
        limitations: ["Demo data is static and illustrative."],
        execution_metadata: {deterministic: true},
        metadata: {pillar: "Risk", practice: "Adversarial testing", ai_system: "Fraud detection AI", test_type: "light", test_id: "fraud-detection-ai-adversarial-testing-lt1", evaluator_id: "phase2c_fraud_adversarial_threshold_evasion_v1", diagnostic_family: "adversarial_robustness"}
      }
    ]
  },
  benchmark: {
    metric: "Adversarial Robustness Score",
    score: 58,
    eligible: true,
    reason: null,
    industry_median: 71,
    top_quartile: 84,
    percentile: 30,
    distribution: [42, 51, 58, 63, 68, 71, 76, 80, 84, 89],
    peer_grouping: ["Lendingtech", "Fraud detection AI", "Synthetic Phase 1 demo"],
    provenance: "Internal illustrative synthetic distribution; no empirical industry source.",
    limitations: ["Not an industry benchmark", "Not derived from anonymized customer observations"]
  },
  report: {
    title: "Demo Lendingtech Startup AI Health Check Report",
    scorecard: {aggregate_score: 58, aggregate_risk_level: "High"},
    risk_summary: "Fraud robustness is materially below the illustrative synthetic reference median and vulnerable to threshold evasion.",
    key_weaknesses: [
      "Adversarial perturbations reduced fraud scores below the escalation boundary.",
      "Boundary cases lack a confidence-aware manual review path."
    ],
    recommended_next_steps: [
      "Introduce adversarial fraud scenario testing in release gates.",
      "Strengthen thresholds around transaction fragmentation and night velocity."
    ]
  },
  replay: {replay_id: "demo-replay", path: "backend/evaluations/replays/demo-replay.json"}
};
