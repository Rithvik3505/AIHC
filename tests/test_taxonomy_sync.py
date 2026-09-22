from __future__ import annotations

import json

import pytest

from backend.registries.taxonomy_sync import (
    TaxonomyRegistryDriftError,
    check_registry,
    expected_registry_text,
    validate_registry_file,
    write_registry,
)
from backend.taxonomy_engine.validation import (
    EXPECTED_COUNTS,
    EXPECTED_IDENTITY_FINGERPRINT,
    identity_fingerprint,
    taxonomy_counts,
    validate_all,
    validate_specification_completeness,
    validate_test_differentiation,
    validate_normalized_schema,
    validate_registry_references,
    validate_registry_sync,
    validate_phase2d_registry_truth,
    validate_taxonomy_contract,
)
from backend.taxonomy_engine.taxonomy import load_taxonomy


def test_taxonomy_counts_and_identity_are_preserved():
    taxonomy = load_taxonomy()
    counts = taxonomy_counts(taxonomy)
    for key, expected in EXPECTED_COUNTS.items():
        assert counts[key] == expected
    assert counts["tests_per_use_case"] == {4: 130}
    assert counts["categories"] == {"A": 104, "B": 26}
    assert counts["orientations"] == {"Horizontal": 104, "Hybrid": 26}
    assert "Data Integrity" in counts["pillars"]
    assert "Data" not in counts["pillars"]
    assert identity_fingerprint(taxonomy) == EXPECTED_IDENTITY_FINGERPRINT
    assert validate_taxonomy_contract(taxonomy) == []


def test_tests_use_normalized_diagnostic_schema():
    taxonomy = load_taxonomy()
    assert validate_normalized_schema(taxonomy) == []
    for system in taxonomy.ai_systems:
        for pillar in system.pillars:
            for practice in pillar.practices:
                for use_case in practice.use_cases:
                    for test in use_case.tests:
                        assert not hasattr(test, "metrics")
                        assert isinstance(test.primary_metrics, list)
                        assert isinstance(test.secondary_metrics, list)
                        assert isinstance(test.preprocessing_steps, list)
                        assert isinstance(test.perturbation_strategy, list)
                        assert isinstance(test.benchmark_interpretation, list)
                        assert isinstance(test.failure_criteria, list)
                        assert isinstance(test.recommendation_logic, list)


def test_taxonomy_registry_matches_deterministic_exporter():
    assert validate_registry_sync() == []


def test_registry_write_then_check_is_idempotent(tmp_path):
    registry_path = tmp_path / "taxonomy_registry.json"
    write_registry(registry_path)
    first = registry_path.read_text(encoding="utf-8")
    validate_registry_file(registry_path)
    check_registry(registry_path)
    write_registry(registry_path)
    assert registry_path.read_text(encoding="utf-8") == first == expected_registry_text()


def test_registry_check_detects_drift_without_writing(tmp_path):
    registry_path = tmp_path / "taxonomy_registry.json"
    write_registry(registry_path)
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    payload["taxonomy"]["ai_systems"][0]["name"] = "Changed system name"
    drifted = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    registry_path.write_text(drifted, encoding="utf-8")
    with pytest.raises(TaxonomyRegistryDriftError):
        check_registry(registry_path)
    assert registry_path.read_text(encoding="utf-8") == drifted


def test_registry_references_are_resolvable():
    assert validate_registry_references(load_taxonomy()) == []


def test_complete_taxonomy_validation_passes():
    assert validate_all() == []


def test_phase_2d_registry_truth_validation_passes():
    assert validate_phase2d_registry_truth(load_taxonomy()) == []


def test_phase_2b_specifications_are_complete_and_differentiated():
    taxonomy = load_taxonomy()
    assert validate_specification_completeness(taxonomy) == []
    assert validate_test_differentiation(taxonomy) == []
