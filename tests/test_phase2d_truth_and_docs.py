from __future__ import annotations

import zipfile
from html import unescape
from pathlib import Path

from backend.benchmark_engine.distributions import benchmark_for_workflow
from backend.registries.loader import registry_items
from backend.workflows.golden import run_workflow


DOCX_PATH = Path("docs/Completed_MVP_Product_Taxonomy_Formatted.docx")
REPLAY_DIR = Path("backend/evaluations/replays")


def test_kyc_workflow_has_no_fraud_benchmark_fallback():
    result = benchmark_for_workflow("kyc_outlier_diagnostics", 72)
    assert result["eligible"] is False
    assert result["benchmark_id"] is None
    assert result["distribution"] == []
    assert "No AIHC synthetic reference mapping" in result["reason"]
    assert result["industry_peer_distribution"]["available"] is False
    assert result["external_references"]


def test_benchmark_registry_discloses_synthetic_non_industry_provenance():
    benchmarks = registry_items("benchmark_registry.json", "benchmarks")
    synthetic = [item for item in benchmarks if item["benchmark_type"] == "synthetic_reference"]
    external = [item for item in benchmarks if item["benchmark_type"] == "external_reference"]
    assert len(synthetic) == 4
    assert len(external) == 7
    for benchmark in synthetic:
        assert benchmark["empirical"] is False
        assert benchmark["distribution"]
        assert "Not an industry benchmark" in benchmark["limitations"]
    for reference in external:
        assert reference["source_url"].startswith("https://")
        assert reference["applicability"]
        assert reference["limitations"]


def test_workflow_registry_discloses_operational_structured_evidence_and_private_replays():
    for workflow in registry_items("workflow_registry.json", "workflows"):
        assert workflow["execution_mode"] == "demo_manual_upload"
        assert workflow["supported_evidence_modes"] == ["demo", "manual", "upload"]
        assert workflow["customer_upload_supported"] is True
        assert workflow["supported_uploads"] == ["csv", "json"]
        assert "user-provided" in workflow["evidence_source"]
        assert "not persisted" in workflow["replay_behavior"]
        assert workflow["raw_document_upload_supported"] is False


def test_all_golden_workflows_run_with_replay_writes_stubbed(monkeypatch, tmp_path):
    replay_calls: list[tuple[str, dict]] = []

    def fake_write_replay(workflow_id: str, payload: dict):
        replay_calls.append((workflow_id, payload))
        return {"replay_id": f"stub-{workflow_id}", "path": str(tmp_path / f"{workflow_id}.json")}

    monkeypatch.setattr("backend.workflows.golden.write_replay", fake_write_replay)
    before = sorted(path.name for path in REPLAY_DIR.glob("*.json"))
    workflows = registry_items("workflow_registry.json", "workflows")
    assert len(workflows) == 6

    for workflow in workflows:
        result = run_workflow(workflow["id"])
        assert result["workflow"]["id"] == workflow["id"]
        assert result["evaluation"].coverage.selected_test_count == 4
        assert result["report"].scorecard["assurance_scope"].startswith("Synthetic demo evidence")
        if workflow["id"] == "kyc_outlier_diagnostics":
            assert result["benchmark"]["eligible"] is False
        else:
            assert result["benchmark"]["eligible"] is True

    assert [call[0] for call in replay_calls] == [workflow["id"] for workflow in workflows]
    assert sorted(path.name for path in REPLAY_DIR.glob("*.json")) == before


def test_generated_taxonomy_docx_contains_normalized_schema_and_phase2d_caveats():
    assert DOCX_PATH.exists()
    with zipfile.ZipFile(DOCX_PATH) as archive:
        names = set(archive.namelist())
        assert {
            "[Content_Types].xml",
            "_rels/.rels",
            "word/document.xml",
            "word/styles.xml",
            "word/_rels/document.xml.rels",
        } <= names
        document = archive.read("word/document.xml").decode("utf-8")
    document = unescape(document)
    required_text = [
        "Test ID:",
        "Preprocessing Steps:",
        "Perturbation Strategy:",
        "Secondary Metrics:",
        "Benchmark Interpretation:",
        "Failure Criteria:",
        "Recommendation Logic:",
        "Output / Result Contract:",
        "Only the Phase 2C Golden Workflow subset has executable test-specific evaluators.",
        "customer evidence upload is not implemented",
        "illustrative synthetic references, not empirical industry peer data",
    ]
    for text in required_text:
        assert text in document
