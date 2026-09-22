from __future__ import annotations

import json
import re
import sys
import zipfile
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.diagnostics_engine.test_specific import implemented_test_ids
from backend.taxonomy_engine.validation import EXPECTED_IDENTITY_FINGERPRINT, taxonomy_counts


REGISTRY_PATH = ROOT / "backend" / "registries" / "taxonomy_registry.json"
COMPLETE_DOCX_PATH = ROOT / "docs" / "Completed_MVP_Product_Taxonomy_Formatted.docx"
REVIEW_PACK_PATH = ROOT / "docs" / "Completed_MVP_Product_Taxonomy_Review_Pack.docx"
FIXED_ZIP_DATE = (2024, 1, 1, 0, 0, 0)
GENERATION_DATE = date(2026, 9, 9).isoformat()
PHASE_BASELINE = "df51f2b7913da5438f4e42df394c3388bca6531b"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def xml(text: Any) -> str:
    return escape(str(text), quote=False)


def slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return cleaned[:36] or "section"


def run(text: str, bold: bool = False, size: int | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if size:
        props.append(f'<w:sz w:val="{size}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{xml(text)}</w:t></w:r>'


def page_number_run() -> str:
    return (
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        '<w:r><w:t>1</w:t></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
    )


def para(
    text: str = "",
    style: str | None = None,
    *,
    keep_next: bool = False,
    keep_lines: bool = False,
    page_break_before: bool = False,
    bullet: bool = False,
    bookmark: str | None = None,
    anchor: str | None = None,
    bookmark_id: int | None = None,
) -> str:
    props = []
    if style:
        props.append(f'<w:pStyle w:val="{style}"/>')
    if bullet:
        props.append('<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>')
    if keep_next:
        props.append("<w:keepNext/>")
    if keep_lines:
        props.append("<w:keepLines/>")
    props.append("<w:widowControl/>")
    if page_break_before:
        props.append("<w:pageBreakBefore/>")
    ppr = f"<w:pPr>{''.join(props)}</w:pPr>"
    body = run(text)
    if anchor:
        body = f'<w:hyperlink w:anchor="{anchor}" w:history="1"><w:r><w:rPr><w:color w:val="0563C1"/><w:u w:val="single"/></w:rPr><w:t xml:space="preserve">{xml(text)}</w:t></w:r></w:hyperlink>'
    if bookmark and bookmark_id is not None:
        body = f'<w:bookmarkStart w:id="{bookmark_id}" w:name="{bookmark}"/>{body}<w:bookmarkEnd w:id="{bookmark_id}"/>'
    return f"<w:p>{ppr}{body}</w:p>"


def bullet_para(text: str) -> str:
    return para(text, "ListBullet", bullet=True, keep_lines=True)


def field_label(text: str) -> str:
    return para(text, "FieldLabel", keep_next=True, keep_lines=True)


def section_list(label: str, values: list[str]) -> list[str]:
    items = [field_label(f"{label}:")]
    for value in values or ["None specified"]:
        items.append(bullet_para(value))
    return items


def cell(content: list[str] | str, width: int | None = None) -> str:
    width_xml = f'<w:tcW w:w="{width}" w:type="dxa"/>' if width else ""
    body = content if isinstance(content, list) else [para(str(content), keep_lines=True)]
    return f"<w:tc><w:tcPr>{width_xml}<w:vAlign w:val=\"top\"/></w:tcPr>{''.join(body)}</w:tc>"


def table(rows: list[list[list[str] | str]], widths: list[int] | None = None) -> str:
    table_props = (
        '<w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>'
        '<w:tblBorders><w:top w:val="single" w:sz="4" w:color="8A99A8"/>'
        '<w:left w:val="single" w:sz="4" w:color="8A99A8"/><w:bottom w:val="single" w:sz="4" w:color="8A99A8"/>'
        '<w:right w:val="single" w:sz="4" w:color="8A99A8"/><w:insideH w:val="single" w:sz="4" w:color="D6DEE6"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="D6DEE6"/></w:tblBorders>'
        '<w:tblLook w:firstRow="1" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
    )
    rendered_rows = []
    for row in rows:
        cells = []
        for index, value in enumerate(row):
            cells.append(cell(value, widths[index] if widths and index < len(widths) else None))
        rendered_rows.append(f"<w:tr><w:trPr><w:cantSplit/></w:trPr>{''.join(cells)}</w:tr>")
    return f"<w:tbl>{table_props}{''.join(rendered_rows)}</w:tbl>"


def sect_pr(orientation: str = "portrait", header_rid: str = "rHeader1", footer_rid: str = "rFooter1") -> str:
    if orientation == "landscape":
        page = '<w:pgSz w:w="15840" w:h="12240" w:orient="landscape"/>'
        margins = '<w:pgMar w:top="540" w:right="540" w:bottom="540" w:left="540" w:header="300" w:footer="300" w:gutter="0"/>'
    else:
        page = '<w:pgSz w:w="12240" w:h="15840"/>'
        margins = '<w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="360" w:footer="360" w:gutter="0"/>'
    return (
        "<w:sectPr>"
        f'<w:headerReference w:type="default" r:id="{header_rid}"/>'
        f'<w:footerReference w:type="default" r:id="{footer_rid}"/>'
        f"{page}{margins}"
        "</w:sectPr>"
    )


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def styles_xml() -> str:
    heading_styles = []
    for level, size in [(1, 28), (2, 22), (3, 18), (4, 15), (5, 13), (6, 11)]:
        heading_styles.append(
            f'<w:style w:type="paragraph" w:styleId="Heading{level}">'
            f'<w:name w:val="heading {level}"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>'
            '<w:pPr><w:keepNext/><w:keepLines/><w:widowControl/>'
            f'<w:spacing w:before="{180 if level < 4 else 100}" w:after="60" w:line="240" w:lineRule="auto"/></w:pPr>'
            f'<w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:b/><w:sz w:val="{size * 2}"/></w:rPr></w:style>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:styles xmlns:w="{W_NS}">'
        '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:sz w:val="20"/>'
        '</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:widowControl/><w:spacing w:after="80" w:line="240" w:lineRule="auto"/>'
        '</w:pPr></w:pPrDefault></w:docDefaults>'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>'
        '<w:pPr><w:widowControl/><w:spacing w:after="80" w:line="240" w:lineRule="auto"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:sz w:val="20"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:qFormat/>'
        '<w:pPr><w:keepNext/><w:spacing w:before="120" w:after="160" w:line="280" w:lineRule="auto"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display"/><w:b/><w:sz w:val="44"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:qFormat/>'
        '<w:pPr><w:keepNext/><w:spacing w:after="180" w:line="260" w:lineRule="auto"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:sz w:val="24"/><w:color w:val="475569"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="FieldLabel"><w:name w:val="Field Label"/><w:basedOn w:val="Normal"/>'
        '<w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="40" w:after="20" w:line="220" w:lineRule="auto"/></w:pPr>'
        '<w:rPr><w:b/><w:sz w:val="18"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Compact"><w:name w:val="Compact"/><w:basedOn w:val="Normal"/>'
        '<w:pPr><w:keepLines/><w:spacing w:after="20" w:line="210" w:lineRule="auto"/></w:pPr><w:rPr><w:sz w:val="18"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/><w:basedOn w:val="Normal"/>'
        '<w:pPr><w:keepLines/><w:spacing w:after="30" w:line="220" w:lineRule="auto"/></w:pPr><w:rPr><w:sz w:val="18"/></w:rPr></w:style>'
        '<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblCellMar>'
        '<w:top w:w="80" w:type="dxa"/><w:left w:w="80" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/>'
        '</w:tblCellMar></w:tblPr></w:style>'
        + "".join(heading_styles)
        + "</w:styles>"
    )


def numbering_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:numbering xmlns:w="{W_NS}">'
        '<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="singleLevel"/>'
        '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/>'
        '<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="360" w:hanging="180"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol" w:hint="default"/></w:rPr></w:lvl></w:abstractNum>'
        '<w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num></w:numbering>'
    )


def settings_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:settings xmlns:w="{W_NS}"><w:updateFields w:val="true"/><w:evenAndOddHeaders w:val="false"/></w:settings>'
    )


