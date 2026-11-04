from __future__ import annotations

import logging

from fastapi import Body, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.benchmark_engine.benchmarks import benchmark_store
from backend.diagnostics_engine.pipeline import run_evaluation
from backend.evaluations.replay_store import list_replays
from backend.registries.loader import load_registry
from backend.report_generation.reports import generate_report
from backend.schemas.models import (
    EvaluationRequest,
    EvaluationResponse,
    ReportRequest,
    ReportResponse,
    WorkflowValidationRequest,
)
from backend.scoring_engine.scorer import aggregate_outputs
from backend.taxonomy_engine.taxonomy import list_use_cases, load_taxonomy
from backend.workflows.evidence import MAX_UPLOAD_BYTES, contract_for_workflow, parse_uploaded_evidence, validate_workflow_evidence
from backend.workflows.golden import demo_payload_for, list_workflows, run_workflow

app = FastAPI(title="AI Health Check API", version="0.1.0")

logger = logging.getLogger("ai_health_check.api")


def _dump_model(model: object) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()  # type: ignore[no-any-return]
    if hasattr(model, "dict"):
        return model.dict()  # type: ignore[no-any-return]
    return dict(model)  # type: ignore[arg-type]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate(request: EvaluationRequest) -> EvaluationResponse:
    try:
        response = run_evaluation(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if response.aggregate_score is not None:
        benchmark_store.record(response.benchmark_indicator["distribution_key"], response.aggregate_score)
    return response


@app.post("/score")
def score(response: EvaluationResponse) -> dict:
    aggregate_score, aggregate_risk, coverage = aggregate_outputs(response.outputs)
    return {
        "score": aggregate_score,
        "risk_level": aggregate_risk.value if aggregate_risk else None,
        "coverage": _dump_model(coverage),
    }


@app.post("/generate-report", response_model=ReportResponse)
def report(request: ReportRequest) -> ReportResponse:
    return generate_report(request.evaluation, request.company_name)


@app.post("/benchmark")
def benchmark(response: EvaluationResponse) -> dict:
    if response.aggregate_score is None:
        return {"eligible": False, "reason": "No assessable aggregate score is available."}
    key = response.benchmark_indicator["distribution_key"]
    return benchmark_store.record(key, response.aggregate_score)


@app.post("/taxonomy")
def taxonomy() -> dict:
    return load_taxonomy().dict()


@app.get("/use-cases")
def use_cases(ai_system: str | None = None) -> list[dict[str, str]]:
    return list_use_cases(ai_system)


@app.get("/tests")
def tests(ai_system: str, pillar: str, practice: str, use_case: str) -> list[dict]:
    from backend.taxonomy_engine.taxonomy import find_use_case

    try:
        _, _, _, use_case_item = find_use_case(ai_system, pillar, practice, use_case)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return use_case_item["tests"]


@app.get("/registries/{registry_name}")
def registry(registry_name: str) -> dict:
    if not registry_name.endswith(".json"):
        registry_name = f"{registry_name}.json"
    return load_registry(registry_name)


@app.get("/workflows")
def workflows() -> list[dict]:
    return list_workflows()


@app.get("/workflows/{workflow_id}/evidence-contract")
def workflow_evidence_contract(workflow_id: str) -> dict:
    try:
        return contract_for_workflow(workflow_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/workflows/{workflow_id}/validate")
def validate_golden_workflow(workflow_id: str, request: WorkflowValidationRequest) -> dict:
    try:
        payload = demo_payload_for(workflow_id) if request.evidence_mode.value == "demo" else request.payload
        return validate_workflow_evidence(workflow_id, payload, request.selected_test_ids)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/workflows/{workflow_id}/upload")
async def upload_golden_workflow_evidence(workflow_id: str, file: UploadFile = File(...)) -> dict:
    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
        return parse_uploaded_evidence(workflow_id, file.filename or "evidence", content)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        await file.close()


@app.post("/workflows/{workflow_id}/run")
def run_golden_workflow(
    workflow_id: str,
    request: Request,
    payload: dict | None = Body(default=None),
) -> dict:
    logger.info(
        "Golden workflow endpoint hit workflow_id=%s origin=%s has_payload=%s",
        workflow_id,
        request.headers.get("origin"),
        payload is not None,
    )
    try:
        body = payload or {}
        is_envelope = any(key in body for key in ("evidence_mode", "payload", "selected_test_ids"))
        if is_envelope:
            evidence_mode = str(body.get("evidence_mode") or "demo")
            workflow_payload = body.get("payload")
            selected_test_ids = body.get("selected_test_ids") or []
            if workflow_payload is not None and not isinstance(workflow_payload, dict):
                raise ValueError("payload must be a JSON object")
            if not isinstance(selected_test_ids, list) or not all(isinstance(item, str) for item in selected_test_ids):
                raise ValueError("selected_test_ids must be a list of strings")
        else:
            evidence_mode = "demo" if not body else "manual"
            workflow_payload = None if not body else body
            selected_test_ids = []
        response = run_workflow(
            workflow_id,
            workflow_payload,
            evidence_mode=evidence_mode,
            selected_test_ids=selected_test_ids,
        )
        logger.info(
            "Golden workflow completed workflow_id=%s score=%s replay_id=%s",
            workflow_id,
            response["evaluation"].aggregate_score,
            response["replay"]["replay_id"],
        )
        return response
    except KeyError as exc:
        logger.exception("Golden workflow not found workflow_id=%s", workflow_id)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        logger.info("Golden workflow validation failed workflow_id=%s detail=%s", workflow_id, exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Golden workflow failed workflow_id=%s", workflow_id)
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {exc}") from exc


@app.get("/replays")
def replays() -> list[dict[str, str]]:
    return list_replays()
