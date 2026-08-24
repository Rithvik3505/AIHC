# Completed MVP Taxonomy

The executable taxonomy lives in `backend/taxonomy_engine/taxonomy.py`.

This MVP prioritizes meaningful intersections over exhaustive theoretical
coverage. The theoretical Phase 1 space is:

- 8 Lendingtech AI systems
- 21 Category A and Category B supporting practices
- 168 possible AI System x Supporting Practice intersections

After applying the Meaningfulness Heuristic, the current MVP taxonomy contains:

- 130 meaningful use cases
- 104 Category A horizontal use cases
- 26 Category B Lendingtech-depth use cases
- 520 tests total

Each use case contains:

- 3 light tests
- 1 strong test
- standardized output schema

The full detailed taxonomy, including hierarchical Word headings and detailed
test definitions, is in `docs/Completed MVP Product Taxonomy.docx`.

## Meaningfulness Heuristic

Each AI System x Supporting Practice intersection is prioritized using:

- Risk Criticality
- Founder Pain
- Investor/Reputational Importance
- Benchmark Density Potential
- Technical Signal Strength
- MVP Feasibility

## Category A Applicability

Category A supporting practices are horizontal AI trust primitives and can be
reused outside Lendingtech. However, the use cases in this MVP document are
written in Lendingtech language. For non-Lendingtech systems, the practice and
test pattern can transfer, but the use-case wording, benchmark labels, inputs,
and recommendations should be adapted to the new vertical.

## Standard Test Output

```json
{
  "score": 0,
  "risk_level": "Low | Medium | High",
  "insight": "...",
  "recommendation": ["...", "..."],
  "metadata": {
    "pillar": "...",
    "practice": "...",
    "ai_system": "...",
    "test_type": "light | strong"
  }
}
```
