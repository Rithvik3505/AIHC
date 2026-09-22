import {BenchmarkComparison} from "@/components/BenchmarkComparison";
import {Card, SectionTitle} from "@/components/ui";
import {demoRun} from "@/features/demoData";

export default function BenchmarksPage() {
  return (
    <div>
      <SectionTitle title="Benchmarks" subtitle="Illustrative synthetic reference distributions; real peer benchmarking is not implemented." />
      <div className="grid gap-5 lg:grid-cols-[1fr_.8fr]">
        <BenchmarkComparison score={demoRun.benchmark.score} median={demoRun.benchmark.industry_median} topQuartile={demoRun.benchmark.top_quartile} distribution={demoRun.benchmark.distribution} provenance={demoRun.benchmark.provenance} limitations={demoRun.benchmark.limitations} />
        <Card>
          <div className="text-sm font-semibold">Benchmark Scope</div>
          <div className="mt-4 space-y-3 text-sm text-muted">
            <p>Reference group: Lendingtech / Fraud Detection / Synthetic Phase 1 demo</p>
            <p>Illustrative synthetic percentile: {demoRun.benchmark.percentile}</p>
            <p>Customer cohort distributions and anonymized cross-company benchmarks are planned capabilities, not current evidence.</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
