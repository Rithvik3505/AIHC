from __future__ import annotations

from typing import Any, Callable

from backend.diagnostics_engine import evaluators
from backend.recommendation_engine.recommender import recommendations_for
from backend.schemas.models import EvaluationMetadata, EvaluationRequest, EvaluationResponse, TestOutput
from backend.scoring_engine.scorer import aggregate_outputs, risk_level_for_score
from backend.taxonomy_engine.taxonomy import find_use_case


Evaluator = Callable[[dict[str, Any]], tuple[int, str]]


PRACTICE_EVALUATORS: dict[str, Evaluator] = {
    "Bias mitigation": evaluators.fairness_health,
    "Fairness of model output": evaluators.fairness_health,
    "Correlation analysis": evaluators.fairness_health,
    "Stress testing": evaluators.robustness_health,
    "Adversarial testing": evaluators.robustness_health,
    "AI red teaming": evaluators.robustness_health,
    "Residual analysis": evaluators.residual_health,
    "Time-series diagnostics": evaluators.residual_health,
    "Harmful model output": evaluators.llm_safety_health,
    "Safety of model output": evaluators.llm_safety_health,
    "Data privacy / PII protection": evaluators.llm_safety_health,
    "Model accuracy": evaluators.data_integrity_health,
    "Outlier diagnostics": evaluators.data_integrity_health,
    "Clustering / anomaly analysis": evaluators.data_integrity_health,
    "Model validation": evaluators.governance_health,
    "Human-in-the-loop": evaluators.governance_health,
    "Documentation & compliance checklists": evaluators.governance_health,
    "Feature importance analysis": evaluators.explanation_health,
    "Counterfactual explanations": evaluators.explanation_health,
    "Model transparency": evaluators.explanation_health,
    "Glass box vs black box testing": evaluators.explanation_health,
}


def run_evaluation(request: EvaluationRequest) -> EvaluationResponse:
    _, _, practice_item, use_case_item = find_use_case(
        request.ai_system, request.pillar, request.practice, request.use_case
    )
    evaluator = PRACTICE_EVALUATORS.get(request.practice, evaluators.robustness_health)
    tests = [
        test for test in use_case_item["tests"] if request.run_strong_test or test["test_type"] == "light"
    ]

    outputs: list[TestOutput] = []
    for test in tests:
        base_score, insight = evaluator(request.payload)
        score = min(100, base_score + 4) if test["test_type"] == "light" else base_score
        outputs.append(
            TestOutput(
                score=score,
                risk_level=risk_level_for_score(score),
                insight=f"{test['name']}: {insight}",
                recommendation=recommendations_for(practice_item["name"]),
                metadata=EvaluationMetadata(
                    pillar=request.pillar,
                    practice=request.practice,
                    ai_system=request.ai_system,
                    test_type=test["test_type"],
                ),
            )
        )

    aggregate_score, aggregate_risk = aggregate_outputs(outputs)
    return EvaluationResponse(
        outputs=outputs,
        aggregate_score=aggregate_score,
        aggregate_risk_level=aggregate_risk,
        benchmark_indicator={
            "eligible": True,
            "distribution_key": f"{request.ai_system}|{request.pillar}|{request.practice}|{request.use_case}",
            "meaningfulness_total": practice_item["meaningfulness"],
        },
    )