def header_xml(title: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:hdr xmlns:w="{W_NS}" xmlns:r="{R_NS}">'
        f'<w:p><w:pPr><w:pStyle w:val="Compact"/><w:jc w:val="center"/></w:pPr>{run(title, size=16)}</w:p>'
        "</w:hdr>"
    )


def footer_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:ftr xmlns:w="{W_NS}" xmlns:r="{R_NS}">'
        '<w:p><w:pPr><w:pStyle w:val="Compact"/><w:jc w:val="center"/></w:pPr>'
        f'{run("AI Health Check MVP | Page ", size=16)}{page_number_run()}</w:p></w:ftr>'
    )


def rels_xml(target: str = "word/document.xml") -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="{target}"/>'
        "</Relationships>"
    )


def content_types_xml(headers: list[str]) -> str:
    overrides = [
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>',
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>',
        '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>',
        '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>',
        '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>',
    ]
    overrides.extend(f'<Override PartName="/word/{name}" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>' for name in headers)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        + "".join(overrides)
        + "</Types>"
    )


def document_rels_xml(headers: list[str]) -> str:
    relationships = [
        '<Relationship Id="rStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
        '<Relationship Id="rNumbering" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>',
        '<Relationship Id="rSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>',
        '<Relationship Id="rFooter1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>',
    ]
    relationships.extend(
        f'<Relationship Id="rHeader{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="{name}"/>'
        for index, name in enumerate(headers, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(relationships)
        + "</Relationships>"
    )


def write_docx(path: Path, document_xml: str, headers: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header_names = [name for name, _ in headers]
    parts = [
        ("[Content_Types].xml", content_types_xml(header_names)),
        ("_rels/.rels", rels_xml()),
        ("word/document.xml", document_xml),
        ("word/styles.xml", styles_xml()),
        ("word/numbering.xml", numbering_xml()),
        ("word/settings.xml", settings_xml()),
        ("word/footer1.xml", footer_xml()),
        ("word/_rels/document.xml.rels", document_rels_xml(header_names)),
    ]
    parts.extend((f"word/{name}", content) for name, content in headers)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in parts:
            info = zipfile.ZipInfo(name, FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)


def iter_contexts(registry: dict[str, Any]):
    for system in registry["taxonomy"]["ai_systems"]:
        for pillar in system["pillars"]:
            for practice in pillar["practices"]:
                for use_case in practice["use_cases"]:
                    yield system, pillar, practice, use_case


def flatten_tests(registry: dict[str, Any]) -> list[dict[str, Any]]:
    return [test for *_ctx, use_case in iter_contexts(registry) for test in use_case["tests"]]


def counts_summary(registry: dict[str, Any]) -> dict[str, int]:
    tests = flatten_tests(registry)
    use_cases = list(iter_contexts(registry))
    practices = {practice["name"] for _, _, practice, _ in use_cases}
    return {
        "systems": len(registry["taxonomy"]["ai_systems"]),
        "use_cases": len(use_cases),
        "tests": len(tests),
        "light_tests": sum(test["test_type"] == "light" for test in tests),
        "strong_tests": sum(test["test_type"] == "strong" for test in tests),
        "practices": len(practices),
        "implemented_tests": len(implemented_test_ids()),
        "specification_only_tests": len(tests) - len(implemented_test_ids()),
    }


def provenance_paragraphs(registry: dict[str, Any]) -> list[str]:
    counts = counts_summary(registry)
    return [
        para("Completed MVP Product Taxonomy", "Title"),
        para("Complete Reference | Lendingtech Assisted Intelligence MVP", "Subtitle"),
        field_label("Document Provenance"),
        bullet_para(f"Registry: {registry['registry_name']} v{registry['version']}"),
        bullet_para(f"Generation date: {GENERATION_DATE}"),
        bullet_para(f"Source of truth: {registry.get('source_of_truth', 'backend/taxonomy_engine/taxonomy.py')}"),
        bullet_para(f"Taxonomy identity fingerprint: {EXPECTED_IDENTITY_FINGERPRINT}"),
        bullet_para(f"Phase 2D baseline: {PHASE_BASELINE}"),
        bullet_para(f"Counts: {counts['systems']} systems; {counts['use_cases']} use cases; {counts['light_tests']} Light Tests; {counts['strong_tests']} Strong Tests; {counts['practices']} Supporting Practices"),
        bullet_para(f"Executable tests: {counts['implemented_tests']}; specification-only tests: {counts['specification_only_tests']}"),
        bullet_para("Only the Phase 2C Golden Workflow subset has executable test-specific evaluators."),
        bullet_para("Workflow execution uses deterministic synthetic demo evidence."),
        bullet_para("Workflow runs use deterministic synthetic demo evidence; customer evidence upload is not implemented."),
        bullet_para("Customer-data upload is not implemented."),
        bullet_para("Benchmark distributions are illustrative synthetic references, not empirical industry peer data."),
        bullet_para("Benchmarks are illustrative synthetic references, not empirical industry peer data."),
    ]


def build_index(registry: dict[str, Any], *, include_links: bool = True) -> list[str]:
    body = [para("Navigable Contents", "Heading1")]
    bookmark_id = 1
    for system in registry["taxonomy"]["ai_systems"]:
        body.append(para(system["name"], "Heading3", keep_next=True))
        for pillar in system["pillars"]:
            body.append(para(f"Pillar: {pillar['name']}", "FieldLabel"))
            for practice in pillar["practices"]:
                body.append(para(f"{practice['name']} | Category {practice['category']} | {practice['orientation']}", "Compact"))
                for use_case in practice["use_cases"]:
                    anchor = f"uc_{slug(use_case['id'])}"
                    text = f"{system['name']} > {pillar['name']} > {practice['name']} > {use_case['name']}"
                    body.append(para(text, "Compact", anchor=anchor if include_links else None))
                    bookmark_id += 1
    return body


def build_complete_document(registry: dict[str, Any]) -> tuple[str, list[tuple[str, str]]]:
    headers = [("header1.xml", header_xml("AI Health Check Complete Taxonomy | Section context shown in page headings"))]
    body = provenance_paragraphs(registry)
    body.extend(build_index(registry))
    body.append(page_break())
    body.append(para(f"Fintech Segment: {registry['taxonomy']['fintech_segment']}", "Heading1", bookmark="taxonomy_start", bookmark_id=9000))
    bookmark_id = 100
    for system in registry["taxonomy"]["ai_systems"]:
        body.append(para(f"AI System: {system['name']}", "Heading2", keep_next=True, keep_lines=True))
        body.append(para(f"Typical Use: {system['typical_use']}"))
        for pillar in system["pillars"]:
            body.append(para(f"Pillar: {pillar['name']}", "Heading3", keep_next=True, keep_lines=True))
            for practice in pillar["practices"]:
                body.append(para(f"Supporting Practice: {practice['name']}", "Heading4", keep_next=True, keep_lines=True))
                body.append(para(f"Category: {practice['category']} | Orientation: {practice['orientation']}", "Compact"))
                scores = practice["meaningfulness"]
                body.append(para("Meaningfulness Scores: " + "; ".join(f"{key.replace('_', ' ').title()}={value}" for key, value in scores.items()), "Compact"))
                for use_case in practice["use_cases"]:
                    body.append(
                        para(
                            f"Use Case: {use_case['name']}",
                            "Heading5",
                            keep_next=True,
                            keep_lines=True,
                            bookmark=f"uc_{slug(use_case['id'])}",
                            bookmark_id=bookmark_id,
                        )
                    )
                    bookmark_id += 1
                    body.append(para(f"Use Case ID: {use_case['id']}", "Compact"))
                    body.append(para(f"Use Case Description: {use_case['description']}"))
                    light_index = 1
                    for test in use_case["tests"]:
                        label = "Strong Test" if test["test_type"] == "strong" else f"Light Test {light_index}"
                        light_index += 1 if test["test_type"] == "light" else 0
                        body.append(para(f"{label}: {test['name']}", "Heading6", keep_next=True, keep_lines=True))
                        body.append(para(f"Test ID: {test['id']}", "Compact"))
                        body.append(para(f"Test Type: {test['test_type']}", "Compact"))
                        body.append(para(f"Objective: {test['objective']}"))
                        body.append(para(f"Technique: {test['technique']}"))
                        for label_name, key in [
                            ("Inputs Required", "inputs_required"),
                            ("Preprocessing Steps", "preprocessing_steps"),
                            ("Perturbation Strategy", "perturbation_strategy"),
                            ("Method", "method"),
                            ("Primary Metrics", "primary_metrics"),
                            ("Secondary Metrics", "secondary_metrics"),
                            ("Benchmark Interpretation", "benchmark_interpretation"),
                            ("Failure Criteria", "failure_criteria"),
                            ("Recommendation Logic", "recommendation_logic"),
                        ]:
                            body.extend(section_list(label_name, test[key]))
                        metadata = test["implementation_metadata"]
                        body.append(field_label("Implementation Metadata:"))
                        for key, value in metadata.items():
                            body.append(bullet_para(f"{key.replace('_', ' ').title()}: {value}"))
                        body.append(para("Output / Result Contract: score, risk_level, execution_status, evidence_status, raw_metrics, metric_interpretation, sample_size, coverage, thresholds, findings, insight, recommendation, limitations, execution_metadata, and metadata."))
    body.append(para("Implementation Source of Truth", "Heading1"))
    body.append(para("This complete reference is generated from backend/registries/taxonomy_registry.json, which is generated from backend/taxonomy_engine/taxonomy.py."))
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}"><w:body>'
        + "".join(body)
        + sect_pr("portrait")
        + "</w:body></w:document>"
    )
    return document, headers


