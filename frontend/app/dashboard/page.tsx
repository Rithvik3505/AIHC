import {AIHealthScoreCard} from "@/components/AIHealthScoreCard";
import {BenchmarkComparison} from "@/components/BenchmarkComparison";
import {DiagnosticInsightPanel} from "@/components/DiagnosticInsightPanel";
import {PillarBreakdownChart} from "@/components/PillarBreakdownChart";
import {RecommendationPanel} from "@/components/RecommendationPanel";
import {RiskMeter} from "@/components/RiskMeter";
import {Card, SectionTitle} from "@/components/ui";
import {demoRun} from "@/features/demoData";

export default function DashboardPage() {
  return (
    <div>
      <SectionTitle title="AI Assurance Dashboard" subtitle="Static demonstration view using synthetic Phase 1 evaluation data." />
      <Card className="mb-5">
        <div className="text-sm text-muted">Dashboard figures are illustrative demo results, not persisted customer evidence or empirical industry benchmarks.</div>
      </Card>
      <div className="grid gap-5 lg:grid-cols-[1.1fr_.9fr]">
        <div className="space-y-5">
          <AIHealthScoreCard score={demoRun.evaluation.aggregate_score} risk={demoRun.evaluation.aggregate_risk_level} />
          <PillarBreakdownChart />
          <DiagnosticInsightPanel outputs={demoRun.evaluation.outputs} />
        </div>
        <div className="space-y-5">
          <RiskMeter score={demoRun.evaluation.aggregate_score} />
          <BenchmarkComparison score={demoRun.benchmark.score} median={demoRun.benchmark.synthetic_reference_median ?? undefined} topQuartile={demoRun.benchmark.synthetic_reference_top_quartile ?? undefined} percentile={demoRun.benchmark.synthetic_percentile} distribution={demoRun.benchmark.distribution} provenance={demoRun.benchmark.provenance} limitations={demoRun.benchmark.limitations} externalStatus={demoRun.benchmark.external_reference_status} industryReason={demoRun.benchmark.industry_peer_distribution?.reason} />
          <RecommendationPanel items={demoRun.report.recommended_next_steps} />
        </div>
      </div>
    </div>
  );
}
