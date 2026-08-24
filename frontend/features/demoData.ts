import type { WorkflowRun } from "@/schemas/types";

export const demoRun: WorkflowRun = {
  workflow: {
    id: "fraud_adversarial_testing",
    name: "Fraud Detection AI - Adversarial Testing"
  },
  evaluation: {
    aggregate_score: 58,
    aggregate_risk_level: "High",
    benchmark_indicator: {eligible: true},
    outputs: [
      {
        score: 55,
        risk_level: "High",
        insight: "High Risk because adversarial perturbation succeeded near the fraud threshold.",
        recommendation: ["Harden fraud thresholds with adversarial regression tests."],
        metadata: {pillar: "Risk", practice: "Adversarial testing", ai_system: "Fraud detection AI", test_type: "strong"}
      },
      {
        score: 64,
        risk_level: "Medium",
        insight: "Threshold instability detected across amount fragmentation scenarios.",
        recommendation: ["Add secondary review for low-confidence boundary cases."],
        metadata: {pillar: "Risk", practice: "Adversarial testing", ai_system: "Fraud detection AI", test_type: "light"}
      }
    ]
  },
  benchmark: {
    metric: "Adversarial Robustness Score",
    score: 58,
    industry_median: 71,
    top_quartile: 84,
    percentile: 30,
    distribution: [42, 51, 58, 63, 68, 71, 76, 80, 84, 89]
  },
  report: {
    title: "Demo Lendingtech Startup AI Health Check Report",
    scorecard: {aggregate_score: 58, aggregate_risk_level: "High"},
    risk_summary: "Fraud robustness is materially below peer median and vulnerable to threshold evasion.",
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