def common_values(tests: list[dict[str, Any]], key: str) -> list[str]:
    values = [tuple(test[key]) for test in tests]
    return list(values[0]) if values and all(value == values[0] for value in values) else []


def first_or_join(values: list[str]) -> str:
    return "; ".join(values) if values else "None specified"


def workflow_for(workflows: list[dict[str, Any]], system: str, practice: str, use_case: str) -> dict[str, Any] | None:
    for workflow in workflows:
        if workflow["ai_system"] == system and workflow["supporting_practice"] == practice and workflow["use_case"] == use_case:
            return workflow
    return None


def benchmark_eligibility(test: dict[str, Any], workflow: dict[str, Any] | None) -> str:
    if workflow and workflow["id"] == "kyc_outlier_diagnostics":
        return "Benchmark ineligible: KYC outlier diagnostics has no benchmark mapping and does not fall back to fraud."
    reference = test["implementation_metadata"]["benchmark_reference"]
    if reference == "benchmark_registry:planned":
        return "Benchmark ineligible/planned for this specification."
    return "Benchmark eligible only against illustrative synthetic reference distributions."


def build_review_sheet(
    system: dict[str, Any],
    pillar: dict[str, Any],
    practice: dict[str, Any],
    use_case: dict[str, Any],
    workflow: dict[str, Any] | None,
    bookmark_id: int,
) -> list[str]:
    tests = use_case["tests"]
    common_inputs = common_values(tests, "inputs_required")
    common_preprocessing = common_values(tests, "preprocessing_steps")
    workflow_text = workflow["id"] if workflow else "No Golden Workflow"
    benchmark_text = benchmark_eligibility(tests[0], workflow)
    body = [
        para(
            f"Use Case Review Sheet: {use_case['name']}",
            "Heading1",
            page_break_before=True,
            bookmark=f"uc_{slug(use_case['id'])}",
            bookmark_id=bookmark_id,
        ),
        table(
            [
                ["AI System", system["name"], "Pillar", pillar["name"]],
                ["Supporting Practice", practice["name"], "Category / Orientation", f"{practice['category']} / {practice['orientation']}"],
                ["Use Case ID", use_case["id"], "Workflow", workflow_text],
                ["Benchmark", benchmark_text, "Customer Upload", "Not implemented"],
            ],
            [2200, 5200, 2200, 5200],
        ),
        field_label("Use Case Description:"),
        para(use_case["description"], "Compact"),
        field_label("Meaningfulness Scores:"),
        para("; ".join(f"{key.replace('_', ' ').title()}={value}" for key, value in practice["meaningfulness"].items()), "Compact"),
        field_label("Common Evidence Contract:"),
        para(first_or_join(common_inputs) if common_inputs else "Evidence requirements differ by test; see test rows.", "Compact"),
        field_label("Common Preprocessing Requirements:"),
        para(first_or_join(common_preprocessing) if common_preprocessing else "Preprocessing requirements differ by test; see test rows.", "Compact"),
    ]
    rows: list[list[list[str] | str]] = [[
        [para("Test", "FieldLabel")],
        [para("Objective / Technique", "FieldLabel")],
        [para("Evidence, Metrics, Benchmark", "FieldLabel")],
        [para("Failure / Recommendation / Status", "FieldLabel")],
    ]]
    light_index = 1
    for test in tests:
        label = "Strong" if test["test_type"] == "strong" else f"Light {light_index}"
        light_index += 1 if test["test_type"] == "light" else 0
        metadata = test["implementation_metadata"]
        evaluator = metadata["evaluator_reference"].replace("evaluator_registry:", "")
        if evaluator == "planned":
            evaluator = "not implemented"
        rows.append(
            [
                [
                    para(label, "Compact"),
                    para(test["id"], "Compact"),
                    para(test["name"], "Compact"),
                ],
                [
                    para(test["objective"], "Compact"),
                    para(f"Technique: {test['technique']}", "Compact"),
                    para(f"Perturbation: {first_or_join(test['perturbation_strategy'])}", "Compact"),
                ],
                [
                    para(f"Inputs: {'test-specific differences' if common_inputs else first_or_join(test['inputs_required'])}", "Compact"),
                    para(f"Preprocessing: {'test-specific differences' if common_preprocessing else first_or_join(test['preprocessing_steps'])}", "Compact"),
                    para(f"Primary: {first_or_join(test['primary_metrics'])}", "Compact"),
                    para(f"Secondary: {first_or_join(test['secondary_metrics'])}", "Compact"),
                    para(f"Benchmark: {first_or_join(test['benchmark_interpretation'])}", "Compact"),
                ],
                [
                    para(f"Failure: {first_or_join(test['failure_criteria'])}", "Compact"),
                    para(f"Recommendation: {first_or_join(test['recommendation_logic'])}", "Compact"),
                    para(f"Evaluator ID: {evaluator}", "Compact"),
                    para(f"Implementation Status: {metadata['implementation_status']}; Evaluator Status: {metadata['evaluator_status']}", "Compact"),
                ],
            ]
        )
    body.append(table(rows, [2700, 4200, 4700, 4700]))
    body.append(field_label("Reviewer Area:"))
    body.append(table([["Review decision", "Accept / Revise / Reject"], ["Reviewer notes", "\n\n\n"]], [3000, 12000]))
    return body


