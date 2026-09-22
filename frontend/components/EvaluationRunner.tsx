"use client";

import {useState} from "react";
import {Button, Card} from "@/components/ui";
import {runWorkflow} from "@/services/api";
import type {WorkflowDefinition, WorkflowRun} from "@/schemas/types";

export function EvaluationRunner({workflow, onResult}: {workflow: WorkflowDefinition | null; onResult: (result: WorkflowRun) => void}) {
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function run() {
    if (!workflow) return;
    setRunning(true);
    setError(null);
    try {
      onResult(await runWorkflow(workflow.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Workflow failed");
    } finally {
      setRunning(false);
    }
  }
  return (
    <Card>
      <div className="mb-4 text-sm font-semibold">Evaluation Runner</div>
      <p className="mb-3 text-sm text-muted">Runs the selected Golden Workflow with deterministic synthetic demo evidence.</p>
      <Button onClick={run} disabled={running || !workflow}>{running ? "Running diagnostics..." : "Run Selected Workflow"}</Button>
      {error ? <p className="mt-3 text-sm text-risk">{error}</p> : null}
    </Card>
  );
}
