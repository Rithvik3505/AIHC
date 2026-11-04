# AI Health Check Backend

MVP backend scaffold for the Lendingtech-focused AI Assurance platform.

Core flow:

1. Select an AI system, pillar, supporting practice, and use case.
2. Choose deterministic demo evidence or provide ephemeral manual/CSV/JSON evidence for registered Golden Workflows.
3. Run preprocessing, perturbation, diagnostics, scoring, recommendations, and benchmarks.
4. Return standardized test outputs and founder-friendly report sections.

Current implementation boundary:

- 520 normalized taxonomy test specifications exist.
- 24 tests across six Golden Workflows have Phase 2C executable evaluators.
- Non-routed tests fail closed as `not_implemented`.
- Structured CSV/JSON and manual evidence is operational for the six Golden Workflows; PDF/image extraction is not implemented.
- Manual and uploaded evidence is not written to replay files or benchmark distributions.
- Benchmarks are fixed illustrative synthetic references, not industry peer distributions.

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

Demo workflow runs write replay artifacts under `backend/evaluations/replays`.
Manual and upload workflow runs explicitly disable replay persistence.
Automated tests stub replay writes where needed; do not run Golden Workflows
when a read-only inspection is required.
