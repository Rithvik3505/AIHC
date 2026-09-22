from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from backend.registries.loader import load_registry
from backend.registries.taxonomy_sync import build_taxonomy_registry
from backend.schemas.models import TaxonomyDefinition
from backend.diagnostics_engine.test_specific import EVALUATOR_CONFIGS
from backend.taxonomy_engine.diagnostic_specs import SYSTEM_CONTEXT_PROFILES
from backend.taxonomy_engine.taxonomy import load_taxonomy


EXPECTED_COUNTS = {
    "ai_systems": 8,
    "use_cases": 130,
    "tests": 520,
    "light_tests": 390,
    "strong_tests": 130,
    "supporting_practices": 21,
    "category_a_use_cases": 104,
    "category_b_use_cases": 26,
}

EXPECTED_PILLARS = ["Risk", "Reliability", "Data Integrity", "Explainability", "Governance"]
EXPECTED_IDENTITY_FINGERPRINT = "d7f9f041248661a6e1bc551c824d9c82bd6668518b5ebca266d1e08fad905b9f"

NORMALIZED_TEST_FIELDS = {
    "id",
    "name",
    "test_type",
    "objective",
    "inputs_required",
    "preprocessing_steps",
    "perturbation_strategy",
    "technique",
    "method",
    "primary_metrics",
    "secondary_metrics",
    "benchmark_interpretation",
    "failure_criteria",
    "recommendation_logic",
    "implementation_metadata",
}


def _model_to_jsonable(taxonomy: TaxonomyDefinition) -> dict[str, Any]:
    if hasattr(taxonomy, "model_dump"):
        return taxonomy.model_dump(mode="json")
    return json.loads(json.dumps(taxonomy.dict()))


def _validate_model(payload: dict[str, Any]) -> TaxonomyDefinition:
    if hasattr(TaxonomyDefinition, "model_validate"):
        return TaxonomyDefinition.model_validate(payload)
    return TaxonomyDefinition.parse_obj(payload)


