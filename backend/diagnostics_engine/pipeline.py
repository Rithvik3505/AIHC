from __future__ import annotations

from backend.diagnostics_engine.test_specific import evaluate_test
from backend.schemas.models import EvaluationMetadata, EvaluationRequest, EvaluationResponse, TestOutput
from backend.scoring_engine.scorer import aggregate_outputs
from backend.taxonomy_engine.taxonomy import find_use_case


def _dump_model(model: object) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()  # type: ignore[no-any-return]
    if hasattr(model, "dict"):
        return model.dict()  # type: ignore[no-any-return]
    return dict(model)  # type: ignore[arg-type]


def run_evaluation(request: EvaluationRequest) -> EvaluationResponse:
    _, _, practice_item, use_case_item = find_use_case(
        request.ai_system, request.pillar, request.practice, request.use_case
    )
    tests = [
        test for test in use_case_item["tests"] if request.run_strong_test or test["test_type"] == "light"
    ]

    outputs: list[TestOutput] = []
    for test in tests:
        result = evaluate_test(test["id"], request.payload)
        outputs.append(
            TestOutput(
                score=result.score,
                risk_level=result.risk_level,
                execution_status=result.execution_status,
                evidence_status=result.evidence_status,
                evaluator_id=result.evaluator_id,
                raw_metrics=result.raw_metrics,
                metric_interpretation=result.metric_interpretation,
                sample_size=result.sample_size,
                coverage=result.coverage,
                thresholds=result.thresholds,
                findings=result.findings,
                insight=f"{test['name']}: {result.insight}",
                recommendation=result.recommendations,
                limitations=result.limitations,
                execution_metadata=result.execution_metadata,
                metadata=EvaluationMetadata(
                    pillar=request.pillar,
                    practice=request.practice,
                    ai_system=request.ai_system,
                    test_type=test["test_type"],
                    test_id=test["id"],
                    evaluator_id=result.evaluator_id,
                    diagnostic_family=result.execution_metadata.get("family"),
                ),
            )
        )

    aggregate_score, aggregate_risk, coverage = aggregate_outputs(outputs)
    return EvaluationResponse(
        outputs=outputs,
        aggregate_score=aggregate_score,
        aggregate_risk_level=aggregate_risk,
        coverage=coverage,
        benchmark_indicator={
            "eligible": aggregate_score is not None,
            "distribution_key": f"{request.ai_system}|{request.pillar}|{request.practice}|{request.use_case}",
            "meaningfulness_total": practice_item["meaningfulness"],
            "coverage": _dump_model(coverage),
        },
    )
