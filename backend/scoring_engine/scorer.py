from __future__ import annotations

from statistics import mean

from backend.schemas.models import RiskLevel, TestOutput


def risk_level_for_score(score: int, inverted: bool = False) -> RiskLevel:
    """Map score to risk. Normal scores are health scores where high is good."""
    if inverted:
        if score < 30:
            return RiskLevel.low
        if score <= 60:
            return RiskLevel.medium
        return RiskLevel.high
    if score >= 80:
        return RiskLevel.low
    if score >= 60:
        return RiskLevel.medium
    return RiskLevel.high


def weighted_score(scores: list[tuple[int, float]]) -> int:
    if not scores:
        return 0
    total_weight = sum(weight for _, weight in scores)
    if total_weight == 0:
        return int(mean(score for score, _ in scores))
    return round(sum(score * weight for score, weight in scores) / total_weight)


def aggregate_outputs(outputs: list[TestOutput]) -> tuple[int, RiskLevel]:
    strong_weight = 2.0
    light_weight = 1.0
    score = weighted_score(
        [
            (output.score, strong_weight if output.metadata.test_type.value == "strong" else light_weight)
            for output in outputs
        ]
    )
    return score, risk_level_for_score(score)