def build_review_pack(registry: dict[str, Any], workflows: list[dict[str, Any]]) -> tuple[str, list[tuple[str, str]]]:
    headers = [("header1.xml", header_xml("AI Health Check Review Pack | Use-case sheets | Page context in sheet header"))]
    counts = counts_summary(registry)
    body = [
        para("Completed MVP Product Taxonomy Review Pack", "Title"),
        para("Human Review Pack | Generated Artifact", "Subtitle"),
        field_label("Purpose"),
        para("This pack gives reviewers a compact view of every use case and every test ID without repeating the full complete-reference specification text four times per use case."),
        field_label("Counts And Identity"),
        bullet_para(f"AI systems: {counts['systems']}"),
        bullet_para(f"Supporting Practices: {counts['practices']}"),
        bullet_para(f"Use cases: {counts['use_cases']}"),
        bullet_para(f"Tests: {counts['tests']} ({counts['light_tests']} Light; {counts['strong_tests']} Strong)"),
        bullet_para(f"Executable tests: {counts['implemented_tests']}; specification-only tests: {counts['specification_only_tests']}"),
        bullet_para(f"Taxonomy identity fingerprint: {EXPECTED_IDENTITY_FINGERPRINT}"),
        field_label("Phase 2D Boundaries"),
        bullet_para("Only 24 tests currently have concrete executable evaluators."),
        bullet_para("The remaining 496 tests are technically refined specifications."),
        bullet_para("Workflow execution uses deterministic synthetic demo evidence."),
        bullet_para("Customer-data upload is not implemented."),
        bullet_para("Benchmarks are illustrative synthetic references; no industry-peer claims are supported."),
        bullet_para("KYC outlier diagnostics are benchmark-ineligible in the current MVP."),
        bullet_para("This review pack does not replace the executable taxonomy or registry."),
        field_label("Reviewer Instructions"),
        bullet_para("Review one use-case sheet at a time."),
        bullet_para("Confirm that each Light Test has a distinct purpose and that the Strong Test adds depth."),
        bullet_para("Mark Accept, Revise, or Reject and add notes in the reviewer area."),
        field_label("Legend"),
        bullet_para("Light: targeted diagnostic check."),
        bullet_para("Strong: deeper combined or stress-oriented diagnostic."),
        bullet_para("Implemented: concrete Phase 2C evaluator exists for the test ID."),
        bullet_para("Partial: specification is refined but not fully productized."),
        bullet_para("Planned: no evaluator is currently routed."),
        bullet_para("Benchmark eligible: illustrative synthetic reference is available."),
        bullet_para("Benchmark ineligible: no benchmark mapping is used."),
        para("Six Golden Workflow Summary", "Heading1"),
        table(
            [["Workflow ID", "AI System", "Practice", "Evidence Source", "Benchmark", "Replay Behavior"]]
            + [
                [
                    workflow["id"],
                    workflow["ai_system"],
                    workflow["supporting_practice"],
                    workflow["evidence_source"],
                    "Ineligible" if workflow["id"] == "kyc_outlier_diagnostics" else "Synthetic reference",
                    workflow["replay_behavior"],
                ]
                for workflow in workflows
            ],
            [3200, 3000, 3200, 5000, 2200, 4200],
        ),
    ]
    body.extend(build_index(registry))
    bookmark_id = 100
    for system, pillar, practice, use_case in iter_contexts(registry):
        workflow = workflow_for(workflows, system["name"], practice["name"], use_case["name"])
        body.extend(build_review_sheet(system, pillar, practice, use_case, workflow, bookmark_id))
        bookmark_id += 1
    body.append(para("Standard Output / Result Contract", "Heading1", page_break_before=True))
    body.append(para("Every test returns or specifies: score, risk_level, execution_status, evidence_status, raw_metrics, metric_interpretation, sample_size, coverage, thresholds, findings, insight, recommendation, limitations, execution_metadata, and metadata."))
    body.append(para("Benchmark And Evidence Caveats", "Heading1"))
    body.append(bullet_para("Synthetic benchmark distributions are illustrative and fixed for MVP review."))
    body.append(bullet_para("Customer evidence upload and production persistence are not implemented."))
    body.append(bullet_para("Do not interpret this pack as regulatory certification or industry benchmark proof."))
    body.append(para("Reviewer Sign-Off Summary", "Heading1"))
    body.append(table([["Reviewer", ""], ["Date", ""], ["Overall decision", "Accept / Revise / Reject"], ["Summary notes", "\n\n\n\n"]], [3000, 12000]))
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}"><w:body>'
        + "".join(body)
        + sect_pr("landscape")
        + "</w:body></w:document>"
    )
    return document, headers


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    workflows = json.loads((ROOT / "backend" / "registries" / "workflow_registry.json").read_text(encoding="utf-8"))["workflows"]
    counts = taxonomy_counts()
    if counts["tests"] != 520 or counts["use_cases"] != 130:
        raise SystemExit(f"Unexpected taxonomy counts: {counts}")
    complete_xml, complete_headers = build_complete_document(registry)
    review_xml, review_headers = build_review_pack(registry, workflows)
    write_docx(COMPLETE_DOCX_PATH, complete_xml, complete_headers)
    write_docx(REVIEW_PACK_PATH, review_xml, review_headers)
    print(COMPLETE_DOCX_PATH)
    print(REVIEW_PACK_PATH)


if __name__ == "__main__":
    main()
