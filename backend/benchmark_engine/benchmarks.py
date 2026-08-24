from __future__ import annotations

from collections import defaultdict
from statistics import mean


class InMemoryBenchmarkStore:
    """MVP placeholder for anonymized aggregate metrics.

    Production storage should use PostgreSQL tables and only retain anonymized
    distribution metrics, never raw borrower records or customer text.
    """

    def __init__(self) -> None:
        self._scores: dict[str, list[int]] = defaultdict(list)

    def record(self, distribution_key: str, score: int) -> dict:
        self._scores[distribution_key].append(score)
        values = self._scores[distribution_key]
        return {
            "distribution_key": distribution_key,
            "sample_count": len(values),
            "average_score": round(mean(values)),
            "latest_score": score,
        }

    def snapshot(self) -> dict[str, dict]:
        return {
            key: {"sample_count": len(values), "average_score": round(mean(values))}
            for key, values in self._scores.items()
        }


benchmark_store = InMemoryBenchmarkStore()

