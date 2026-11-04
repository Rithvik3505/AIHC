import {BenchmarkComparison} from "@/components/BenchmarkComparison";
import {Card, SectionTitle} from "@/components/ui";
import {demoRun} from "@/features/demoData";

export default function BenchmarksPage() {
  return (
    <div>
      <SectionTitle title="Benchmarks" subtitle="Illustrative synthetic reference distributions; real peer benchmarking is not implemented." />
      <div className="grid gap-5 lg:grid-cols-[1fr_.8fr]">
        <BenchmarkComparison score={demoRun.benchmark.score} median={demoRun.benchmark.synthetic_reference_median ?? undefined} topQuartile={demoRun.benchmark.synthetic_reference_top_quartile ?? undefined} percentile={demoRun.benchmark.synthetic_percentile} distribution={demoRun.benchmark.distribution} provenance={demoRun.benchmark.provenance} limitations={demoRun.benchmark.limitations} externalStatus={demoRun.benchmark.external_reference_status} industryReason={demoRun.benchmark.industry_peer_distribution?.reason} />
        <Card>
          <div className="text-sm font-semibold">Benchmark Scope</div>
          <div className="mt-4 space-y-3 text-sm text-muted">
            <p>Reference group: Lendingtech / Fraud Detection / Synthetic Phase 1 demo</p>
            <p>Illustrative synthetic percentile: {demoRun.benchmark.synthetic_percentile}</p>
            <p>Customer cohort distributions and anonymized cross-company benchmarks are planned capabilities, not current evidence.</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
