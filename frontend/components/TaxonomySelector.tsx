import {Card} from "@/components/ui";

const fields = ["AI System", "Pillar", "Supporting Practice", "Use Case"];

export function TaxonomySelector() {
  return (
    <Card>
      <div className="mb-4 text-sm font-semibold">Taxonomy Selector</div>
      <div className="grid gap-3 md:grid-cols-2">
        {fields.map((field) => (
          <label className="text-sm" key={field}>
            <span className="mb-1 block text-muted">{field}</span>
            <select className="w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-ink">
              <option>{field === "AI System" ? "Fraud detection AI" : field === "Pillar" ? "Risk" : field === "Supporting Practice" ? "Adversarial testing" : "Adversarial testing for fraud scoring"}</option>
            </select>
          </label>
        ))}
      </div>
    </Card>
  );
}
