import {Card} from "@/components/ui";
import type {TestOutput} from "@/schemas/types";

export function DiagnosticInsightPanel({outputs}: {outputs: TestOutput[]}) {
  return (
    <Card>
      <div className="mb-4 text-sm font-semibold">Diagnostic Insights</div>
      <div className="space-y-3">
        {outputs.map((output, index) => (
          <div className="rounded-md border border-white/10 bg-white/[0.03] p-3" key={`${output.insight}-${index}`}>
            <div className="text-sm font-medium">{output.metadata.practice} · {output.metadata.test_type}</div>
            <p className="mt-1 text-sm text-muted">{output.insight}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
