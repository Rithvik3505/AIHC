"use client";

import {Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis} from "recharts";
import {Card} from "@/components/ui";

const data = [
  {pillar: "Risk", score: 58},
  {pillar: "Reliability", score: 72},
  {pillar: "Data", score: 69},
  {pillar: "Explain", score: 76},
  {pillar: "Gov", score: 64}
];

export function PillarBreakdownChart() {
  return (
    <Card>
      <div className="mb-4 text-sm font-semibold">Pillar Breakdown</div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke="#263541" />
            <XAxis dataKey="pillar" stroke="#9fb0c0" />
            <YAxis stroke="#9fb0c0" />
            <Tooltip contentStyle={{background: "#17212b", border: "1px solid rgba(255,255,255,.1)"}} />
            <Bar dataKey="score" fill="#36c2a3" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
