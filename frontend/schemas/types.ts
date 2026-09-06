export type RiskLevel = "Low" | "Medium" | "High";
export type ExecutionStatus = "completed" | "insufficient_evidence" | "not_implemented" | "failed";
export type EvidenceStatus = "valid" | "missing" | "malformed" | "insufficient" | "not_applicable";

export type TestOutput = {
  score: number | null;
  risk_level: RiskLevel | null;
  execution_status: ExecutionStatus;
  evidence_status: EvidenceStatus;
  evaluator_id: string | null;
  raw_metrics: Record<string, unknown>;
  metric_interpretation: Record<string, string>;
  sample_size: number | null;
  coverage: Record<string, unknown>;
  thresholds: Record<string, unknown>;
  findings: string[];
  insight: string;
  recommendation: string[];
  limitations: string[];
  execution_metadata: Record<string, unknown>;
  metadata: {
    pillar: string;
    practice: string;
    ai_system: string;
    test_type: "light" | "strong";
    test_id?: string | null;
    evaluator_id?: string | null;
    diagnostic_family?: string | null;
  };
};

export type EvaluationCoverage = {
  selected_test_count: number;
  completed_count: number;
  insufficient_evidence_count: number;
  not_implemented_count: number;
  failed_count: number;
  score_coverage_percentage: number;
};

export type EvaluationResponse = {
  outputs: TestOutput[];
  aggregate_score: number | null;
  aggregate_risk_level: RiskLevel | null;
  coverage: EvaluationCoverage;
  benchmark_indicator: Record<string, unknown>;
};

export type WorkflowRun = {
  workflow: Record<string, unknown>;
  evaluation: EvaluationResponse;
  benchmark: {
    metric: string;
    score: number | null;
    industry_median?: number;
    top_quartile?: number;
    percentile?: number;
    distribution: number[];
  };
  report: {
    title: string;
    scorecard: Record<string, unknown>;
    risk_summary: string;
    key_weaknesses: string[];
    recommended_next_steps: string[];
  };
  replay: {
    replay_id: string;
    path: string;
  };
};
