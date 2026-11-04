from __future__ import annotations

from enum import Enum
from typing import Any, Literal, get_args, get_origin, get_type_hints

try:
    from pydantic import BaseModel, Field
except ModuleNotFoundError:
    _MISSING = object()

    def Field(default: Any = _MISSING, **kwargs: Any) -> Any:
        if "default_factory" in kwargs:
            return kwargs["default_factory"]()
        return None if default is _MISSING else default

    class BaseModel:
        def __init__(self, **data: Any) -> None:
            hints = get_type_hints(type(self))
            for key, hint in hints.items():
                if key.startswith("_"):
                    continue
                value = data.get(key, getattr(type(self), key, None))
                setattr(self, key, self._coerce(hint, value))

        @classmethod
        def parse_obj(cls, payload: dict[str, Any]) -> "BaseModel":
            return cls(**payload)

        @classmethod
        def model_validate(cls, payload: dict[str, Any]) -> "BaseModel":
            return cls(**payload)

        def dict(self) -> dict[str, Any]:
            return {key: self._dump(value) for key, value in self.__dict__.items()}

        @classmethod
        def _coerce(cls, hint: Any, value: Any) -> Any:
            origin = get_origin(hint)
            args = get_args(hint)
            if origin is list and args and isinstance(value, list):
                return [cls._coerce(args[0], item) for item in value]
            if origin is dict and isinstance(value, dict):
                return value
            if origin is Literal:
                return value
            if isinstance(hint, type) and issubclass(hint, Enum):
                return value if isinstance(value, hint) else hint(value)
            if isinstance(hint, type) and issubclass(hint, BaseModel) and isinstance(value, dict):
                return hint(**value)
            return value

        @classmethod
        def _dump(cls, value: Any) -> Any:
            if isinstance(value, BaseModel):
                return value.dict()
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, list):
                return [cls._dump(item) for item in value]
            if isinstance(value, dict):
                return {key: cls._dump(item) for key, item in value.items()}
            return value


class RiskLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class TestKind(str, Enum):
    light = "light"
    strong = "strong"


class ExecutionStatus(str, Enum):
    completed = "completed"
    insufficient_evidence = "insufficient_evidence"
    not_implemented = "not_implemented"
    failed = "failed"


class EvidenceStatus(str, Enum):
    valid = "valid"
    missing = "missing"
    malformed = "malformed"
    insufficient = "insufficient"
    not_applicable = "not_applicable"


class EvidenceMode(str, Enum):
    demo = "demo"
    manual = "manual"
    upload = "upload"


class MeaningfulnessScore(BaseModel):
    risk_criticality: int = Field(ge=0, le=5)
    founder_pain: int = Field(ge=0, le=5)
    investor_reputational_importance: int = Field(ge=0, le=5)
    benchmark_density_potential: int = Field(ge=0, le=5)
    technical_signal_strength: int = Field(ge=0, le=5)
    mvp_feasibility: int = Field(ge=0, le=5)

    @property
    def total(self) -> int:
        return sum(
            [
                self.risk_criticality,
                self.founder_pain,
                self.investor_reputational_importance,
                self.benchmark_density_potential,
                self.technical_signal_strength,
                self.mvp_feasibility,
            ]
        )


class ImplementationMetadata(BaseModel):
    implementation_status: str
    workflow_status: str
    workflow_reference: str
    evaluator_status: str
    evaluator_reference: str
    evidence_type: str
    dataset_source: str
    dataset_reference: str
    benchmark_status: str
    benchmark_reference: str
    customer_upload: str
    automation_level: str


class TestDefinition(BaseModel):
    id: str
    name: str
    test_type: TestKind
    objective: str
    inputs_required: list[str]
    preprocessing_steps: list[str]
    perturbation_strategy: list[str]
    technique: str
    method: list[str]
    primary_metrics: list[str]
    secondary_metrics: list[str]
    benchmark_interpretation: list[str]
    failure_criteria: list[str]
    recommendation_logic: list[str]
    implementation_metadata: ImplementationMetadata


class UseCaseDefinition(BaseModel):
    id: str
    name: str
    description: str
    tests: list[TestDefinition]


class PracticeDefinition(BaseModel):
    name: str
    category: Literal["A", "B"]
    orientation: Literal["Horizontal", "Hybrid", "Vertical"] = "Horizontal"
    meaningfulness: MeaningfulnessScore
    use_cases: list[UseCaseDefinition]


class PillarDefinition(BaseModel):
    name: str
    practices: list[PracticeDefinition]


class AISystemDefinition(BaseModel):
    name: str
    typical_use: str
    pillars: list[PillarDefinition]


class TaxonomyDefinition(BaseModel):
    fintech_segment: Literal["Lendingtech"]
    product_phase: Literal["Assisted Intelligence MVP"]
    ai_systems: list[AISystemDefinition]


class EvaluationMetadata(BaseModel):
    pillar: str
    practice: str
    ai_system: str
    test_type: TestKind
    test_id: str | None = None
    evaluator_id: str | None = None
    diagnostic_family: str | None = None


class EvaluationCoverage(BaseModel):
    selected_test_count: int = 0
    completed_count: int = 0
    insufficient_evidence_count: int = 0
    not_implemented_count: int = 0
    failed_count: int = 0
    score_coverage_percentage: float = 0.0


class TestOutput(BaseModel):
    score: int | None = Field(default=None, ge=0, le=100)
    risk_level: RiskLevel | None = None
    execution_status: ExecutionStatus = ExecutionStatus.completed
    evidence_status: EvidenceStatus = EvidenceStatus.valid
    evaluator_id: str | None = None
    raw_metrics: dict[str, Any] = Field(default_factory=dict)
    metric_interpretation: dict[str, str] = Field(default_factory=dict)
    sample_size: int | None = None
    coverage: dict[str, Any] = Field(default_factory=dict)
    thresholds: dict[str, Any] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)
    insight: str
    recommendation: list[str]
    limitations: list[str] = Field(default_factory=list)
    execution_metadata: dict[str, Any] = Field(default_factory=dict)
    metadata: EvaluationMetadata


class EvaluationRequest(BaseModel):
    ai_system: str
    pillar: str
    practice: str
    use_case: str
    payload: dict[str, Any] = Field(default_factory=dict)
    run_strong_test: bool = True
    selected_test_ids: list[str] = Field(default_factory=list)


class WorkflowRunRequest(BaseModel):
    evidence_mode: EvidenceMode = EvidenceMode.demo
    payload: dict[str, Any] | None = None
    selected_test_ids: list[str] = Field(default_factory=list)


class WorkflowValidationRequest(BaseModel):
    evidence_mode: EvidenceMode = EvidenceMode.manual
    payload: dict[str, Any] = Field(default_factory=dict)
    selected_test_ids: list[str] = Field(default_factory=list)


class EvaluationResponse(BaseModel):
    outputs: list[TestOutput]
    aggregate_score: int | None = Field(default=None, ge=0, le=100)
    aggregate_risk_level: RiskLevel | None = None
    coverage: EvaluationCoverage = Field(default_factory=EvaluationCoverage)
    benchmark_indicator: dict[str, Any]


class ReportRequest(BaseModel):
    evaluation: EvaluationResponse
    company_name: str | None = None


class ReportResponse(BaseModel):
    title: str
    scorecard: dict[str, Any]
    risk_summary: str
    key_weaknesses: list[str]
    recommended_next_steps: list[str]
