"use client";

import {Suspense, useEffect, useMemo, useState} from "react";
import {useSearchParams} from "next/navigation";
import {EvaluationRunner} from "@/components/EvaluationRunner";
import {ReportViewer} from "@/components/ReportViewer";
import {TaxonomySelector} from "@/components/TaxonomySelector";
import {UploadPanel} from "@/components/UploadPanel";
import {Card, SectionTitle} from "@/components/ui";
import {getWorkflows} from "@/services/api";
import type {WorkflowDefinition, WorkflowRun} from "@/schemas/types";

function EvaluatePageContent() {
  const searchParams = useSearchParams();
  const requestedWorkflow = searchParams.get("workflow");
  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [selectionNotice, setSelectionNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [run, setRun] = useState<WorkflowRun | null>(null);

  useEffect(() => {
    getWorkflows()
      .then((items) => {
        setWorkflows(items);
        const requested = requestedWorkflow ? items.find((item) => item.id === requestedWorkflow) : null;
        if (requested) {
          setSelectedId(requested.id);
        } else {
          setSelectedId(items[0]?.id ?? "");
          setSelectionNotice(requestedWorkflow ? `Unknown workflow "${requestedWorkflow}". Showing the first registered workflow.` : "Defaulting to the first registered Golden Workflow.");
        }
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Unable to load workflows."));
  }, [requestedWorkflow]);

  const selectedWorkflow = useMemo(() => workflows.find((workflow) => workflow.id === selectedId) ?? null, [selectedId, workflows]);

  return (
    <div>
      <SectionTitle title="Run Diagnostics" subtitle="Select one registered Golden Workflow and run deterministic synthetic demo evidence through the Phase 2C evaluators." />
      {error ? <Card className="mb-5"><p className="text-sm text-risk">{error}</p></Card> : null}
      <div className="grid gap-5 lg:grid-cols-[.9fr_1.1fr]">
        <div className="space-y-5">
          <TaxonomySelector workflows={workflows} selectedWorkflow={selectedWorkflow} onSelect={(id) => { setSelectedId(id); setRun(null); setSelectionNotice(null); }} error={selectionNotice} />
          <UploadPanel workflow={selectedWorkflow} />
          <EvaluationRunner workflow={selectedWorkflow} onResult={setRun} />
        </div>
        {run ? (
          <ReportViewer run={run} />
        ) : (
          <Card>
            <div className="text-sm font-semibold">No evaluation run yet</div>
            <p className="mt-2 text-sm text-muted">Choose a Golden Workflow and run it to see structured Phase 2C results, coverage, findings, recommendations, limitations, and synthetic benchmark eligibility.</p>
          </Card>
        )}
      </div>
    </div>
  );
}

export default function EvaluatePage() {
  return (
    <Suspense fallback={<Card><div className="text-sm text-muted">Loading workflows...</div></Card>}>
      <EvaluatePageContent />
    </Suspense>
  );
}
