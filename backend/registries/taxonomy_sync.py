from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.schemas.models import TaxonomyDefinition
from backend.taxonomy_engine.taxonomy import load_taxonomy


REGISTRY_PATH = Path(__file__).resolve().parent / "taxonomy_registry.json"

REGISTRY_ENVELOPE: dict[str, Any] = {
    "registry_name": "ai_health_check_lendingtech_taxonomy",
    "version": "0.4.0",
    "fintech_segment": "Lendingtech",
    "source_of_truth": "backend/taxonomy_engine/taxonomy.py",
    "hierarchy": [
        "fintech_segment",
        "ai_system",
        "pillar",
        "supporting_practice",
        "use_case",
        "tests",
    ],
    "meaningfulness_heuristic": [
        "risk_criticality",
        "founder_pain",
        "investor_reputational_importance",
        "benchmark_density_potential",
        "technical_signal_strength",
        "mvp_feasibility",
    ],
    "test_contract": {
        "id": "string",
        "name": "string",
        "test_type": "light | strong",
        "objective": "string",
        "inputs_required": "list[string]",
        "preprocessing_steps": "list[string]",
        "perturbation_strategy": "list[string]",
        "technique": "string",
        "method": "list[string]",
        "primary_metrics": "list[string]",
        "secondary_metrics": "list[string]",
        "benchmark_interpretation": "list[string]",
        "failure_criteria": "list[string]",
        "recommendation_logic": "list[string]",
        "implementation_metadata": {
            "implementation_status": "Ready | Partial | Planned",
            "workflow_status": "Implemented | Planned",
            "workflow_reference": "workflow_registry:<id> | workflow_registry:planned",
            "evaluator_status": "Implemented | Planned",
            "evaluator_reference": "evaluator registry name",
            "evidence_type": "string",
            "dataset_source": "string",
            "dataset_reference": "dataset_registry:<id>",
            "benchmark_status": "Available | Planned",
            "benchmark_reference": "benchmark_registry:<id> | benchmark_registry:planned",
            "customer_upload": "Supported | Planned",
            "automation_level": "Automated | Assisted",
        },
    },
}


class TaxonomyRegistryDriftError(RuntimeError):
    pass


def _model_to_jsonable(model: TaxonomyDefinition) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return json.loads(json.dumps(model.dict()))


def _validate_taxonomy(payload: dict[str, Any]) -> TaxonomyDefinition:
    if hasattr(TaxonomyDefinition, "model_validate"):
        return TaxonomyDefinition.model_validate(payload)
    return TaxonomyDefinition.parse_obj(payload)


def build_taxonomy_registry() -> dict[str, Any]:
    taxonomy = load_taxonomy()
    _validate_taxonomy(_model_to_jsonable(taxonomy))
    return {**REGISTRY_ENVELOPE, "taxonomy": _model_to_jsonable(taxonomy)}


def serialize_registry(registry: dict[str, Any]) -> str:
    return json.dumps(registry, indent=2, ensure_ascii=False) + "\n"


def expected_registry_text() -> str:
    return serialize_registry(build_taxonomy_registry())


def write_registry(path: Path = REGISTRY_PATH) -> None:
    expected = expected_registry_text()
    temp_path = path.with_name(f"{path.name}.tmp")
    temp_path.write_text(expected, encoding="utf-8")
    temp_path.replace(path)
    validate_registry_file(path)


def validate_registry_file(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    taxonomy_payload = payload.get("taxonomy")
    if not isinstance(taxonomy_payload, dict):
        raise ValueError(f"{path} does not contain a taxonomy object")
    _validate_taxonomy(taxonomy_payload)
    return payload


def check_registry(path: Path = REGISTRY_PATH) -> None:
    expected = expected_registry_text()
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        raise TaxonomyRegistryDriftError(
            f"{path} is out of sync with backend/taxonomy_engine/taxonomy.py. "
            "Run: python scripts/sync_taxonomy_registry.py --write"
        )
    validate_registry_file(path)