def _dump_model(model: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return model.dict()


def _iter_taxonomy(taxonomy: TaxonomyDefinition):
    for system_index, system in enumerate(taxonomy.ai_systems):
        for pillar_index, pillar in enumerate(system.pillars):
            for practice_index, practice in enumerate(pillar.practices):
                for use_case_index, use_case in enumerate(practice.use_cases):
                    yield system_index, system, pillar_index, pillar, practice_index, practice, use_case_index, use_case


def taxonomy_counts(taxonomy: TaxonomyDefinition | None = None) -> dict[str, Any]:
    taxonomy = taxonomy or load_taxonomy()
    categories: Counter[str] = Counter()
    orientations: Counter[str] = Counter()
    tests_per_use_case: Counter[int] = Counter()
    pillars: list[str] = []
    practices: set[str] = set()
    tests = []
    for _, system, _, pillar, _, practice, _, use_case in _iter_taxonomy(taxonomy):
        pillars.append(pillar.name)
        practices.add(practice.name)
        categories[practice.category] += 1
        orientations[practice.orientation] += 1
        tests_per_use_case[len(use_case.tests)] += 1
        tests.extend(use_case.tests)
    return {
        "ai_systems": len(taxonomy.ai_systems),
        "use_cases": sum(tests_per_use_case.values()),
        "tests": len(tests),
        "light_tests": sum(test.test_type.value == "light" for test in tests),
        "strong_tests": sum(test.test_type.value == "strong" for test in tests),
        "supporting_practices": len(practices),
        "category_a_use_cases": categories["A"],
        "category_b_use_cases": categories["B"],
        "categories": dict(categories),
        "orientations": dict(orientations),
        "tests_per_use_case": dict(tests_per_use_case),
        "pillars": pillars,
    }


def identity_payload(taxonomy: TaxonomyDefinition | None = None) -> list[dict[str, Any]]:
    taxonomy = taxonomy or load_taxonomy()
    payload = []
    for system_index, system, pillar_index, pillar, practice_index, practice, use_case_index, use_case in _iter_taxonomy(taxonomy):
        payload.append(
            {
                "system_index": system_index,
                "ai_system": system.name,
                "pillar_index": pillar_index,
                "pillar": pillar.name,
                "practice_index": practice_index,
                "practice": practice.name,
                "category": practice.category,
                "orientation": practice.orientation,
                "use_case_index": use_case_index,
                "use_case_id": use_case.id,
                "use_case_name": use_case.name,
                "tests": [
                    {
                        "index": test_index,
                        "id": test.id,
                        "name": test.name,
                        "test_type": test.test_type.value,
                    }
                    for test_index, test in enumerate(use_case.tests)
                ],
            }
        )
    return payload


def identity_fingerprint(taxonomy: TaxonomyDefinition | None = None) -> str:
    encoded = json.dumps(identity_payload(taxonomy), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_taxonomy_contract(taxonomy: TaxonomyDefinition | None = None) -> list[str]:
    taxonomy = taxonomy or load_taxonomy()
    issues: list[str] = []
    counts = taxonomy_counts(taxonomy)
    for key, expected in EXPECTED_COUNTS.items():
        if counts[key] != expected:
            issues.append(f"{key}: expected {expected}, found {counts[key]}")
    if counts["tests_per_use_case"] != {4: 130}:
        issues.append(f"tests_per_use_case: expected {{4: 130}}, found {counts['tests_per_use_case']}")
    for _, _, _, _, _, _, _, use_case in _iter_taxonomy(taxonomy):
        kinds = Counter(test.test_type.value for test in use_case.tests)
        if kinds != {"light": 3, "strong": 1}:
            issues.append(f"{use_case.id}: expected 3 light and 1 strong test, found {dict(kinds)}")
    if set(counts["categories"]) != {"A", "B"}:
        issues.append(f"categories: expected only A and B, found {sorted(counts['categories'])}")
    if set(counts["orientations"]) != {"Horizontal", "Hybrid"}:
        issues.append(f"orientations: expected only Horizontal and Hybrid, found {sorted(counts['orientations'])}")
    if "Data" in counts["pillars"] or "Data Integrity" not in counts["pillars"]:
        issues.append("pillar names must include Data Integrity and must not rename it to Data")
    if any(pillar not in EXPECTED_PILLARS for pillar in counts["pillars"]):
        issues.append(f"pillar names: found unexpected pillar in {sorted(set(counts['pillars']))}")
    if identity_fingerprint(taxonomy) != EXPECTED_IDENTITY_FINGERPRINT:
        issues.append("identity fingerprint changed; taxonomy identities, ordering, or hierarchy drifted")
    use_case_ids = [item["use_case_id"] for item in identity_payload(taxonomy)]
    test_ids = [test["id"] for item in identity_payload(taxonomy) for test in item["tests"]]
    if len(use_case_ids) != len(set(use_case_ids)):
        issues.append("use-case IDs are not unique")
    if len(test_ids) != len(set(test_ids)):
        issues.append("test IDs are not unique")
    return issues


def validate_normalized_schema(taxonomy: TaxonomyDefinition | None = None) -> list[str]:
    taxonomy = taxonomy or load_taxonomy()
    issues: list[str] = []
    _validate_model(_model_to_jsonable(taxonomy))
    for _, _, _, _, _, _, _, use_case in _iter_taxonomy(taxonomy):
        for test in use_case.tests:
            test_payload = json.loads(json.dumps(_dump_model(test)))
            missing = NORMALIZED_TEST_FIELDS - set(test_payload)
            if missing:
                issues.append(f"{test.id}: missing normalized fields {sorted(missing)}")
            if "metrics" in test_payload:
                issues.append(f"{test.id}: legacy metrics field is still serialized")
            for key in NORMALIZED_TEST_FIELDS - {"id", "name", "test_type", "objective", "technique", "implementation_metadata"}:
                if not isinstance(test_payload.get(key), list):
                    issues.append(f"{test.id}: {key} must be a list")
            if not isinstance(test_payload.get("technique"), str):
                issues.append(f"{test.id}: technique must be a string")
            if not isinstance(test_payload.get("implementation_metadata"), dict):
                issues.append(f"{test.id}: implementation_metadata must be an object")
    return issues


def validate_registry_sync(registry_path: Path | None = None) -> list[str]:
    expected = build_taxonomy_registry()
    if registry_path is None:
        actual = load_registry("taxonomy_registry.json")
    else:
        actual = json.loads(registry_path.read_text(encoding="utf-8"))
    issues: list[str] = []
    if actual != expected:
        issues.append("taxonomy registry differs from deterministic exporter output")
    try:
        _validate_model(actual["taxonomy"])
    except Exception as exc:
        issues.append(f"registry taxonomy failed Pydantic validation: {exc}")
    return issues


def _reference_id(value: str, prefix: str) -> str | None:
    planned = f"{prefix}:planned"
    if value == planned:
        return None
    marker = f"{prefix}:"
    if value.startswith(marker):
        return value.removeprefix(marker)
    return value


def validate_registry_references(taxonomy: TaxonomyDefinition | None = None) -> list[str]:
    taxonomy = taxonomy or load_taxonomy()
    evaluators = load_registry("evaluator_registry.json")["evaluators"]
    workflows = load_registry("workflow_registry.json")["workflows"]
    datasets = load_registry("dataset_registry.json")["datasets"]
    benchmarks = load_registry("benchmark_registry.json")["benchmarks"]
    evaluator_names = {item["name"] for item in evaluators}
    evaluator_ids = {item["id"] for item in evaluators}
    workflow_ids = {item["id"] for item in workflows}
    dataset_ids = {item["id"] for item in datasets}
    benchmark_ids = {item["id"] for item in benchmarks}
    issues: list[str] = []
    for _, _, _, _, _, _, _, use_case in _iter_taxonomy(taxonomy):
        for test in use_case.tests:
            metadata = test.implementation_metadata
            workflow_id = _reference_id(metadata.workflow_reference, "workflow_registry")
            if workflow_id and workflow_id not in workflow_ids:
                issues.append(f"{test.id}: missing workflow reference {metadata.workflow_reference}")
            dataset_id = _reference_id(metadata.dataset_reference, "dataset_registry")
            if dataset_id and dataset_id not in dataset_ids:
                issues.append(f"{test.id}: missing dataset reference {metadata.dataset_reference}")
            benchmark_id = _reference_id(metadata.benchmark_reference, "benchmark_registry")
            if benchmark_id and benchmark_id not in benchmark_ids:
                issues.append(f"{test.id}: missing benchmark reference {metadata.benchmark_reference}")
            evaluator_id = _reference_id(metadata.evaluator_reference, "evaluator_registry")
            evaluator_found = metadata.evaluator_reference in evaluator_names or bool(evaluator_id and evaluator_id in evaluator_ids)
            if not evaluator_found:
                issues.append(f"{test.id}: missing evaluator reference {metadata.evaluator_reference}")
            if metadata.implementation_status == "Ready":
                if workflow_id is None:
                    issues.append(f"{test.id}: Ready test has placeholder workflow reference")
                if not evaluator_found:
                    issues.append(f"{test.id}: Ready test has absent evaluator reference")
                if dataset_id is None:
                    issues.append(f"{test.id}: Ready test has placeholder dataset reference")
                if benchmark_id is None:
                    issues.append(f"{test.id}: Ready test has placeholder benchmark reference")
    return issues


def validate_phase2d_registry_truth(taxonomy: TaxonomyDefinition | None = None) -> list[str]:
    taxonomy = taxonomy or load_taxonomy()
    workflows = load_registry("workflow_registry.json")["workflows"]
    datasets = load_registry("dataset_registry.json")["datasets"]
    benchmarks = load_registry("benchmark_registry.json")["benchmarks"]
    evaluators = load_registry("evaluator_registry.json")["evaluators"]
    issues: list[str] = []

    workflow_by_id = {workflow["id"]: workflow for workflow in workflows}
    evaluator_by_id = {evaluator["id"]: evaluator for evaluator in evaluators}
    benchmark_by_id = {benchmark["id"]: benchmark for benchmark in benchmarks}
    dataset_by_id = {dataset["id"]: dataset for dataset in datasets}
    implemented_test_ids = set(EVALUATOR_CONFIGS)
    implemented_evaluator_ids = {config.evaluator_id for config in EVALUATOR_CONFIGS.values()}

    for evaluator_id in implemented_evaluator_ids:
        if evaluator_id not in evaluator_by_id:
            issues.append(f"Phase 2C router evaluator {evaluator_id} is missing from evaluator_registry")
    for evaluator in evaluators:
        supported_test_ids = evaluator.get("supported_test_ids", [])
        if evaluator.get("implementation_status") == "Implemented":
            if evaluator["id"] not in implemented_evaluator_ids:
                issues.append(f"{evaluator['id']}: registry marks evaluator implemented but router does not expose it")
            for test_id in supported_test_ids:
                if test_id not in implemented_test_ids:
                    issues.append(f"{evaluator['id']}: supported_test_id {test_id} is not exposed by the router")

    for workflow in workflows:
        if workflow.get("customer_upload_supported") is not False:
            issues.append(f"{workflow['id']}: workflow must not claim customer upload support in Phase 2D")
        if workflow.get("execution_mode") != "synthetic_demo":
            issues.append(f"{workflow['id']}: workflow execution_mode must be synthetic_demo")
        if "synthetic_data.generators" not in str(workflow.get("evidence_source", "")):
            issues.append(f"{workflow['id']}: workflow evidence_source must point to synthetic data generators")
        if "write" not in str(workflow.get("replay_behavior", "")).lower():
            issues.append(f"{workflow['id']}: workflow replay_behavior must disclose replay writes")

    customer_dataset = dataset_by_id.get("customer_dataset")
    if customer_dataset:
        if customer_dataset.get("customer_upload_supported") is not False:
            issues.append("customer_dataset must disclose customer_upload_supported false")
        if customer_dataset.get("availability_status") != "planned_contract_only":
            issues.append("customer_dataset must remain planned_contract_only")
        if customer_dataset.get("ingestion_method") != "not_implemented":
            issues.append("customer_dataset ingestion_method must remain not_implemented")

    for benchmark in benchmarks:
        if benchmark.get("benchmark_type") != "illustrative_synthetic_reference":
            issues.append(f"{benchmark['id']}: benchmark_type must be illustrative_synthetic_reference")
        provenance = str(benchmark.get("provenance", "")).lower()
        if "no empirical industry source" not in provenance:
            issues.append(f"{benchmark['id']}: benchmark provenance must deny empirical industry sourcing")
        if benchmark.get("sample_size") != len(benchmark.get("synthetic_benchmark_distribution", [])):
            issues.append(f"{benchmark['id']}: sample_size must equal synthetic distribution length")

    taxonomy_test_ids = {test["id"] for item in identity_payload(taxonomy) for test in item["tests"]}
    for test_id, config in EVALUATOR_CONFIGS.items():
        if test_id not in taxonomy_test_ids:
            issues.append(f"{test_id}: router exposes a test_id absent from taxonomy")
        if config.evaluator_id not in evaluator_by_id:
            issues.append(f"{test_id}: router evaluator {config.evaluator_id} absent from registry")

    for _, _, _, _, _, _, _, use_case in _iter_taxonomy(taxonomy):
        for test in use_case.tests:
            metadata = test.implementation_metadata
            if metadata.customer_upload != "Not supported":
                issues.append(f"{test.id}: taxonomy metadata must not claim customer upload support")
            evaluator_id = _reference_id(metadata.evaluator_reference, "evaluator_registry")
            if test.id in implemented_test_ids:
                config = EVALUATOR_CONFIGS[test.id]
                if metadata.evaluator_status != "Implemented":
                    issues.append(f"{test.id}: routed test must disclose an implemented evaluator")
                if evaluator_id != config.evaluator_id:
                    issues.append(f"{test.id}: taxonomy evaluator reference {metadata.evaluator_reference} does not match router {config.evaluator_id}")
            elif metadata.implementation_status in {"Ready", "Implemented"} or metadata.evaluator_status == "Implemented":
                issues.append(f"{test.id}: taxonomy marks executable support but no Phase 2C evaluator is routed")

            workflow_id = _reference_id(metadata.workflow_reference, "workflow_registry")
            if workflow_id:
                if workflow_id not in workflow_by_id:
                    issues.append(f"{test.id}: missing workflow reference {metadata.workflow_reference}")

            benchmark_id = _reference_id(metadata.benchmark_reference, "benchmark_registry")
            if benchmark_id and benchmark_id not in benchmark_by_id:
                issues.append(f"{test.id}: missing benchmark reference {metadata.benchmark_reference}")

    return issues


REQUIRED_BENCHMARK_MARKERS = {
    "illustrative synthetic reference distributions",
    "customer-internal historical baseline",
    "challenger baseline",
    "policy-defined tolerance",
    "configured MVP default",
    "public-dataset reference",
}

STRONG_DEPTH_MARKERS = {
    "multi-source",
    "bootstrap confidence intervals",
    "severity-weighted",
    "interaction analysis",
    "multi-metric",
    "multi-factor",
    "multi-window",
    "coordinated",
    "uncertainty",
}

FORBIDDEN_SPEC_PHRASES = {
    "Legacy MVP practice-level deterministic evaluator",
    "run diagnostic evaluator",
    "customer evidence file",
}


def _contains_any(text: str, markers: set[str]) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in markers)


def validate_specification_completeness(taxonomy: TaxonomyDefinition | None = None) -> list[str]:
    taxonomy = taxonomy or load_taxonomy()
    issues: list[str] = []
    for _, system, _, _, _, _, _, use_case in _iter_taxonomy(taxonomy):
        profile = SYSTEM_CONTEXT_PROFILES[system.name]
        for test in use_case.tests:
            test_payload = _dump_model(test)
            for field in ["id", "name", "objective", "technique"]:
                if not str(test_payload.get(field, "")).strip():
                    issues.append(f"{test.id}: {field} must be non-blank")
            for field in [
                "inputs_required",
                "preprocessing_steps",
                "perturbation_strategy",
                "method",
                "primary_metrics",
                "secondary_metrics",
                "benchmark_interpretation",
                "failure_criteria",
                "recommendation_logic",
            ]:
                values = test_payload.get(field)
                if not isinstance(values, list) or not values or any(not str(item).strip() for item in values):
                    issues.append(f"{test.id}: {field} must be a non-empty list of non-blank strings")
            flattened = " ".join(
                str(value)
                for key, value in test_payload.items()
                if key != "implementation_metadata"
                for value in (value if isinstance(value, list) else [value])
            )
            for phrase in FORBIDDEN_SPEC_PHRASES:
                if phrase.lower() in flattened.lower():
                    issues.append(f"{test.id}: contains forbidden transitional phrase {phrase!r}")
            benchmark_text = " ".join(test.benchmark_interpretation)
            if not _contains_any(benchmark_text, REQUIRED_BENCHMARK_MARKERS):
                issues.append(f"{test.id}: benchmark interpretation lacks a recognized benchmark class")
            if "synthetic" in benchmark_text.lower() and "illustrative synthetic reference distributions" not in benchmark_text.lower():
                issues.append(f"{test.id}: synthetic benchmark language must be explicitly illustrative")
            if not any(item.startswith("If ") for item in test.failure_criteria):
                issues.append(f"{test.id}: failure criteria must contain conditional assessable conditions")
            if not any(item.startswith("If ") for item in test.recommendation_logic):
                issues.append(f"{test.id}: recommendation logic must be conditional")
            if profile["subject"].lower() not in " ".join(test.inputs_required + test.method).lower():
                issues.append(f"{test.id}: evidence contract or method does not reference the AI-system context")
            if "prompt" in " ".join(test.inputs_required + test.method).lower() and system.name != "Customer support LLM":
                if "Prompt Log" not in test.implementation_metadata.evidence_type:
                    issues.append(f"{test.id}: prompt-oriented evidence appears outside a prompt/log diagnostic context")
            if "document_id" in " ".join(test.inputs_required).lower() and system.name != "OCR document extraction":
                if system.name != "KYC verification AI":
                    issues.append(f"{test.id}: OCR document fields appear in a non-document system")
            if test.test_type.value == "strong" and not _contains_any(" ".join(test.method + test.failure_criteria), STRONG_DEPTH_MARKERS):
                issues.append(f"{test.id}: strong test lacks an explicit depth mechanism")
    return issues


def validate_test_differentiation(taxonomy: TaxonomyDefinition | None = None) -> list[str]:
    taxonomy = taxonomy or load_taxonomy()
    issues: list[str] = []
    for _, _, _, _, _, _, _, use_case in _iter_taxonomy(taxonomy):
        tests = use_case.tests
        if [test.test_type.value for test in tests] != ["light", "light", "light", "strong"]:
            issues.append(f"{use_case.id}: expected light/light/light/strong ordering")
        comparisons = {
            "objectives": [test.objective for test in tests],
            "techniques": [test.technique for test in tests],
            "methods": [tuple(test.method) for test in tests],
            "perturbation strategies": [tuple(test.perturbation_strategy) for test in tests],
            "primary metric sets": [tuple(test.primary_metrics) for test in tests],
            "failure criteria": [tuple(test.failure_criteria) for test in tests],
            "recommendation logic": [tuple(test.recommendation_logic) for test in tests],
        }
        for label, values in comparisons.items():
            if len(set(values)) != len(values):
                issues.append(f"{use_case.id}: tests do not have distinct {label}")
        strong = tests[-1]
        light_methods = {" ".join(test.method) for test in tests[:3]}
        if " ".join(strong.method) in light_methods:
            issues.append(f"{use_case.id}: strong method duplicates a light-test method")
        if not _contains_any(" ".join(strong.method + strong.primary_metrics + strong.failure_criteria), STRONG_DEPTH_MARKERS):
            issues.append(f"{use_case.id}: strong test does not demonstrate deeper analysis")
    return issues


def validate_all(registry_path: Path | None = None) -> list[str]:
    taxonomy = load_taxonomy()
    return [
        *validate_taxonomy_contract(taxonomy),
        *validate_normalized_schema(taxonomy),
        *validate_specification_completeness(taxonomy),
        *validate_test_differentiation(taxonomy),
        *validate_registry_sync(registry_path),
        *validate_registry_references(taxonomy),
        *validate_phase2d_registry_truth(taxonomy),
    ]
