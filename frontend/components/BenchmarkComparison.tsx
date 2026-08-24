"use client";

import {Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis} from "recharts";
import {Card} from "@/components/ui";

export function BenchmarkComparison({score, median, topQuartile, distribution}: {score: number; median: number; topQuartile: number; distribution: number[]}) {
  const data = distribution.map((value, index) => ({peer: index + 1, score: value}));
  return (
    <Card>
      <div className="mb-3 flex items-start justify-between gap-4">
        <div>
          <div className="text-sm font-semibold">Benchmark Comparison</div>
          <div className="mt-1 text-sm text-muted">Industry median {median} · Top quartile {topQuartile}</div>
        </div>
        <div className="rounded-md bg-signal/10 px-3 py-2 text-sm text-signal">You: {score}</div>
      </div>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="peer" stroke="#9fb0c0" />
            <YAxis stroke="#9fb0c0" />
            <Tooltip contentStyle={{background: "#17212b", border: "1px solid rgba(255,255,255,.1)"}} />
            <ReferenceLine y={score} stroke="#ef596f" />
            <Line type="monotone" dataKey="score" stroke="#5aa9ff" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
