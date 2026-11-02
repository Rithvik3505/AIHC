# Phase 2C Evaluator Correctness Hardening

## Task Objective

Harden the existing 24 Phase 2C Golden Workflow evaluators against the correctness, statistical-semantics, evidence-contract, and naming findings in the external audit. This task did not add executable coverage for any of the remaining 496 taxonomy tests.

## Repository And Starting State

- Branch: `main`
- Starting and final source checkpoint: `a01be800c61a9a57d35b30c730b041e6a74edadf` (`Complete Phase 2D and documentation hardening`)
- Remote: `origin https://github.com/Rithvik3505/AIHC.git`
- `origin/main` after fetch: `a01be800c61a9a57d35b30c730b041e6a74edadf`
- No commit, push, merge, branch, or remote mutation was performed.
- The starting tree already contained modified tracked `frontend/.next/` output, eight untracked replay JSON files dated 2026-09-17, and the user-owned untracked `docs/Completed_MVP_Product_Taxonomy_Formatted_v2.docx`. These were not treated as task changes, deleted, staged, or overwritten.

## Audit Input

- File: `C:\Users\LENOVO\WORK\Projects\LendingTech\AIHC_24_Implemented_Tests_Correctness_Audit (1).docx`
- Audit repository commit: `a01be800c61a9a57d35b30c730b041e6a74edadf`
- Scope: all 24 implemented tests across the six Golden Workflows.
- The DOCX was read in full before code edits. Findings were mapped to evaluator functions, shared helpers, generators, workflow payloads, registries, generated taxonomy specifications, and tests.

## Files Changed

Created:

- `tests/test_phase2c_mathematical_correctness.py`
- `reports/08_phase_2c_evaluator_correctness_hardening.md`

Modified:

- `backend/diagnostics_engine/test_specific.py`
- `backend/llm_evaluators/rule_based.py`
- `backend/synthetic_data/generators.py`
- `backend/workflows/golden.py`
- `backend/registries/evaluator_registry.json`
- `backend/registries/workflow_registry.json`
- `backend/taxonomy_engine/diagnostic_specs.py`
- `backend/registries/taxonomy_registry.json` through the deterministic synchronizer
- `docs/HLD.md`
- `docs/Completed_MVP_Product_Taxonomy_Formatted.docx` through the canonical generator
- `docs/Completed_MVP_Product_Taxonomy_Review_Pack.docx` through the canonical generator
- `tests/test_phase2c_evaluators.py`
- `tests/test_pipeline.py`
- `tests/test_documentation_hardening.py`
- `reports/README.md`

Deleted: none.

## Defect-By-Defect Closure

Verified implementation outcomes:

