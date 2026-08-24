from __future__ import annotations

import logging

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.benchmark_engine.benchmarks import benchmark_store
from backend.diagnostics_engine.pipeline import run_evaluation
from backend.evaluations.replay_store import list_replays
from backend.registries.loader import load_registry
from backend.report_generation.reports import generate_report
from backend.schemas.models import EvaluationRequest, EvaluationResponse, ReportRequest, ReportResponse
from backend.scoring_engine.scorer import aggregate_outputs
from backend.taxonomy_engine.taxonomy import list_use_cases, load_taxonomy
from backend.workflows.golden import list_workflows, run_workflow

app = FastAPI(title="AI Health Check API", version="0.1.0")

logger = logging.getLogger("ai_health_check.api")

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
    benchmark_store.record(response.benchmark_indicator["distribution_key"], response.aggregate_score)
    return response


@app.post("/score")
def score(response: EvaluationResponse) -> dict:
    aggregate_score, aggregate_risk = aggregate_outputs(response.outputs)
    return {"score": aggregate_score, "risk_level": aggregate_risk.value}


@app.post("/generate-report", response_model=ReportResponse)
def report(request: ReportRequest) -> ReportResponse:
    return generate_report(request.evaluation, request.company_name)


@app.post("/benchmark")
def benchmark(response: EvaluationResponse) -> dict:
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
        response = run_workflow(workflow_id, payload)
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
    except Exception as exc:
        logger.exception("Golden workflow failed workflow_id=%s", workflow_id)
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {exc}") from exc


@app.get("/replays")
def replays() -> list[dict[str, str]]:
    return list_replays()
