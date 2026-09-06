from __future__ import annotations

from backend.schemas.models import EvaluationResponse, ReportResponse


def generate_report(evaluation: EvaluationResponse, company_name: str | None = None) -> ReportResponse:
    scored_outputs = [output for output in evaluation.outputs if output.score is not None]
    high_risk = [output for output in scored_outputs if output.risk_level and output.risk_level.value == "High"]
    weakest = sorted(scored_outputs, key=lambda item: item.score or 101)[:3]
    unassessable = [output for output in evaluation.outputs if output.score is None]
    name = company_name or "Startup"
    pillar_scores: dict[str, list[int]] = {}
    for output in scored_outputs:
        if output.score is not None:
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
            "aggregate_risk_level": evaluation.aggregate_risk_level.value if evaluation.aggregate_risk_level else None,
            "tests_run": len(evaluation.outputs),
            "coverage": evaluation.coverage.dict(),
            "pillar_scores": pillar_summary,
            "why_this_score_happened": why,
            "benchmark": evaluation.benchmark_indicator,
        },
        risk_summary=(
            f"Overall AI health score is {evaluation.aggregate_score}/100 "
            f"with {evaluation.aggregate_risk_level.value.lower()} aggregate risk."
            if evaluation.aggregate_score is not None and evaluation.aggregate_risk_level
            else "No aggregate AI health score is available because no selected tests were assessable."
        ),
        key_weaknesses=[item.insight for item in weakest] + [item.insight for item in unassessable[:2]],
        recommended_next_steps=[
            recommendation
            for output in (high_risk or weakest)
            for recommendation in output.recommendation[:1]
        ][:5] or [recommendation for output in unassessable for recommendation in output.recommendation[:1]][:5],
    )