1. KYC ST1 now builds detector flag sets from stable record IDs, reports per-detector flags/counts, records flagged by two/all assessable detectors, pairwise Jaccard overlap, mean Jaccard agreement, and prioritized review IDs.
2. Credit Bias LT1 uses a record threshold, workflow threshold, or documented `0.55` default consistently for baseline/counterfactual decisions and crossing logic.
3. Credit Bias LT3 preserves valid `0.0` scores through explicit `None` handling and accepts only `semantic_variant_valid is True`.
4. Fraud LT2 reports baseline FNR, attacked FNR, their difference, and actual-positive count using only reliable binary positive labels.
5. Loan Fairness LT1 computes parity independently for `gender`, `segment`, and `geography`; aggregate health uses the worst valid within-attribute disparity.
6. Residual LT1 requires usable temporal evidence, sorts records, calculates fixed rolling-window MAE, and reports explicit boundaries and sizes. Input shuffling does not change results.
7. LLM LT2 consumes prompt/response evidence plus deterministic policy/fact references and reports policy violations, factual contradictions, unsupported guarantees, and unsafe guidance separately.
8. LLM LT3 derives vulnerability from prompt/scenario tags and evaluates acknowledgement, official support/escalation, and pressure/coercion in the response.
9. LLM ST1 separates generic sensitive-field mentions, requests to collect sensitive data, and reproduced sensitive values. `Never share your Aadhaar number` is not leakage.
10. Pseudo-bootstrap helpers and raw metrics were removed. Strong Tests expose observed ranges from actual component/record observations without confidence-interval claims.
11. Loan Fairness LT2 preserves undefined TPR/FPR/FNR values as `null`, reports denominators, and compares only rates defined for at least two groups.
12. Overclaimed labels were corrected: statistical interaction became `worst_scenario_excess_success_rate`; calibration proxy became `worst_component_severity`; KYC multivariate language became robust multi-feature scoring; detector agreement is now actual Jaccard overlap.
13. Fraud LT1 clamps degradation at zero and removes algebraically duplicate threshold-margin scoring.
14. Fraud LT3 scores only valid in-budget attacks and reports excluded constraint-violating evidence separately.
15. Fraud ST1 excludes out-of-budget attacks and reports worst-scenario excess success rather than a statistical interaction effect.
16. Credit Bias LT2 reports Cramer's V protected/proxy association, outcome disparity, and optional controlled prediction sensitivity. It explicitly disclaims causal/discrimination proof.
17. Loan Fairness LT3 prefers explicit matched pairs, otherwise uses normalized numeric risk-feature distance. Only decision disagreement materially reduces health.
18. Residual LT3 requires four observations per substantive segment and reports worst-minus-overall and worst-minus-best-valid MAE gaps plus excluded segments.
19. KYC LT1 implements `0.6745 * (x - median) / MAD` and limits analysis to whitelisted continuous KYC quality fields.
20. KYC LT2 is named and reported as a robust multi-feature anomaly score and explicitly disclaims covariance-aware multivariate detection.
21. KYC LT3 structurally validates PAN, separates missing from malformed values, and applies document-type-specific name/PAN/income checks without external identity verification.
22. All six Strong Tests expose component metrics and add worst-case, explicit weighting, record-level, or cross-view depth. They do not merely average scores under a stronger label.
23. An additional defect found by golden tests was fixed: Strong Test expressions using `item.score or 100` converted legitimate zero scores into perfect health. All such aggregations now preserve zero.

## 24-Test Implementation Matrix

| Test ID | Before | After | Status |
| --- | --- | --- | --- |
| `fraud-detection-ai-adversarial-testing-lt1` | Negative degradation could improve health; duplicate margin signal | Non-negative degradation; distinct flip and degradation signals | Resolved |
| `fraud-detection-ai-adversarial-testing-lt2` | Mislabeled, incorrectly normalized FN metric | Exact baseline/attacked FNR and delta over actual positives | Resolved |
| `fraud-detection-ai-adversarial-testing-lt3` | Invalid attacks penalized robustness | Invalid/out-of-budget attacks excluded and disclosed | Resolved |
| `fraud-detection-ai-adversarial-testing-st1` | Overclaimed interaction/bootstrap terms; budget violations scored | Valid-budget scenario severity, worst-scenario excess, observed range | Resolved |
| `credit-scoring-ai-bias-mitigation-lt1` | `0.50` evaluator threshold vs `0.55` generator | One explicit record/workflow/default threshold | Resolved |
| `credit-scoring-ai-bias-mitigation-lt2` | Outcome gaps called proxy sensitivity | Protected/proxy association plus optional controlled sensitivity | Resolved |
| `credit-scoring-ai-bias-mitigation-lt3` | Zero fallback and semantic validity defaulted true | Explicit `None` check; only validated semantic pairs | Resolved |
| `credit-scoring-ai-bias-mitigation-st1` | Artificial pseudo-bootstrap sample | Equal documented weights, worst component, observed range | Resolved |
| `loan-approval-ai-fairness-of-model-output-lt1` | Mixed unrelated cohort dimensions | Independent within-attribute parity and worst-valid aggregation | Resolved |
| `loan-approval-ai-fairness-of-model-output-lt2` | Undefined rates forced to zero | Null undefined rates with explicit denominators | Resolved |
| `loan-approval-ai-fairness-of-model-output-lt3` | Heuristic distance directly penalized health | Explicit pairs/normalized distance; disagreement is primary failure | Resolved |
| `loan-approval-ai-fairness-of-model-output-st1` | Implicit aggregation and pseudo-bootstrap | Equal explicit weights, worst view, observed range | Resolved |
| `customer-support-llm-harmful-model-output-lt1` | Output-list-only adapter | Same transparent lexical method with structured-record support | Verified acceptable MVP |
| `customer-support-llm-harmful-model-output-lt2` | Unsafe phrase scan only | Deterministic policy/factual consistency plus separate guidance signals | Resolved |
| `customer-support-llm-harmful-model-output-lt3` | Vulnerability inferred from response | Vulnerability established from prompt/scenario context | Resolved |
| `customer-support-llm-harmful-model-output-st1` | Sensitive terminology treated as leakage | Separate mention, collection request, and actual-value exposure metrics | Resolved |
| `loan-default-prediction-ai-residual-analysis-lt1` | Unsorted first-half/second-half split | Temporally sorted fixed rolling-window analysis | Resolved |
| `loan-default-prediction-ai-residual-analysis-lt2` | Descriptive MVP statistic | Core method retained; aligned record evidence preferred | Verified acceptable MVP |
| `loan-default-prediction-ai-residual-analysis-lt3` | Two-record segment minimum; one diluted gap | Four-record minimum and two explicit disparity gaps | Resolved |
| `loan-default-prediction-ai-residual-analysis-st1` | Bootstrap/calibration overclaims | Worst component and observed component-severity range | Resolved |
| `kyc-verification-ai-outlier-diagnostics-lt1` | Unscaled MAD distance; all numeric fields | Conventional modified z-score; quality-field whitelist | Resolved |
| `kyc-verification-ai-outlier-diagnostics-lt2` | “Multivariate” overclaim | Transparent robust multi-feature score | Resolved by conservative rename |
| `kyc-verification-ai-outlier-diagnostics-lt3` | PAN length only | PAN structure and document-specific missing/malformed checks | Resolved |
| `kyc-verification-ai-outlier-diagnostics-st1` | Metric-schema count called detector agreement | Actual record-level flag overlap/Jaccard and review priority | Resolved |

