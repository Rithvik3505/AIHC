import type {TaxonomyTest} from "@/schemas/types";

const badgeTone: Record<string, string> = {
  Ready: "bg-trust/15 text-trust border-trust/25",
  Implemented: "bg-trust/15 text-trust border-trust/25",
  "Synthetic reference": "bg-signal/15 text-signal border-signal/25",
  Assisted: "bg-signal/15 text-signal border-signal/25",
  Partial: "bg-warning/15 text-warning border-warning/25",
  Planned: "bg-warning/15 text-warning border-warning/25",
  "Not supported": "bg-risk/15 text-risk border-risk/25",
  None: "bg-risk/15 text-risk border-risk/25"
};

function Badge({label, value}: {label: string; value: string}) {
  const tone = badgeTone[value] ?? "bg-white/[0.04] text-muted border-white/10";
  return (
    <div className={`rounded-md border px-2 py-1 ${tone}`}>
      <span className="text-[11px] uppercase tracking-normal opacity-75">{label}: </span>
      <span className="text-xs font-medium">{value}</span>
    </div>
  );
}

function ListSection({title, items}: {title: string; items: string[]}) {
  return (
    <details className="rounded-md border border-white/10 bg-white/[0.02] p-3">
      <summary className="cursor-pointer text-sm font-semibold">{title}</summary>
      <ul className="mt-2 space-y-2 text-sm text-muted">
        {items.map((item, index) => <li key={`${title}-${index}`}>{item}</li>)}
      </ul>
    </details>
  );
}

export function TaxonomyTestDetailPanel({test}: {test: TaxonomyTest}) {
  const metadata = test.implementation_metadata;
  return (
    <div className="rounded-md border border-white/10 bg-panel p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-xs uppercase text-muted">{test.test_type} test / {test.id}</div>
          <div className="mt-1 text-sm font-semibold">{test.name}</div>
          <p className="mt-2 text-sm text-muted">{test.objective}</p>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <Badge label="Implementation" value={metadata.implementation_status} />
        <Badge label="Evaluator" value={metadata.evaluator_status} />
        <Badge label="Workflow" value={metadata.workflow_status} />
        <Badge label="Evidence" value={metadata.evidence_type} />
        <Badge label="Dataset" value={metadata.dataset_source} />
        <Badge label="Benchmark" value={metadata.benchmark_status} />
        <Badge label="Upload" value={metadata.customer_upload} />
        <Badge label="Automation" value={metadata.automation_level} />
      </div>
      <div className="mt-4 grid gap-3">
        <div className="rounded-md border border-white/10 bg-white/[0.02] p-3 text-sm">
          <div className="font-semibold">Technique</div>
          <div className="mt-1 text-muted">{test.technique}</div>
        </div>
        <ListSection title="Inputs Required" items={test.inputs_required} />
        <ListSection title="Preprocessing Steps" items={test.preprocessing_steps} />
        <ListSection title="Perturbation Strategy" items={test.perturbation_strategy} />
        <ListSection title="Method" items={test.method} />
        <ListSection title="Primary Metrics" items={test.primary_metrics} />
        <ListSection title="Secondary Metrics" items={test.secondary_metrics} />
        <ListSection title="Benchmark Interpretation" items={test.benchmark_interpretation} />
        <ListSection title="Failure Criteria" items={test.failure_criteria} />
        <ListSection title="Recommendation Logic" items={test.recommendation_logic} />
        <details className="rounded-md border border-white/10 bg-white/[0.02] p-3">
          <summary className="cursor-pointer text-sm font-semibold">Implementation Metadata And References</summary>
          <dl className="mt-2 grid gap-2 text-sm text-muted md:grid-cols-2">
            {Object.entries(metadata).map(([key, value]) => (
              <div key={key}>
                <dt className="text-xs uppercase text-muted">{key.replaceAll("_", " ")}</dt>
                <dd className="break-words text-ink">{value}</dd>
              </div>
            ))}
          </dl>
        </details>
      </div>
    </div>
  );
}
