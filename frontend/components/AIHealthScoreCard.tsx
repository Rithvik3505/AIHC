import {ShieldCheck} from "lucide-react";
import {Card} from "@/components/ui";

export function AIHealthScoreCard({score, risk}: {score: number; risk: string}) {
  return (
    <Card className="flex items-center justify-between">
      <div>
        <div className="text-sm text-muted">Overall AI Health Score</div>
        <div className="mt-2 text-5xl font-semibold">{score}</div>
        <div className="mt-2 text-sm text-muted">Aggregate Risk: <span className="text-ink">{risk}</span></div>
      </div>
      <div className="rounded-full border border-trust/40 bg-trust/10 p-4 text-trust">
        <ShieldCheck size={42} />
      </div>
    </Card>
  );
}
