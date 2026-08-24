import {AIHealthScoreCard} from "@/components/AIHealthScoreCard";
import {BenchmarkComparison} from "@/components/BenchmarkComparison";
import {DiagnosticInsightPanel} from "@/components/DiagnosticInsightPanel";
import {PillarBreakdownChart} from "@/components/PillarBreakdownChart";
import {RecommendationPanel} from "@/components/RecommendationPanel";
import {RiskMeter} from "@/components/RiskMeter";
import {SectionTitle} from "@/components/ui";
import {demoRun} from "@/features/demoData";

export default function DashboardPage() {
  return (
    <div>
      <SectionTitle title="AI Assurance Dashboard" subtitle="Trust diagnostics for high-risk Lendingtech AI systems." />
      <div className="grid gap-5 lg:grid-cols-[1.1fr_.9fr]">
        <div className="space-y-5">
          <AIHealthScoreCard score={demoRun.evaluation.aggregate_score} risk={demoRun.evaluation.aggregate_risk_level} />
          <PillarBreakdownChart />
          <DiagnosticInsightPanel outputs={demoRun.evaluation.outputs} />
        </div>
        <div className="space-y-5">
          <RiskMeter score={demoRun.evaluation.aggregate_score} />
          <BenchmarkComparison score={demoRun.benchmark.score} median={demoRun.benchmark.industry_median} topQuartile={demoRun.benchmark.top_quartile} distribution={demoRun.benchmark.distribution} />
          <RecommendationPanel items={demoRun.report.recommended_next_steps} />
        </div>
      </div>
    </div>
  );
}
