import {Card} from "@/components/ui";

export function RecommendationPanel({items}: {items: string[]}) {
  return (
    <Card>
      <div className="mb-4 text-sm font-semibold">Recommendations</div>
      <div className="space-y-2">
        {items.map((item) => (
          <div className="rounded-md bg-trust/10 px-3 py-2 text-sm text-ink" key={item}>{item}</div>
        ))}
      </div>
    </Card>
  );
}
