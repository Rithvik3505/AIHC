import {Card} from "@/components/ui";

type ImplementationMetadata = {
  implementation_status: string;
  workflow_status: string;
  workflow_reference: string;
  evaluator_status: string;
  evaluator_reference: string;
  evidence_type: string;
  dataset_source: string;
  dataset_reference: string;
  benchmark_status: string;
  benchmark_reference: string;
  customer_upload: string;
  automation_level: string;
};

type TaxonomyTest = {
  id: string;
  name: string;
  test_type: "light" | "strong";
  objective: string;
  metrics: string[];
  implementation_metadata: ImplementationMetadata;
};

const badgeTone: Record<string, string> = {
  Ready: "bg-trust/15 text-trust border-trust/25",
  Implemented: "bg-trust/15 text-trust border-trust/25",
  Supported: "bg-trust/15 text-trust border-trust/25",
  Available: "bg-trust/15 text-trust border-trust/25",
  Assisted: "bg-signal/15 text-signal border-signal/25",
  "Synthetic Demo": "bg-signal/15 text-signal border-signal/25",
  "Public Dataset": "bg-signal/15 text-signal border-signal/25",
  Partial: "bg-warning/15 text-warning border-warning/25",
  Planned: "bg-warning/15 text-warning border-warning/25",
  "Not Supported": "bg-risk/15 text-risk border-risk/25",
  None: "bg-risk/15 text-risk border-risk/25"
};

function Badge({label, value}: {label: string; value: string}) {
  const tone = badgeTone[value] ?? "bg-white/[0.04] text-muted border-white/10";
  return (
    <div className={`rounded-md border px-2 py-1 ${tone}`}>
      <span className="text-[11px] uppercase tracking-wide opacity-75">{label}: </span>
      <span className="text-xs font-medium">{value}</span>
    </div>
  );
}

export function TaxonomyTestDetailPanel({test}: {test: TaxonomyTest}) {
  const metadata = test.implementation_metadata;
  return (
    <Card className="p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-xs uppercase text-muted">{test.test_type} test</div>
          <div className="mt-1 text-sm font-semibold">{test.name}</div>
          <p className="mt-2 text-sm text-muted">{test.objective}</p>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <Badge label="Implementation Status" value={metadata.implementation_status} />
        <Badge label="Workflow" value={metadata.workflow_status} />
        <Badge label="Evaluator" value={metadata.evaluator_status} />
        <Badge label="Evidence Type" value={metadata.evidence_type} />
        <Badge label="Dataset" value={metadata.dataset_source} />
        <Badge label="Benchmark" value={metadata.benchmark_status} />
        <Badge label="Customer Upload" value={metadata.customer_upload} />
        <Badge label="Automation Level" value={metadata.automation_level} />
      </div>
      <div className="mt-3 grid gap-2 text-xs text-muted md:grid-cols-3">
        <div>Workflow Ref: {metadata.workflow_reference}</div>
        <div>Evaluator Ref: {metadata.evaluator_reference}</div>
        <div>Dataset Ref: {metadata.dataset_reference}</div>
      </div>
    </Card>
  );
}
