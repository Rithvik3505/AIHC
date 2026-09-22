"use client";

import {Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis} from "recharts";
import {Card} from "@/components/ui";

export function BenchmarkComparison({
  score,
  median,
  topQuartile,
  distribution,
  provenance,
  limitations
}: {
  score: number | null;
  median?: number;
  topQuartile?: number;
  distribution: number[];
  provenance?: string;
  limitations?: string[];
}) {
  const data = distribution.map((value, index) => ({peer: index + 1, score: value}));
  const hasDistribution = data.length > 0;

  return (
    <Card>
      <div className="mb-3 flex items-start justify-between gap-4">
        <div>
          <div className="text-sm font-semibold">Synthetic Reference Comparison</div>
          <div className="mt-1 text-sm text-muted">
            Illustrative synthetic median {median ?? "N/A"} / synthetic top quartile {topQuartile ?? "N/A"}
          </div>
        </div>
        <div className="rounded-md bg-signal/10 px-3 py-2 text-sm text-signal">You: {score === null ? "N/A" : score}</div>
      </div>
      <div className="h-56">
        {hasDistribution ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <XAxis dataKey="peer" stroke="#9fb0c0" />
              <YAxis stroke="#9fb0c0" />
              <Tooltip contentStyle={{background: "#17212b", border: "1px solid rgba(255,255,255,.1)"}} />
              {score !== null ? <ReferenceLine y={score} stroke="#ef596f" /> : null}
              <Line type="monotone" dataKey="score" stroke="#5aa9ff" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full items-center justify-center rounded-md border border-white/10 text-sm text-muted">
            No benchmark distribution is available for this workflow.
          </div>
        )}
      </div>
      {provenance ? <p className="mt-3 text-xs text-muted">{provenance}</p> : null}
      {limitations?.length ? <p className="mt-2 text-xs text-muted">{limitations.join(" / ")}</p> : null}
    </Card>
  );
}
