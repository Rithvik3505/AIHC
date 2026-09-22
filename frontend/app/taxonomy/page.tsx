import {TaxonomyBrowser} from "@/components/TaxonomyBrowser";
import {Card, SectionTitle} from "@/components/ui";
import type {TaxonomyRegistry} from "@/schemas/types";

async function loadTaxonomyRegistry(): Promise<TaxonomyRegistry | null> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
  try {
    const response = await fetch(`${baseUrl}/registries/taxonomy_registry`, {cache: "no-store"});
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export default async function TaxonomyPage() {
  const registry = await loadTaxonomyRegistry();
  return (
    <div>
      <SectionTitle
        title="Taxonomy"
        subtitle="Live registry view of the Lendingtech diagnostic library: 520 specified tests, with 24 Phase 2C executable evaluator procedures."
      />
      {registry ? (
        <TaxonomyBrowser registry={registry} />
      ) : (
        <Card>
          <div className="text-sm font-semibold">Backend taxonomy registry unavailable</div>
          <p className="mt-2 text-sm text-muted">Start the FastAPI backend and reload this page to inspect the live generated taxonomy.</p>
        </Card>
      )}
    </div>
  );
}
