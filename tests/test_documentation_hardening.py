from __future__ import annotations

import re
import zipfile
from html import unescape
from pathlib import Path

from backend.diagnostics_engine.test_specific import implemented_test_ids
from backend.registries.loader import load_registry
from backend.taxonomy_engine.validation import EXPECTED_IDENTITY_FINGERPRINT


COMPLETE_DOCX = Path("docs/Completed_MVP_Product_Taxonomy_Formatted.docx")
REVIEW_PACK = Path("docs/Completed_MVP_Product_Taxonomy_Review_Pack.docx")
HLD = Path("docs/HLD.md")


def _doc_part(path: Path, name: str) -> str:
    with zipfile.ZipFile(path) as archive:
        return archive.read(name).decode("utf-8")


def _visible_text(path: Path) -> str:
    xml = _doc_part(path, "word/document.xml")
    xml = re.sub(r"<[^>]+>", "", xml)
    return unescape(xml)


def _taxonomy_items():
    taxonomy = load_registry("taxonomy_registry.json")["taxonomy"]
    systems = taxonomy["ai_systems"]
    contexts = []
    tests = []
    for system in systems:
        for pillar in system["pillars"]:
            for practice in pillar["practices"]:
                for use_case in practice["use_cases"]:
                    contexts.append((system, pillar, practice, use_case))
                    tests.extend(use_case["tests"])
    return systems, contexts, tests


def test_complete_reference_contains_all_520_test_ids_and_explicit_docx_structure():
    systems, _contexts, tests = _taxonomy_items()
    document = _visible_text(COMPLETE_DOCX)
    styles = _doc_part(COMPLETE_DOCX, "word/styles.xml")
    footer = _doc_part(COMPLETE_DOCX, "word/footer1.xml")
    numbering = _doc_part(COMPLETE_DOCX, "word/numbering.xml")

    assert len(tests) == 520
    assert all(test["id"] in document for test in tests)
    assert all(system["name"] in document for system in systems)
    assert EXPECTED_IDENTITY_FINGERPRINT in document
    assert "Customer-data upload is not implemented." in document
    assert "Benchmarks are illustrative synthetic references" in document
    assert "Output / Result Contract:" in document
    assert "w:abstractNum" in numbering and "w:numFmt w:val=\"bullet\"" in numbering
    assert "PAGE" in footer
    for style_id in ["Normal", "Title", "Subtitle", "Heading1", "Heading2", "Heading3", "Heading4", "Heading5", "Heading6", "ListBullet", "FieldLabel"]:
        assert f'w:styleId="{style_id}"' in styles


def test_review_pack_covers_taxonomy_once_with_navigation_and_status_counts():
    systems, contexts, tests = _taxonomy_items()
    document = _visible_text(REVIEW_PACK)
    styles = _doc_part(REVIEW_PACK, "word/styles.xml")
    footer = _doc_part(REVIEW_PACK, "word/footer1.xml")
    implemented = implemented_test_ids()

    assert len(contexts) == 130
    assert len(tests) == 520
    for test in tests:
        assert document.count(test["id"]) == 1
    assert document.count("Use Case ID") == 130
    for index, (_system, _pillar, _practice, use_case) in enumerate(contexts):
        marker = f"Use Case ID{use_case['id']}"
        assert marker in document
        sheet_start = document.index(marker)
        if index + 1 < len(contexts):
            next_marker = f"Use Case ID{contexts[index + 1][3]['id']}"
            sheet_end = document.index(next_marker)
        else:
            sheet_end = document.index("Standard Output / Result Contract")
        sheet = document[sheet_start:sheet_end]
        assert sheet.count("Light 1") == 1
        assert sheet.count("Light 2") == 1
        assert sheet.count("Light 3") == 1
        assert sheet.count("Strong") >= 1
    for system in systems:
        assert system["name"] in document
    pillars = {pillar["name"] for system in systems for pillar in system["pillars"]}
    practices = {practice["name"] for system in systems for pillar in system["pillars"] for practice in pillar["practices"]}
    assert len(pillars) == 5
    assert len(practices) == 21
    assert all(pillar in document for pillar in pillars)
    assert all(practice in document for practice in practices)
    assert document.count("Evaluator Status: Implemented") == len(implemented) == 24
    assert document.count("Evaluator Status: Planned") == 520 - len(implemented) == 496
    assert EXPECTED_IDENTITY_FINGERPRINT in document
    assert "KYC outlier diagnostics are benchmark-ineligible" in document
    assert "Customer-data upload is not implemented." in document
    assert "Standard Output / Result Contract" in document
    raw_document = _doc_part(REVIEW_PACK, "word/document.xml")
    assert raw_document.count("<w:bookmarkStart") >= 130
    assert raw_document.count("<w:hyperlink") >= 130
    assert "PAGE" in footer
    for style_id in ["Normal", "Heading1", "Heading2", "Heading3", "Heading4", "Heading5", "Heading6"]:
        assert f'w:styleId="{style_id}"' in styles


def test_hld_contains_required_sections_and_mermaid_diagrams():
    text = HLD.read_text(encoding="utf-8")
    required_sections = [
        "Document Purpose And Status",
        "Product Scope And Non-Goals",
        "Taxonomy Model And Invariants",
        "System Context",
        "Component Architecture",
        "Evaluation Request And Response Sequence",
        "Taxonomy-To-Registry Synchronization Flow",
        "Backend Component Responsibilities",
        "Frontend Component And Route Responsibilities",
        "API Surface And Side Effects",
        "Golden Workflow Catalogue",
        "Evidence And Dataset-Origin Model",
        "Test-Specific Evaluator-Routing Model",
        "Execution And Evidence Statuses",
        "Scoring And Coverage Eligibility",
        "Benchmark Architecture And Eligibility",
        "Reporting And Recommendation Flow",
        "Replay And Persistence Behavior",
        "Database Status",
        "Deployment And Runtime Topology",
        "Security And Trust Boundaries",
        "Error Handling",
        "Observability And Auditability",
        "Current Limitations",
        "Future Architecture",
        "Source-Of-Truth And Generated-Artifact Rules",
    ]
    for section in required_sections:
        assert f"## {section}" in text
    assert text.count("```mermaid") >= 4
    assert "POST /workflows/{workflow_id}/run writes a replay JSON file" in text
    assert "KYC does not fall back to the fraud benchmark" in text
    assert "backend/schemas/database.sql is a proposed relational schema" in text
    assert re.search(r"\| `/taxonomy` \| Live backend data", text)
