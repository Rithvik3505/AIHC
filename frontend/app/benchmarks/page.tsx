import {BenchmarkComparison} from "@/components/BenchmarkComparison";
import {Card, SectionTitle} from "@/components/ui";
import {demoRun} from "@/features/demoData";

export default function BenchmarksPage() {
  return (
    <div>
      <SectionTitle title="Benchmarks" subtitle="Synthetic benchmark distributions now; anonymized cross-startup intelligence later." />
      <div className="grid gap-5 lg:grid-cols-[1fr_.8fr]">
        <BenchmarkComparison score={demoRun.benchmark.score} median={demoRun.benchmark.industry_median} topQuartile={demoRun.benchmark.top_quartile} distribution={demoRun.benchmark.distribution} />
        <Card>
          <div className="text-sm font-semibold">Benchmark Readiness</div>
          <div className="mt-4 space-y-3 text-sm text-muted">
            <p>Peer group: Lendingtech · Fraud Detection · Phase 1 Startup</p>
            <p>Percentile rank: {demoRun.benchmark.percentile}</p>
            <p>Future moat: anonymized aggregate diagnostics across startup cohorts.</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
