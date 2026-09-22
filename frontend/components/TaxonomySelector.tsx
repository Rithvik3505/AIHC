import {Card} from "@/components/ui";
import type {WorkflowDefinition} from "@/schemas/types";

export function TaxonomySelector({
  workflows,
  selectedWorkflow,
  onSelect,
  error
}: {
  workflows: WorkflowDefinition[];
  selectedWorkflow: WorkflowDefinition | null;
  onSelect: (workflowId: string) => void;
  error?: string | null;
}) {
  return (
    <Card>
      <div className="mb-4 text-sm font-semibold">Golden Workflow</div>
      {error ? <p className="mb-3 text-sm text-warning">{error}</p> : null}
      <label className="text-sm">
        <span className="mb-1 block text-muted">Workflow</span>
        <select
          className="w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-ink"
          value={selectedWorkflow?.id ?? ""}
          onChange={(event) => onSelect(event.target.value)}
        >
          {workflows.map((workflow) => <option value={workflow.id} key={workflow.id}>{workflow.name}</option>)}
        </select>
      </label>
      {selectedWorkflow ? (
        <dl className="mt-4 grid gap-2 text-sm md:grid-cols-2">
          <div><dt className="text-muted">AI System</dt><dd>{selectedWorkflow.ai_system}</dd></div>
          <div><dt className="text-muted">Pillar</dt><dd>{selectedWorkflow.pillar}</dd></div>
          <div><dt className="text-muted">Supporting Practice</dt><dd>{selectedWorkflow.supporting_practice}</dd></div>
          <div><dt className="text-muted">Use Case</dt><dd>{selectedWorkflow.use_case}</dd></div>
          <div><dt className="text-muted">Automation</dt><dd>{selectedWorkflow.automation_level}</dd></div>
          <div><dt className="text-muted">Status</dt><dd>{selectedWorkflow.implementation_status}</dd></div>
          <div><dt className="text-muted">Evidence Mode</dt><dd>{selectedWorkflow.execution_mode ?? "synthetic_demo"}</dd></div>
          <div><dt className="text-muted">Evidence Contracts</dt><dd>{selectedWorkflow.supported_uploads.join(", ")}</dd></div>
          <div className="md:col-span-2"><dt className="text-muted">Report Template</dt><dd>{selectedWorkflow.report_template}</dd></div>
        </dl>
      ) : (
        <p className="mt-3 text-sm text-muted">No workflows are available from the backend.</p>
      )}
    </Card>
  );
}
