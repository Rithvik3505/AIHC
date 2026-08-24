# AI Health Check MVP HLD

## Product Scope

AI Health Check is an AI Assurance platform for startup AI systems. Phase 1 is
Lendingtech only and covers 8 systems:

- Credit scoring AI
- Loan approval AI
- Fraud detection AI
- KYC verification AI
- Loan default prediction AI
- Loan underwriting AI
- OCR document extraction
- Customer support LLM

The platform model is:

`Fintech Segment -> AI System -> Pillar -> Supporting Practice -> Use Case -> Test Type`

## Pillars

- Risk
- Reliability
- Data Integrity
- Explainability
- Governance

## Taxonomy Strategy

The MVP does not implement every theoretical combination. It uses a
meaningfulness heuristic:

- Risk criticality
- Founder pain
- Investor/reputational importance
- Benchmark density potential
- Technical signal strength
- MVP feasibility

Only high-signal intersections are encoded in `backend/taxonomy_engine/taxonomy.py`.
Each use case has 3 light tests and 1 strong test, all returning the standard
JSON test output schema.

## Backend Architecture

- `taxonomy_engine`: Lendingtech ontology and use-case selection.
- `diagnostics_engine`: pipeline orchestration and evaluator routing.
- `scoring_engine`: risk thresholds, weighted aggregation, and risk levels.
- `recommendation_engine`: practice-aware recommendations.
- `benchmark_engine`: anonymized distribution capture for future moat.
- `llm_evaluators`: deterministic MVP evaluator adapters; replaceable with LLM-as-judge.
- `perturbation_engine`: counterfactual, numeric stress, and text attack generation.
- `synthetic_data`: synthetic borrowers and fraud transactions.
- `report_generation`: founder-facing report summaries.
- `schemas`: Pydantic and database schemas.
- `api`: FastAPI routes.

## Evaluation Pipeline

1. User selects AI system, pillar, practice, and use case.
2. User uploads records, outputs, predictions, actuals, prompts, or evidence.
3. API validates taxonomy selection.
4. Diagnostics engine selects evaluator by supporting practice.
5. Light tests run fast checks; strong tests apply deeper scenario logic.
6. Scoring engine aggregates tests with stronger weight for strong tests.
7. Recommendation engine returns actionable remediation guidance.
8. Benchmark engine stores anonymized score distributions.
9. Report generator produces founder-friendly summaries.

## API Surface

- `POST /evaluate`
- `POST /score`
- `POST /generate-report`
- `POST /benchmark`
- `POST /taxonomy`
- `GET /use-cases`
- `GET /tests`

## Database Design

See `backend/schemas/database.sql`.

Core tables:

- `organizations`
- `ai_systems`
- `evaluations`
- `test_results`
- `benchmark_distributions`

## Benchmark Architecture

The MVP stores distribution keys at:

`ai_system|pillar|practice|use_case`

Future production storage should add anonymized organization attributes such as
company stage, geography, AI maturity, and lender type. Never store raw borrower
records, prompts, or outputs in benchmark distributions.

## LLM Evaluation Strategy

The MVP uses deterministic rule-based evaluators as placeholders. Production
LLM-as-judge evaluators should be:

- schema-constrained
- temperature 0
- grounded in rubric prompts
- logged with evaluator version
- calibrated against public and synthetic datasets

Recommended LLM judge tasks:

- toxicity
- harmfulness
- empathy
- compliance
- misleading financial content
- explanation quality

## Synthetic Data Strategy

Generate:

- synthetic borrowers
- synthetic fraud transactions
- synthetic document extraction records
- synthetic support conversations
- counterfactual sensitive-attribute variants
- fraud and prompt adversarial attacks
- temporal drift scenarios

## MVP Roadmap

1. Backend taxonomy and deterministic pipeline.
2. CSV/JSON upload and evaluator adapters.
3. Founder report UI in Next.js.
4. Advisor-assisted review workflows.
5. PostgreSQL persistence and benchmark distributions.
6. LLM-as-judge rubric evaluators.
7. Dataset calibration with public and synthetic datasets.
8. Cross-startup benchmark dashboards.

