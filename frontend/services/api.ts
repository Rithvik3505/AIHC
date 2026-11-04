import type {EvidenceContract, EvidenceMode, EvidenceValidation, TaxonomyRegistry, WorkflowDefinition, WorkflowRun} from "@/schemas/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function parseError(response: Response): Promise<string> {
  const text = await response.text();
  try {
    const payload = JSON.parse(text) as {detail?: unknown; message?: unknown};
    return String(payload.detail ?? payload.message ?? text);
  } catch {
    return text || response.statusText;
  }
}

function explainFetchFailure(error: unknown, url: string): Error {
  if (error instanceof TypeError && error.message === "Failed to fetch") {
    return new Error(
      `Backend request did not complete. Check that ${API_BASE} is reachable and that FastAPI CORS allows the frontend origin. URL: ${url}`
    );
  }
  if (error instanceof Error) {
    return error;
  }
  return new Error(`Unknown request failure for ${url}`);
}

export async function runWorkflow(
  workflowId: string,
  request: {evidence_mode: EvidenceMode; payload?: Record<string, unknown>; selected_test_ids: string[]}
): Promise<WorkflowRun> {
  const url = `${API_BASE}/workflows/${workflowId}/run`;
  console.debug("[AI Health Check] runWorkflow request", {url, method: "POST", evidenceMode: request.evidence_mode});
  try {
    const response = await fetch(url, {
    method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(request)
    });
    console.debug("[AI Health Check] runWorkflow response", {url, status: response.status, ok: response.ok});
    if (!response.ok) {
      throw new Error(`Workflow failed (${response.status}): ${await parseError(response)}`);
    }
    return response.json();
  } catch (error) {
    console.error("[AI Health Check] runWorkflow failed", {url, error});
    throw explainFetchFailure(error, url);
  }
}

export async function getEvidenceContract(workflowId: string): Promise<EvidenceContract> {
  const url = `${API_BASE}/workflows/${workflowId}/evidence-contract`;
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Evidence contract failed (${response.status}): ${await parseError(response)}`);
    return response.json();
  } catch (error) {
    throw explainFetchFailure(error, url);
  }
}

export async function validateWorkflowEvidence(
  workflowId: string,
  request: {evidence_mode: EvidenceMode; payload: Record<string, unknown>; selected_test_ids: string[]}
): Promise<EvidenceValidation> {
  const url = `${API_BASE}/workflows/${workflowId}/validate`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(request)
    });
    if (!response.ok) throw new Error(`Evidence validation failed (${response.status}): ${await parseError(response)}`);
    return response.json();
  } catch (error) {
    throw explainFetchFailure(error, url);
  }
}

export async function uploadWorkflowEvidence(workflowId: string, file: File): Promise<EvidenceValidation> {
  const url = `${API_BASE}/workflows/${workflowId}/upload`;
  const form = new FormData();
  form.append("file", file);
  try {
    const response = await fetch(url, {method: "POST", body: form});
    if (!response.ok) throw new Error(`Evidence upload failed (${response.status}): ${await parseError(response)}`);
    return response.json();
  } catch (error) {
    throw explainFetchFailure(error, url);
  }
}

export async function getWorkflows(): Promise<WorkflowDefinition[]> {
  const url = `${API_BASE}/workflows`;
  console.debug("[AI Health Check] getWorkflows request", {url, method: "GET"});
  try {
    const response = await fetch(url);
    console.debug("[AI Health Check] getWorkflows response", {url, status: response.status, ok: response.ok});
    if (!response.ok) {
      throw new Error(`Workflow list failed (${response.status}): ${await parseError(response)}`);
    }
    return response.json();
  } catch (error) {
    console.error("[AI Health Check] getWorkflows failed", {url, error});
    throw explainFetchFailure(error, url);
  }
}

export async function getTaxonomyRegistry(): Promise<TaxonomyRegistry> {
  const url = `${API_BASE}/registries/taxonomy_registry`;
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Taxonomy registry failed (${response.status}): ${await parseError(response)}`);
    }
    return response.json();
  } catch (error) {
    throw explainFetchFailure(error, url);
  }
}
