from __future__ import annotations

from backend.schemas.models import EvaluationResponse, ReportResponse


def generate_report(evaluation: EvaluationResponse, company_name: str | None = None) -> ReportResponse:
    high_risk = [output for output in evaluation.outputs if output.risk_level.value == "High"]
    weakest = sorted(evaluation.outputs, key=lambda item: item.score)[:3]
    name = company_name or "Startup"
    pillar_scores: dict[str, list[int]] = {}
    for output in evaluation.outputs:
        pillar_scores.setdefault(output.metadata.pillar, []).append(output.score)
    pillar_summary = {
        pillar: round(sum(scores) / len(scores))
        for pillar, scores in pillar_scores.items()
        if scores
    }
    why = [
        f"{output.metadata.practice}: {output.insight}"
        for output in weakest
    ]
    return ReportResponse(
        title=f"{name} AI Health Check Report",
        scorecard={
            "aggregate_score": evaluation.aggregate_score,
            "aggregate_risk_level": evaluation.aggregate_risk_level.value,
            "tests_run": len(evaluation.outputs),
            "pillar_scores": pillar_summary,
            "why_this_score_happened": why,
            "benchmark": evaluation.benchmark_indicator,
        },
        risk_summary=(
            f"Overall AI health score is {evaluation.aggregate_score}/100 "
            f"with {evaluation.aggregate_risk_level.value.lower()} aggregate risk."
        ),
        key_weaknesses=[item.insight for item in weakest],
        recommended_next_steps=[
            recommendation
            for output in (high_risk or weakest)
            for recommendation in output.recommendation[:1]
        ][:5],
    )
