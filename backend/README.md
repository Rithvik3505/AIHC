# AI Health Check Backend

MVP backend scaffold for the Lendingtech-focused AI Assurance platform.

Core flow:

1. Select an AI system, pillar, supporting practice, and use case.
2. Upload prompts, outputs, CSV/JSON records, or sample payloads.
3. Run preprocessing, perturbation, diagnostics, scoring, recommendations, and benchmarks.
4. Return standardized test outputs and founder-friendly report sections.

## Canonical Registries

The platform contracts live in `backend/registries`:

- `taxonomy_registry.json`
- `dataset_registry.json`
- `evaluator_registry.json`
- `perturbation_registry.json`
- `benchmark_registry.json`
- `workflow_registry.json`

JSON Schema contracts live in `backend/schemas/json`.

## Golden Workflows

The flagship workflows are implemented in `backend/workflows/golden.py`:

- Fraud Detection AI -> Adversarial Testing
- Credit Scoring AI -> Bias Mitigation
- Loan Approval AI -> Counterfactual Fairness
- Customer Support LLM -> Harmful Output
- Loan Default Prediction AI -> Residual Drift
- KYC Verification AI -> Outlier Diagnostics

Workflow runs write replay artifacts under `backend/evaluations/replays`.
