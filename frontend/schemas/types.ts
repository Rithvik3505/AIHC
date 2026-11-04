export type RiskLevel = "Low" | "Medium" | "High";
export type ExecutionStatus = "completed" | "insufficient_evidence" | "not_implemented" | "failed";
export type EvidenceStatus = "valid" | "missing" | "malformed" | "insufficient" | "not_applicable";
export type EvidenceMode = "demo" | "manual" | "upload";

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
  evidence_mode: EvidenceMode;
  validation: EvidenceValidation;
  evaluation: EvaluationResponse;
  benchmark: {
    benchmark_id?: string | null;
    benchmark_type?: string | null;
    metric: string | null;
    score: number | null;
    eligible?: boolean;
    reason?: string | null;
    synthetic_reference_median?: number | null;
    synthetic_reference_top_quartile?: number | null;
    synthetic_percentile?: number | null;
    distribution: number[];
    peer_grouping?: string[];
    provenance?: string;
    limitations?: string[];
    normalization_method?: string | null;
    external_reference_status?: string;
    external_references?: BenchmarkReference[];
    industry_peer_distribution?: {available: boolean; reason: string};
  };
  report: {
    title: string;
    scorecard: Record<string, unknown>;
    risk_summary: string;
    key_weaknesses: string[];
    recommended_next_steps: string[];
  };
  replay: {
    replay_id: string | null;
    path: string | null;
    persisted: boolean;
    reason: string;
  };
};

export type BenchmarkReference = {
  id: string;
  name: string;
  benchmark_type: string;
  metric: string;
  source: string;
  source_url: string | null;
  publication: string;
  publication_date: string | null;
  version: string;
  applicability: string;
  limitations: string[];
  empirical: boolean;
};

export type EvidenceField = {
  key: string;
  label: string;
  type: "text" | "textarea" | "number" | "binary" | "boolean" | "list" | "select" | "json";
  description: string;
  required_for: string[];
  options: string[];
  minimum: number | null;
  maximum: number | null;
};

export type WorkflowTestContract = {
  id: string;
  name: string;
  test_type: "light" | "strong";
  purpose: string;
  required_evidence: string[];
};

export type EvidenceContract = {
  workflow_id: string;
  workflow_name: string;
  supported_formats: string[];
  record_fields: EvidenceField[];
  top_level_fields: EvidenceField[];
  tests: WorkflowTestContract[];
  example_payload: Record<string, unknown>;
  limits: {
    maximum_file_bytes: number;
    maximum_records: number;
    maximum_prompt_or_response_characters: number;
  };
  privacy: {processing: string; replay: string; benchmark: string};
  raw_document_upload: {supported: boolean; status: string; reason: string};
};

export type EvidenceIssue = {
  message: string;
  field: string | null;
  row: number | null;
  severity: "error" | "warning";
  fatal: boolean;
};

export type TestEvidenceStatus = {
  test_id: string;
  test_name: string;
  test_type: "light" | "strong";
  status: "Ready" | "Missing evidence" | "Invalid evidence" | "Insufficient sample" | "Optional evidence unavailable";
  evidence_status: EvidenceStatus;
  message: string;
  required_evidence: string[];
};

export type EvidenceValidation = {
  workflow_id: string;
  can_run: boolean;
  normalized_payload: Record<string, unknown>;
  issues: EvidenceIssue[];
  tests: TestEvidenceStatus[];
  limits: EvidenceContract["limits"];
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
  supported_evidence_modes?: EvidenceMode[];
  execution_mode?: string;
  evidence_source?: string;
  replay_behavior?: string;
  raw_document_upload_supported?: boolean;
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
