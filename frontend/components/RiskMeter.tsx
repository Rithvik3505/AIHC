export function RiskMeter({score}: {score: number | null}) {
  const safeScore = score ?? 0;
  const color = safeScore >= 80 ? "bg-trust" : safeScore >= 60 ? "bg-warning" : "bg-risk";
  return (
    <div>
      <div className="mb-2 flex justify-between text-sm text-muted">
        <span>Risk posture</span>
        <span>{score === null ? "N/A" : `${score}/100`}</span>
      </div>
      <div className="h-3 rounded-full bg-white/10">
        <div className={`h-3 rounded-full ${color}`} style={{width: `${safeScore}%`}} />
      </div>
    </div>
  );
}
