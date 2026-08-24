import {Card} from "@/components/ui";
import type {WorkflowRun} from "@/schemas/types";

export function ReportViewer({run}: {run: WorkflowRun}) {
  return (
    <Card>
      <div className="text-sm text-muted">AI Health Report</div>
      <h2 className="mt-1 text-xl font-semibold">{run.report.title}</h2>
      <p className="mt-3 text-sm text-muted">{run.report.risk_summary}</p>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div>
          <div className="text-sm font-semibold">Failure Modes</div>
          <ul className="mt-2 space-y-2 text-sm text-muted">
            {run.report.key_weaknesses.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
        <div>
          <div className="text-sm font-semibold">Suggested Next Steps</div>
          <ul className="mt-2 space-y-2 text-sm text-muted">
            {run.report.recommended_next_steps.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
      </div>
    </Card>
  );
}
