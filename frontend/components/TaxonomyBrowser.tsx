"use client";

import {useMemo, useState} from "react";
import {TaxonomyTestDetailPanel} from "@/components/TaxonomyTestDetailPanel";
import {Card} from "@/components/ui";
import type {TaxonomyRegistry, TaxonomySystem} from "@/schemas/types";

function statusMatches(value: string, filter: string) {
  return filter === "All" || value === filter;
}

export function TaxonomyBrowser({registry}: {registry: TaxonomyRegistry}) {
  const systems = registry.taxonomy.ai_systems;
  const [systemName, setSystemName] = useState(systems[0]?.name ?? "");
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("All");

  const selectedSystem = systems.find((system) => system.name === systemName) ?? systems[0];
  const counts = useMemo(() => summarize(systems), [systems]);
  const lowered = query.trim().toLowerCase();

  if (!selectedSystem) {
    return <Card><div className="text-sm text-muted">No taxonomy systems are available.</div></Card>;
  }

  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-4">
        <Card><div className="text-sm text-muted">AI Systems</div><div className="mt-1 text-3xl font-semibold">{counts.systems}</div></Card>
        <Card><div className="text-sm text-muted">Use Cases</div><div className="mt-1 text-3xl font-semibold">{counts.useCases}</div></Card>
        <Card><div className="text-sm text-muted">Tests</div><div className="mt-1 text-3xl font-semibold">{counts.tests}</div></Card>
        <Card><div className="text-sm text-muted">Executable Tests</div><div className="mt-1 text-3xl font-semibold">{counts.implementedEvaluators}</div></Card>
      </div>
      <Card>
        <div className="grid gap-3 md:grid-cols-[1fr_1fr_.7fr]">
          <label className="text-sm">
            <span className="mb-1 block text-muted">AI System</span>
            <select className="w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-ink" value={selectedSystem.name} onChange={(event) => setSystemName(event.target.value)}>
              {systems.map((system) => <option key={system.name}>{system.name}</option>)}
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-muted">Search</span>
            <input className="w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-ink" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Use case, test, metric, evaluator..." />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-muted">Implementation</span>
            <select className="w-full rounded-md border border-white/10 bg-surface px-3 py-2 text-ink" value={status} onChange={(event) => setStatus(event.target.value)}>
              {["All", "Partial", "Planned", "Ready"].map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
        </div>
      </Card>
      <Card>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold">{selectedSystem.name}</h2>
            <p className="mt-1 text-sm text-muted">{selectedSystem.typical_use}</p>
          </div>
          <span className="rounded-md border border-white/10 bg-white/[0.04] px-2 py-1 text-xs text-muted">{registry.taxonomy.fintech_segment}</span>
        </div>
        <div className="mt-5 space-y-3">
          {selectedSystem.pillars.map((pillar) => {
            const matchingPractices = pillar.practices.map((practice) => ({
              practice,
              useCases: practice.use_cases.filter((useCase) => {
                const text = JSON.stringify(useCase).toLowerCase();
                const implementation = useCase.tests[0]?.implementation_metadata.implementation_status ?? "";
                return (!lowered || text.includes(lowered)) && statusMatches(implementation, status);
              })
            })).filter((item) => item.useCases.length > 0);
            if (!matchingPractices.length) return null;
            return (
              <details className="rounded-md border border-white/10 bg-surface/40 p-4" key={pillar.name} open>
                <summary className="cursor-pointer text-sm font-semibold">{pillar.name}</summary>
                <div className="mt-3 space-y-4">
                  {matchingPractices.map(({practice, useCases}) => (
                    <details className="rounded-md border border-white/10 bg-white/[0.02] p-4" key={`${pillar.name}-${practice.name}`}>
                      <summary className="cursor-pointer text-sm font-semibold">
                        {practice.name} / Category {practice.category} / {practice.orientation}
                      </summary>
                      <div className="mt-3 space-y-4">
                        {useCases.map((useCase) => (
                          <details className="rounded-md border border-white/10 bg-panel p-4" key={useCase.id}>
                            <summary className="cursor-pointer text-sm font-semibold">{useCase.name}</summary>
                            <p className="mt-2 text-sm text-muted">{useCase.description}</p>
                            <div className="mt-3 grid gap-3">
                              {useCase.tests.map((test) => (
                                <details className="rounded-md border border-white/10 bg-white/[0.02] p-3" key={test.id}>
                                  <summary className="cursor-pointer text-sm font-medium">
                                    {test.test_type === "strong" ? "Strong Test" : "Light Test"} / {test.name}
                                  </summary>
                                  <div className="mt-3">
                                    <TaxonomyTestDetailPanel test={test} />
                                  </div>
                                </details>
                              ))}
                            </div>
                          </details>
                        ))}
                      </div>
                    </details>
                  ))}
                </div>
              </details>
            );
          })}
        </div>
      </Card>
    </div>
  );
}

function summarize(systems: TaxonomySystem[]) {
  let useCases = 0;
  let tests = 0;
  let implementedEvaluators = 0;
  for (const system of systems) {
    for (const pillar of system.pillars) {
      for (const practice of pillar.practices) {
        useCases += practice.use_cases.length;
        for (const useCase of practice.use_cases) {
          tests += useCase.tests.length;
          implementedEvaluators += useCase.tests.filter((test) => test.implementation_metadata.evaluator_status === "Implemented").length;
        }
      }
    }
  }
  return {systems: systems.length, useCases, tests, implementedEvaluators};
}