## Evidence-Contract And Synthetic-Data Changes

- Fairness records now carry `decision_threshold: 0.55`; all generated decisions use `>=` against that threshold.
- Support LLM demo evidence now uses prompt/response/scenario-tag records plus declared deterministic policy and fact references.
- Residual evaluators prefer aligned prediction/actual values carried by timestamped records when available.
- Fraud attacks retain explicit magnitude, budget, and constraint-violation fields; invalid attacks are retained as excluded evidence.
- KYC records retain stable applicant/document IDs for detector overlap.
- All generators remain deterministic, small, inspectable, synthetic, and free of encoded expected scores.

## Golden Mathematical Tests

`tests/test_phase2c_mathematical_correctness.py` adds a hand-computable raw-metric and score fixture for every one of the 24 evaluator IDs. It also covers:

- non-negative fraud degradation;
- exact fraud FNR arithmetic;
- attack-budget exclusion;
- threshold consistency;
- zero-score and unknown-semantic handling;
- within-attribute loan parity;
- undefined fairness rates;
- policy contradiction without legacy unsafe keywords;
- prompt-context vulnerability;
- safe Aadhaar warning behavior;
- shuffled temporal evidence;
- undersized residual segments;
- conventional modified-z arithmetic;
- structural PAN validation;
- known KYC detector overlap;
- absence of bootstrap/confidence raw-metric claims.

## Specification And Registry Synchronization

- Stable test IDs, use-case IDs, evaluator IDs, workflow IDs, names, and ordering are unchanged.
- Targeted diagnostic-spec overrides align only the six implemented Golden Workflow use cases with the corrected algorithms and conservative names.
- `taxonomy_registry.json` was regenerated with `scripts/sync_taxonomy_registry.py --write` and passed check mode.
- The complete DOCX and review pack were regenerated through `scripts/generate_formatted_taxonomy_docx.py`; neither was manually edited.
- Evaluator and workflow registries now disclose corrected evidence contracts and limitations.

Pre/post invariants:

- 8 AI systems
- 130 use cases
- 520 tests
- 390 Light Tests
- 130 Strong Tests
- 21 Supporting Practices
- 104 Category A / 26 Category B use cases
- Exactly 24 implemented evaluator/test IDs
- Exactly six Golden Workflows
- Identity fingerprint unchanged: `d7f9f041248661a6e1bc551c824d9c82bd6668518b5ebca266d1e08fad905b9f`

## Intentional Conservative Alternatives

- No bootstrap was implemented because the Strong Tests do not consistently expose suitable independent sample-level observations. Honest observed ranges are reported instead.
- KYC LT2 was renamed rather than adding a heavy covariance-aware anomaly dependency.
- LLM policy/factual review remains deterministic and reference-pattern-based; no external LLM judge or open-domain fact checker was introduced.
- KYC format checks remain local and deterministic; no external identity-verification service was introduced.
- Credit proxy analysis supports controlled variants when supplied, while current demo evidence primarily demonstrates protected/proxy association. Association is explicitly not treated as causal proof.

