import {Card} from "@/components/ui";
import type {TestOutput, WorkflowRun} from "@/schemas/types";

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "Not available";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(3);
  if (typeof value === "boolean") return value ? "true" : "false";
  if (Array.isArray(value)) return value.map(formatValue).join(", ");
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>).map(([key, item]) => `${key}: ${formatValue(item)}`).join("; ");
  }
  return String(value);
}

function KeyValueList({items}: {items: Record<string, unknown>}) {
  return (
    <dl className="grid gap-2 text-sm md:grid-cols-2">
      {Object.entries(items).map(([key, value]) => (
        <div key={key}>
          <dt className="text-xs uppercase text-muted">{key.replaceAll("_", " ")}</dt>
          <dd className="break-words text-ink">{formatValue(value)}</dd>
        </div>
      ))}
    </dl>
  );
}

function TestResult({output}: {output: TestOutput}) {
  return (
    <details className="rounded-md border border-white/10 bg-white/[0.03] p-4">
      <summary className="cursor-pointer text-sm font-semibold">
        {output.metadata.test_id ?? output.metadata.practice} / {output.metadata.test_type} / {output.execution_status}
      </summary>
      <div className="mt-3 grid gap-3">
        <KeyValueList items={{
          evaluator_id: output.evaluator_id,
          diagnostic_family: output.metadata.diagnostic_family,
          evidence_status: output.evidence_status,
          score: output.score ?? "Not assessable",
          risk_level: output.risk_level ?? "Not assessable",
          sample_size: output.sample_size
        }} />
        <details className="rounded-md border border-white/10 p-3"><summary className="cursor-pointer text-sm font-medium">Raw Metrics</summary><div className="mt-2"><KeyValueList items={output.raw_metrics} /></div></details>
        <details className="rounded-md border border-white/10 p-3"><summary className="cursor-pointer text-sm font-medium">Metric Interpretation</summary><div className="mt-2"><KeyValueList items={output.metric_interpretation} /></div></details>
        <details className="rounded-md border border-white/10 p-3"><summary className="cursor-pointer text-sm font-medium">Coverage And Thresholds</summary><div className="mt-2"><KeyValueList items={{...output.coverage, ...output.thresholds}} /></div></details>
        <div>
          <div className="text-sm font-semibold">Findings</div>
          <ul className="mt-1 space-y-1 text-sm text-muted">{output.findings.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
        <p className="text-sm text-muted">{output.insight}</p>
        <div>
          <div className="text-sm font-semibold">Recommendations</div>
          <ul className="mt-1 space-y-1 text-sm text-muted">{output.recommendation.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
        {output.limitations.length ? (
          <div>
            <div className="text-sm font-semibold">Limitations</div>
            <ul className="mt-1 space-y-1 text-sm text-muted">{output.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
          </div>
        ) : null}
        <details className="rounded-md border border-white/10 p-3"><summary className="cursor-pointer text-sm font-medium">Execution Metadata</summary><div className="mt-2"><KeyValueList items={output.execution_metadata} /></div></details>
      </div>
    </details>
  );
}

export function ReportViewer({run}: {run: WorkflowRun}) {
  const benchmarkEligible = run.benchmark.eligible !== false;
  const coverage = run.evaluation.coverage;
  const hasPartialCoverage = coverage.score_coverage_percentage < 100;
  return (
    <Card>
      <div className="text-sm text-muted">Synthetic Demo AI Health Report</div>
      <h2 className="mt-1 text-xl font-semibold">{run.report.title}</h2>
      <p className="mt-3 text-sm text-muted">{run.report.risk_summary}</p>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <div className="rounded-md border border-white/10 bg-white/[0.03] p-3">
          <div className="text-xs uppercase text-muted">Aggregate Score</div>
          <div className="mt-1 text-2xl font-semibold">{run.evaluation.aggregate_score ?? "Not assessable"}</div>
        </div>
        <div className="rounded-md border border-white/10 bg-white/[0.03] p-3">
          <div className="text-xs uppercase text-muted">Aggregate Risk</div>
          <div className="mt-1 text-2xl font-semibold">{run.evaluation.aggregate_risk_level ?? "Not assessable"}</div>
        </div>
        <div className="rounded-md border border-white/10 bg-white/[0.03] p-3">
          <div className="text-xs uppercase text-muted">Score Coverage</div>
          <div className="mt-1 text-2xl font-semibold">{coverage.score_coverage_percentage}%</div>
        </div>
      </div>
      {hasPartialCoverage ? <p className="mt-3 text-sm text-warning">Partial coverage: unassessable tests were excluded from aggregate scoring.</p> : null}
      <div className="mt-4">
        <KeyValueList items={{
          selected_tests: coverage.selected_test_count,
          completed: coverage.completed_count,
          insufficient_evidence: coverage.insufficient_evidence_count,
          not_implemented: coverage.not_implemented_count,
          failed: coverage.failed_count,
          benchmark_eligible: benchmarkEligible,
          benchmark_reason: run.benchmark.reason
        }} />
      </div>
      <div className="mt-5 space-y-3">
        {run.evaluation.outputs.map((output) => <TestResult output={output} key={output.metadata.test_id ?? output.insight} />)}
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-2">
        <div>
          <div className="text-sm font-semibold">Report Findings</div>
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
      <p className="mt-4 text-xs text-muted">This report is based on synthetic demo evidence. It is not a certification, regulatory approval, or customer assurance certificate.</p>
    </Card>
  );
}
