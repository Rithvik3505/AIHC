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
  workflow: WorkflowDefinition;
  evaluation: EvaluationResponse;
  benchmark: {
    metric: string | null;
    score: number | null;
    eligible?: boolean;
    reason?: string | null;
    industry_median?: number;
    top_quartile?: number;
    percentile?: number;
    distribution: number[];
    peer_grouping?: string[];
    provenance?: string;
    limitations?: string[];
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

export type WorkflowDefinition = {
  id: string;
  name: string;
  ai_system: string;
  pillar: string;
  supporting_practice: string;
  use_case: string;
  orchestration_logic: string[];
  supported_uploads: string[];
  customer_upload_supported?: boolean;
  execution_mode?: string;
  evidence_source?: string;
  replay_behavior?: string;
  frontend_routing: string;
  report_template: string;
  implementation_status: string;
  automation_level: string;
};

export type ImplementationMetadata = {
  implementation_status: string;
  workflow_status: string;
  workflow_reference: string;
  evaluator_status: string;
  evaluator_reference: string;
  evidence_type: string;
  dataset_source: string;
  dataset_reference: string;
  benchmark_status: string;
  benchmark_reference: string;
  customer_upload: string;
  automation_level: string;
};

export type TaxonomyTest = {
  id: string;
  name: string;
  test_type: "light" | "strong";
  objective: string;
  inputs_required: string[];
  preprocessing_steps: string[];
  perturbation_strategy: string[];
  technique: string;
  method: string[];
  primary_metrics: string[];
  secondary_metrics: string[];
  benchmark_interpretation: string[];
  failure_criteria: string[];
  recommendation_logic: string[];
  implementation_metadata: ImplementationMetadata;
};

export type TaxonomyUseCase = {
  id: string;
  name: string;
  description: string;
  tests: TaxonomyTest[];
};

export type TaxonomyPractice = {
  name: string;
  category: "A" | "B";
  orientation: "Horizontal" | "Hybrid";
  meaningfulness: Record<string, number>;
  use_cases: TaxonomyUseCase[];
};

export type TaxonomyPillar = {
  name: string;
  practices: TaxonomyPractice[];
};

export type TaxonomySystem = {
  name: string;
  typical_use: string;
  pillars: TaxonomyPillar[];
};

export type TaxonomyRegistry = {
  registry_name: string;
  version: string;
  source_of_truth?: string;
  taxonomy: {
    fintech_segment: string;
    product_phase: string;
    ai_systems: TaxonomySystem[];
  };
};