These choices were explicitly permitted by the audit/request and do not leave a listed correctness defect falsely marked as resolved.

## Validation Commands And Results

Pre-change baseline:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\LENOVO\.codex\validation-envs\aihc-phase2b\Scripts\python.exe -m pytest tests\test_phase2c_evaluators.py -q
npm run type-check
```

- Exit `0`: `8 passed`.
- Exit `0`: TypeScript check completed with no errors.

Focused evaluator and mathematical suite:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\LENOVO\.codex\validation-envs\aihc-phase2b\Scripts\python.exe -m pytest tests\test_phase2c_evaluators.py tests\test_phase2c_mathematical_correctness.py -q
```

- Final exit `0`: `48 passed`.
- Iterative runs correctly exposed the new LLM evidence requirement and the Strong-Test zero-score fallback; both were fixed before final validation.

Golden Workflows with replay writing monkeypatched to a temporary path:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\LENOVO\.codex\validation-envs\aihc-phase2b\Scripts\python.exe -m pytest tests\test_phase2d_truth_and_docs.py::test_all_golden_workflows_run_with_replay_writes_stubbed -q
```

- Exit `0`: `1 passed`; all six workflows executed and no canonical replay was written.

Full backend suite:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\LENOVO\.codex\validation-envs\aihc-phase2b\Scripts\python.exe -m pytest -q
```

- Exit `0`: `68 passed in 5.65s`.

Taxonomy and drift validation:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\LENOVO\.codex\validation-envs\aihc-phase2b\Scripts\python.exe scripts\sync_taxonomy_registry.py --write
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\LENOVO\.codex\validation-envs\aihc-phase2b\Scripts\python.exe scripts\validate_taxonomy.py
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\LENOVO\.codex\validation-envs\aihc-phase2b\Scripts\python.exe scripts\sync_taxonomy_registry.py --check
```

- Exit `0`: registry synchronized.
- Exit `0`: taxonomy validation passed.
- Exit `0`: registry is synchronized.
- An initial synchronizer invocation without `--write` exited `2` with usage text and made no change; it was immediately rerun with the required explicit mode.
- An intermediate taxonomy validation correctly identified three overrides missing recognized Strong-Test depth wording. The source overrides were corrected, synchronized again, and the final validation passed.

Frontend validation:

```powershell
cd frontend
npm run type-check
npm run build
```

- Type-check exit `0`.
- Production build exit `0`; all seven application routes compiled and nine static pages were generated where applicable.

Final repository checks:

```powershell
git diff --check
git diff --name-only -- backend/evaluations/replays frontend/package-lock.json requirements.txt pyproject.toml venv
```

- `git diff --check` exit `0` (line-ending warnings only).
- Restricted-path diff command exit `0` with no changed paths.

## Known Remaining Limitations

- The 24 evaluators remain deterministic evidence-log diagnostics; they do not invoke customer models or prove production performance.
- LLM checks are transparent pattern/rubric checks and can miss paraphrases or contextual harms.
- Fairness findings depend on evidence quality, cohort support, thresholds, and labels; they do not prove causality or legal compliance.
- KYC multi-feature scoring does not model covariance and KYC field rules do not verify identity externally.
- Benchmarks remain illustrative synthetic references, not industry-peer distributions.
- Customer file upload and production persistence remain unsupported.

## Final Worktree State

- Branch remains `main` at `a01be800c61a9a57d35b30c730b041e6a74edadf`.
- Phase 2C correctness changes are intentionally uncommitted for review.
- Pre-existing tracked `.next` output remains modified; the production build refreshed build artifacts, but they are not part of the implementation change set.
- The eight pre-existing untracked replay files and user-owned `_v2` DOCX remain present and untouched.
- No new canonical replay artifact, dependency file, lockfile, virtual environment, or cache was added to the implementation diff.

## Scope Confirmation

Exactly 24 tests remain executable. The remaining 496 taxonomy tests were not implemented or routed. No Phase 2D feature expansion, upload implementation, persistence, external benchmark collection, dependency upgrade, commit, or push was performed.

