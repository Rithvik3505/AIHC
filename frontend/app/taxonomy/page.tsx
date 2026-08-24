import {TaxonomyTestDetailPanel} from "@/components/TaxonomyTestDetailPanel";
import {Card, SectionTitle} from "@/components/ui";

type TaxonomyRegistry = {
  taxonomy: {
    fintech_segment: string;
    product_phase: string;
    ai_systems: Array<{
      name: string;
      typical_use: string;
      pillars: Array<{
        name: string;
        practices: Array<{
          name: string;
          category: "A" | "B";
          orientation: "Horizontal" | "Hybrid" | "Vertical";
          meaningfulness: Record<string, number>;
          use_cases: Array<{
            id: string;
            name: string;
            description: string;
            tests: Array<Parameters<typeof TaxonomyTestDetailPanel>[0]["test"]>;
          }>;
        }>;
      }>;
    }>;
  };
};

async function loadTaxonomyRegistry(): Promise<TaxonomyRegistry> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
  const response = await fetch(`${baseUrl}/registries/taxonomy_registry`, {cache: "no-store"});
  if (!response.ok) {
    throw new Error(`Unable to load taxonomy registry: ${response.status}`);
  }
  return response.json();
}

function PracticeBadges({category, orientation}: {category: string; orientation: string}) {
  return (
    <div className="flex flex-wrap gap-2">
      <span className="rounded-md border border-signal/25 bg-signal/15 px-2 py-1 text-xs text-signal">Category {category}</span>
      <span className="rounded-md border border-trust/25 bg-trust/15 px-2 py-1 text-xs text-trust">{orientation}</span>
    </div>
  );
}

export default async function TaxonomyPage() {
  const registry = await loadTaxonomyRegistry();
  const systems = registry.taxonomy.ai_systems;
  const useCaseCount = systems.flatMap((system) =>
    system.pillars.flatMap((pillar) => pillar.practices.flatMap((practice) => practice.use_cases))
  ).length;

  return (
    <div>
      <SectionTitle
        title="Taxonomy"
        subtitle="Registry-driven Lendingtech assurance taxonomy with horizontal primitives and vertical failure intelligence."
      />
      <div className="mb-5 grid gap-4 md:grid-cols-3">
        <Card>
          <div className="text-sm text-muted">AI Systems</div>
          <div className="mt-1 text-3xl font-semibold">{systems.length}</div>
        </Card>
        <Card>
          <div className="text-sm text-muted">Meaningful Use Cases</div>
          <div className="mt-1 text-3xl font-semibold">{useCaseCount}</div>
        </Card>
        <Card>
          <div className="text-sm text-muted">Product Phase</div>
          <div className="mt-1 text-lg font-semibold">{registry.taxonomy.product_phase}</div>
        </Card>
      </div>
      <div className="space-y-5">
        {systems.map((system) => (
          <Card key={system.name}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">{system.name}</h2>
                <p className="mt-1 text-sm text-muted">{system.typical_use}</p>
              </div>
              <span className="rounded-md bg-white/[0.04] px-2 py-1 text-xs text-muted">{registry.taxonomy.fintech_segment}</span>
            </div>
            <div className="mt-5 space-y-4">
              {system.pillars.map((pillar) => (
                <div className="rounded-md border border-white/10 bg-surface/40 p-4" key={`${system.name}-${pillar.name}`}>
                  <div className="text-sm font-semibold">{pillar.name}</div>
                  <div className="mt-3 space-y-4">
                    {pillar.practices.map((practice) => (
                      <div className="rounded-md border border-white/10 bg-white/[0.02] p-4" key={`${system.name}-${pillar.name}-${practice.name}`}>
                        <div className="flex flex-wrap items-center justify-between gap-3">
                          <div className="text-sm font-semibold">{practice.name}</div>
                          <PracticeBadges category={practice.category} orientation={practice.orientation} />
                        </div>
                        {practice.use_cases.map((useCase) => (
                          <div className="mt-4" key={useCase.id}>
                            <div className="text-sm text-muted">{useCase.name}</div>
                            <div className="mt-3 grid gap-3">
                              {useCase.tests.map((test) => (
                                <TaxonomyTestDetailPanel test={test} key={test.id} />
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
