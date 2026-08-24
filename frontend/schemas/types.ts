export type RiskLevel = "Low" | "Medium" | "High";

export type TestOutput = {
  score: number;
  risk_level: RiskLevel;
  insight: string;
  recommendation: string[];
  metadata: {
    pillar: string;
    practice: string;
    ai_system: string;
    test_type: "light" | "strong";
  };
};

export type EvaluationResponse = {
  outputs: TestOutput[];
  aggregate_score: number;
  aggregate_risk_level: RiskLevel;
  benchmark_indicator: Record<string, unknown>;
};

export type WorkflowRun = {
  workflow: Record<string, unknown>;
  evaluation: EvaluationResponse;
  benchmark: {
    metric: string;
    score: number;
    industry_median: number;
    top_quartile: number;
    percentile: number;
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
