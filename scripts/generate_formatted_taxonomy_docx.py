from __future__ import annotations

import json
import zipfile
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCX_PATH = ROOT / "docs" / "Completed_MVP_Product_Taxonomy_Formatted.docx"
REGISTRY_PATH = ROOT / "backend" / "registries" / "taxonomy_registry.json"


def p(text: str, style: str | None = None) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    return f'<w:p>{style_xml}<w:r><w:t xml:space="preserve">{escape(str(text))}</w:t></w:r></w:p>'


def bullet(text: str) -> str:
    return p(f"- {text}")


def style_xml() -> str:
    styles = [
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="40"/></w:rPr></w:style>',
        '<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:rPr><w:sz w:val="24"/></w:rPr></w:style>',
    ]
    for level in range(1, 7):
        size = 32 - (level * 2)
        styles.append(
            f'<w:style w:type="paragraph" w:styleId="Heading{level}">'
            f'<w:name w:val="heading {level}"/><w:basedOn w:val="Normal"/>'
            f'<w:next w:val="Normal"/><w:qFormat/><w:rPr><w:b/><w:sz w:val="{size}"/></w:rPr></w:style>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        + "".join(styles)
        + "</w:styles>"
    )


def add_metadata(body: list[str], metadata: dict) -> None:
    body.append(p("Implementation Metadata"))
    ordered = [
        ("Implementation Status", "implementation_status"),
        ("Workflow", "workflow_status"),
        ("Workflow Reference", "workflow_reference"),
        ("Evaluator", "evaluator_status"),
        ("Evaluator Reference", "evaluator_reference"),
        ("Evidence Type", "evidence_type"),
        ("Dataset", "dataset_source"),
        ("Dataset Reference", "dataset_reference"),
        ("Benchmark", "benchmark_status"),
        ("Benchmark Reference", "benchmark_reference"),
        ("Customer Upload", "customer_upload"),
        ("Automation Level", "automation_level"),
    ]
    for label, key in ordered:
        body.append(bullet(f"{label}: {metadata.get(key, '')}"))


def build_document_xml(registry: dict) -> str:
    taxonomy = registry["taxonomy"]
    systems = taxonomy["ai_systems"]
    use_cases = [
        use_case
        for system in systems
        for pillar in system["pillars"]
        for practice in pillar["practices"]
        for use_case in practice["use_cases"]
    ]
    test_count = sum(len(use_case["tests"]) for use_case in use_cases)
    category_a = sum(
        1
        for system in systems
        for pillar in system["pillars"]
        for practice in pillar["practices"]
        for _ in practice["use_cases"]
        if practice["category"] == "A"
    )
    category_b = len(use_cases) - category_a

    body: list[str] = []
    body.append(p("Completed MVP Product Taxonomy", "Title"))
    body.append(p("AI Health Check - Lendingtech Phase 1", "Subtitle"))
    body.append(p("Document Summary", "Heading1"))
    body.append(p(f"Meaningful use cases: {len(use_cases)}"))
    body.append(p(f"Category A use cases: {category_a}"))
    body.append(p(f"Category B use cases: {category_b}"))
    body.append(p(f"Total tests: {test_count}"))
    body.append(p("Scope", "Heading1"))
    body.append(
        p(
            "This taxonomy preserves the Phase 1 Lendingtech hierarchy while refining semantic quality, "
            "diagnostic realism, implementation traceability, and frontend usability."
        )
    )
    body.append(p("Hierarchy", "Heading1"))
    body.append(p("Fintech Segment -> AI System -> Pillar -> Supporting Practice -> Use Case -> Test Type"))
    body.append(p("Meaningfulness Heuristic", "Heading1"))
    for item in registry["meaningfulness_heuristic"]:
        body.append(bullet(item.replace("_", " ").title()))
    body.append(p(f"Fintech Segment: {taxonomy['fintech_segment']}", "Heading1"))

    for system in systems:
        body.append(p(f"AI System: {system['name']}", "Heading2"))
        body.append(p(f"Typical Use: {system['typical_use']}"))
        for pillar in system["pillars"]:
            body.append(p(f"Pillar: {pillar['name']}", "Heading3"))
            for practice in pillar["practices"]:
                body.append(p(f"Supporting Practice: {practice['name']}", "Heading4"))
                body.append(p(f"Category: {practice['category']}"))
                body.append(p(f"Orientation: {practice['orientation']}"))
                scores = practice["meaningfulness"]
                body.append(
                    p(
                        "Meaningfulness Scores: "
                        f"Risk Criticality={scores['risk_criticality']}; "
                        f"Founder Pain={scores['founder_pain']}; "
                        f"Investor/Reputational Importance={scores['investor_reputational_importance']}; "
                        f"Benchmark Density Potential={scores['benchmark_density_potential']}; "
                        f"Technical Signal Strength={scores['technical_signal_strength']}; "
                        f"MVP Feasibility={scores['mvp_feasibility']}"
                    )
                )
                for use_case in practice["use_cases"]:
                    body.append(p(f"Use Case: {use_case['name']}", "Heading5"))
                    body.append(p(f"Use Case Description: {use_case['description']}"))
                    light_index = 1
                    for test in use_case["tests"]:
                        if test["test_type"] == "strong":
                            label = f"Strong Test: {test['name']}"
                        else:
                            label = f"Light Test {light_index}: {test['name']}"
                            light_index += 1
                        body.append(p(label, "Heading6"))
                        body.append(p(f"Test Type: {test['test_type']}"))
                        body.append(p(f"Objective: {test['objective']}"))
                        body.append(p("Inputs Required:"))
                        for item in test["inputs_required"]:
                            body.append(bullet(item))
                        body.append(p("Method:"))
                        for item in test["method"]:
                            body.append(bullet(item))
                        body.append(p("Metrics:"))
                        for item in test["metrics"]:
                            body.append(bullet(item))
                        add_metadata(body, test.get("implementation_metadata", {}))
                        body.append(p("Output: Standard JSON test output with score, risk_level, insight, recommendation, and metadata."))

    body.append(p("Implementation Source of Truth", "Heading1"))
    body.append(p("This document is generated from backend/registries/taxonomy_registry.json, which is exported from backend/taxonomy_engine/taxonomy.py."))
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
        + "".join(body)
        + '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="450" w:footer="450" w:gutter="0"/></w:sectPr>'
        + "</w:body></w:document>"
    )


def write_docx(document_xml: str) -> None:
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )
    doc_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        "</Relationships>"
    )
    DOCX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(DOCX_PATH, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document_xml)
        archive.writestr("word/styles.xml", style_xml())
        archive.writestr("word/_rels/document.xml.rels", doc_rels)


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    write_docx(build_document_xml(registry))
    print(DOCX_PATH)


if __name__ == "__main__":
    main()
