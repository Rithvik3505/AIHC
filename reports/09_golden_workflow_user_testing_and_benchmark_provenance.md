# Golden Workflow User Testing And Benchmark Provenance

## 1. Task Objective

Make the six Golden Workflows actively testable with deterministic demo evidence, manual records, or CSV/JSON uploads while preserving the hardened 24-evaluator boundary and making benchmark provenance explicit.

## 2. Branch And Baseline

- Branch: `main`
- Baseline/final HEAD: `cdfe58b9fe398cdc02cccb9f8476a034c18e9200`
- Baseline commit: `cdfe58b9 Harden Phase 2C evaluator correctness`
- No commit, push, branch, merge, or remote mutation was performed.
- Existing generated `.next` changes, replay JSON files, and `docs/Completed_MVP_Product_Taxonomy_Formatted_v2.docx` were preserved and excluded from application-change accounting.

## 3. Files Changed

Created:

- `backend/workflows/evidence.py`
- `frontend/components/WorkflowEvidenceWorkspace.tsx`
- `docs/GOLDEN_WORKFLOW_USER_TESTING_GUIDE.md`
- `tests/test_workflow_ingestion.py`
- `reports/09_golden_workflow_user_testing_and_benchmark_provenance.md`

Modified:

- `backend/api/main.py`
- `backend/benchmark_engine/distributions.py`
- `backend/diagnostics_engine/pipeline.py`
- `backend/registries/benchmark_registry.json`
- `backend/registries/workflow_registry.json`
- `backend/report_generation/reports.py`
- `backend/schemas/models.py`
- `backend/schemas/json/benchmark.schema.json`
- `backend/schemas/json/workflow.schema.json`
- `backend/taxonomy_engine/validation.py`
- `backend/workflows/golden.py`
- `backend/README.md`
- `docs/HLD.md`
- `frontend/README.md`
- `frontend/app/benchmarks/page.tsx`
- `frontend/app/dashboard/page.tsx`
- `frontend/app/evaluate/page.tsx`
- `frontend/app/layout.tsx`
- `frontend/components/BenchmarkComparison.tsx`
- `frontend/components/EvaluationRunner.tsx`
- `frontend/components/ReportViewer.tsx`
- `frontend/components/TaxonomySelector.tsx`
- `frontend/components/UploadPanel.tsx`
- `frontend/components/ui.tsx`
- `frontend/features/demoData.ts`
- `frontend/schemas/types.ts`
- `frontend/services/api.ts`
- `frontend/styles/globals.css`
- `tests/test_phase2d_truth_and_docs.py`
- `reports/README.md`

No evaluator implementation, taxonomy definition, taxonomy registry, evaluator registry, synthetic generator, dependency declaration, or lockfile was changed.

## 4. Evidence Contracts

| Workflow | Record contract | Workflow-level evidence |
| --- | --- | --- |
| Fraud adversarial | IDs, paired predictions, threshold, label, attack type/features, magnitude, budget, stage, constraint marker, optional transaction context | Default allowed perturbation budget |
| Credit bias | ID, baseline/counterfactual/semantic-variant scores and decisions, explicit semantic validity, protected/proxy categories, optional controlled proxy variant | Protected attribute and default decision threshold |
| Loan output fairness | ID, decision, reviewed label, gender/segment/geography, pair ID, income/DTI/history/risk features | None |
| Support LLM | Response ID, prompt, response, scenario tags | Deterministic `policy_rules` and `reference_facts` |
| Residual analysis | ID, timestamp/month/sequence, prediction, actual, segment | None |
| KYC outliers | Stable applicant/document IDs, document type, name, PAN, income, confidence/quality/biometric scores | None |

`backend/workflows/evidence.py` is the user-facing contract and normalization layer. It does not calculate diagnostic scores and does not alter evaluator algorithms.

## 5. Manual Input Capabilities

`/evaluate` now renders workflow-specific record fields from the live evidence contract. Users can add/remove rows, edit all supported fields, edit LLM policy/fact references, select the protected attribute where applicable, validate, and run all four tests or exactly one LT1/LT2/LT3/ST1 test.

Manual mode starts from a small deterministic synthetic template so record shapes are inspectable. Values are not encoded with expected test scores.

## 6. Upload Capabilities

- Operational formats: UTF-8 CSV and JSON.
- JSON accepts a payload object or top-level record array.
- CSV uses headers and semicolon-delimited list fields.
- Limits: 1,000,000 bytes, 500 records, and 10,000 characters per prompt/response.
- Empty, malformed, unsupported, oversized, and structurally invalid uploads fail with actionable 4xx messages.
- Upload parsing uses FastAPI `UploadFile`, stdlib CSV/JSON parsing, and the same normalization/validation path as manual evidence.
- JSON and CSV sample templates are downloadable from the UI for every workflow.

## 7. Raw-Document Decision

PDF/PNG/JPG/JPEG upload was not implemented. The repository has no reliable OCR/document extraction implementation, and adding fake extraction would violate the task boundary. Structured KYC manual/CSV/JSON evidence is operational independently. The UI, registry, contract endpoint, guide, and HLD mark raw-document extraction as `planned_not_operational`.

## 8. Validation And Error Handling

Preflight calls the same routed evaluator against normalized evidence and reports per selected test:

- Ready
- Missing evidence
- Invalid evidence
- Insufficient sample
- Optional evidence unavailable

Fatal structural errors block execution. Missing or insufficient test-specific evidence is allowed through so evaluators can return honest scoreless outputs and partial coverage. Numeric values reject NaN/Infinity; probability/threshold fields are range-checked; binary and Boolean fields are normalized explicitly; record and text limits are enforced.

Frontend failures are converted into endpoint-aware messages and do not expose Python stack traces.

## 9. Per-Test Selection

`EvaluationRequest.selected_test_ids` is optional and backward compatible. The pipeline validates selected IDs against the resolved use case and routes only those tests through the existing evaluator IDs. An empty selection runs all four tests. A partial run receives normal scoring/coverage but is ineligible for the four-test synthetic reference comparison.

## 10. Benchmark Architecture

The registry now distinguishes:

- `synthetic_reference`
- `external_reference`
- reserved `historical_customer_baseline`
- reserved `policy_threshold`
- reserved `industry_peer_distribution`

Each entry exposes ID, name, type, metric, source, stable URL where applicable, publication/version/date, evaluator compatibility, applicability, limitations, normalization method, empirical flag, grouping, and distribution.

Synthetic result fields are `synthetic_reference_median`, `synthetic_reference_top_quartile`, and `synthetic_percentile`. The legacy `industry_median` field was removed. No external source is normalized into the AIHC 0-100 score.

## 11. External / Industry Status

| Workflow | Implemented stance |
| --- | --- |
| Fraud | NIST adversarial-ML methodology is available; no comparable industry distribution for the AIHC composite |
| Credit bias | Fair-credit regulatory context is available; no universal numeric fairness-composite distribution |
| Loan approval | Regulation B context is available; no universal parity/equalized-odds composite distribution |
| Support LLM | NIST GenAI methodology is available; no lending-industry peer distribution for this safety composite |
| Residual drift | Model-validation/outcomes-analysis guidance is available; no exact AIHC composite peer distribution |
| KYC | NIST biometric subcomponent evidence and RBI KYC context are available; no benchmark for the overall AIHC KYC multi-view score |

KYC remains synthetic-benchmark-ineligible and does not fall back to fraud.

## 12. External Source Provenance

- [NIST AI 100-2 E2025](https://doi.org/10.6028/NIST.AI.100-2e2025): adversarial-ML methodology and terminology.
- [CFPB ECOA compliance resources](https://www.consumerfinance.gov/compliance/compliance-resources/other-applicable-requirements/equal-credit-opportunity-act/): fair-credit regulatory context.
- [CFPB Regulation B](https://www.consumerfinance.gov/rules-policy/regulations/1002/): fair-lending regulatory context.
- [NIST AI 600-1](https://doi.org/10.6028/NIST.AI.600-1): generative-AI risk-management methodology.
- [Federal Reserve SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/sr2602.htm): current model-risk/outcomes-analysis guidance.
- [NIST FRTE/FATE](https://pages.nist.gov/frvt/): scoped empirical biometric subcomponent evaluation.
- [RBI KYC Master Direction](https://www.rbi.org.in/commonman/Upload/English/Notification/PDFs/MD18KYCF6E92C82E1E1419D87323E3869BC9F13.pdf): KYC regulatory context.

These sources do not prove evaluator implementation, establish certification, or provide an industry distribution unless their stated applicability explicitly contains comparable empirical observations. NIST FRTE data is empirical for specific biometric algorithms/datasets, not for the combined KYC score.

## 13. Replay And Privacy

- Demo mode preserves local replay writing.
- Manual/upload modes do not call the replay store and return `persisted: false` metadata.
- Raw evidence is not added to benchmark distributions or the process-local aggregate store.
- No production database, authentication, authorization, encryption/key-management, or governed retention layer was introduced.
- Historical comparison remains planned because local demo replay files are not a governed customer-history store.

## 14. Tests Added

`tests/test_workflow_ingestion.py` covers:

- all six evidence contracts and all 24 stable test IDs;
- all six custom valid evidence runs;
- no custom-evidence replay writes;
- individual-test selection and partial benchmark ineligibility;
- JSON and CSV parsing;
- empty, malformed, unsupported, oversized, and excessive-row input;
- workflow-specific missing/invalid evidence;
- LLM and KYC deliberate failure cases;
- synthetic-versus-industry benchmark labeling and external provenance;
- live FastAPI contract, validation, upload, run, unknown-workflow, and invalid-test paths.

Existing Phase 2C mathematical correctness, evaluator regression, taxonomy, documentation, and Golden Workflow tests remain in the full suite.

## 15. Final 24-Test Matrix

| Test ID | Evaluator ID |
| --- | --- |
| `fraud-detection-ai-adversarial-testing-lt1` | `phase2c_fraud_adversarial_threshold_evasion_v1` |
| `fraud-detection-ai-adversarial-testing-lt2` | `phase2c_fraud_adversarial_attack_pattern_v1` |
| `fraud-detection-ai-adversarial-testing-lt3` | `phase2c_fraud_adversarial_feature_manipulation_v1` |
| `fraud-detection-ai-adversarial-testing-st1` | `phase2c_fraud_adversarial_attack_budget_v1` |
| `credit-scoring-ai-bias-mitigation-lt1` | `phase2c_credit_bias_counterfactual_consistency_v1` |
| `credit-scoring-ai-bias-mitigation-lt2` | `phase2c_credit_bias_proxy_sensitivity_v1` |
| `credit-scoring-ai-bias-mitigation-lt3` | `phase2c_credit_bias_language_variant_v1` |
| `credit-scoring-ai-bias-mitigation-st1` | `phase2c_credit_bias_multifactor_fairness_v1` |
| `loan-approval-ai-fairness-of-model-output-lt1` | `phase2c_loan_fairness_outcome_parity_v1` |
| `loan-approval-ai-fairness-of-model-output-lt2` | `phase2c_loan_fairness_error_rate_v1` |
| `loan-approval-ai-fairness-of-model-output-lt3` | `phase2c_loan_fairness_similar_applicant_v1` |
| `loan-approval-ai-fairness-of-model-output-st1` | `phase2c_loan_fairness_multimetric_segment_v1` |
| `customer-support-llm-harmful-model-output-lt1` | `phase2c_support_harmful_toxicity_v1` |
| `customer-support-llm-harmful-model-output-lt2` | `phase2c_support_harmful_financial_guidance_v1` |
| `customer-support-llm-harmful-model-output-lt3` | `phase2c_support_harmful_vulnerable_customer_v1` |
| `customer-support-llm-harmful-model-output-st1` | `phase2c_support_harmful_multidimensional_v1` |
| `loan-default-prediction-ai-residual-analysis-lt1` | `phase2c_default_residual_rolling_drift_v1` |
| `loan-default-prediction-ai-residual-analysis-lt2` | `phase2c_default_residual_distribution_shape_v1` |
| `loan-default-prediction-ai-residual-analysis-lt3` | `phase2c_default_residual_segment_concentration_v1` |
| `loan-default-prediction-ai-residual-analysis-st1` | `phase2c_default_residual_multidimensional_v1` |
| `kyc-verification-ai-outlier-diagnostics-lt1` | `phase2c_kyc_outlier_univariate_influence_v1` |
| `kyc-verification-ai-outlier-diagnostics-lt2` | `phase2c_kyc_outlier_multivariate_anomaly_v1` |
| `kyc-verification-ai-outlier-diagnostics-lt3` | `phase2c_kyc_outlier_field_constraints_v1` |
| `kyc-verification-ai-outlier-diagnostics-st1` | `phase2c_kyc_outlier_multiview_severity_v1` |

## 16. Validation Commands And Results

All commands exited `0` unless noted:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\LENOVO\.codex\validation-envs\aihc-phase2b\Scripts\python.exe -m pytest -q
# 82 passed, 1 third-party deprecation warning

$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\LENOVO\.codex\validation-envs\aihc-phase2b\Scripts\python.exe scripts\validate_taxonomy.py
# taxonomy validation passed

$env:PYTHONDONTWRITEBYTECODE='1'; C:\Users\LENOVO\.codex\validation-envs\aihc-phase2b\Scripts\python.exe scripts\sync_taxonomy_registry.py --check
# taxonomy registry is synchronized

cd frontend; npm run type-check
# passed

cd frontend; npm run build
# passed; all seven routes compiled

git diff --check
# passed
```

One type-check invocation was initially launched concurrently with `next build` and exited `1` because the build was regenerating `.next/types` at that instant. The same `npm run type-check` command was rerun sequentially after the successful build and exited `0`; no source change was needed for that generated-directory race.

Additional live validation:

- FastAPI and Next.js dev servers started on ports 8000 and 3000.
- `/evaluate` returned HTTP 200.
- All six contract endpoints returned templates.
- All six custom valid payloads returned four Ready statuses and four completed outputs.
- All six empty-record payloads returned zero Ready statuses.
- All six custom runs returned `replay.persisted: false`.
- Headless Chrome rendered desktop and compact-width screenshots from the live `/evaluate` page. An initial compact overflow was corrected with minimum-width and selector constraints.
- No Playwright package was installed, so scripted click-by-click browser automation was not claimed.

## 17. Taxonomy And Scope Verification

- 8 AI systems
- 130 use cases
- 520 tests
- 390 Light Tests
- 130 Strong Tests
- 21 Supporting Practices
- Identity fingerprint: `d7f9f041248661a6e1bc551c824d9c82bd6668518b5ebca266d1e08fad905b9f`
- Executable tests: exactly 24
- Specification-only tests: exactly 496
- Golden Workflows: exactly 6

No taxonomy IDs, names, ordering, counts, hierarchy, or evaluator routing IDs changed.

## 18. Remaining MVP Limitations

- No raw-document OCR or extraction.
- No authentication, authorization, production persistence, encrypted evidence store, or retention controls.
- No governed historical customer baseline or compare-with-previous-run feature.
- No empirical industry-peer distribution for any AIHC composite score.
- KYC external empirical data applies only to biometric subcomponents, not the combined KYC diagnostic.
- Manual editors are contract-driven tables; very wide contracts require horizontal scrolling.
- Browser validation used rendered Chrome plus live HTTP/API paths rather than Playwright interaction automation.

## 19. Final Scope Confirmation

Only the same 24 Phase 2C tests remain executable. The other 496 tests were not implemented. Evaluator mathematics was not weakened or rewritten. No production database, external LLM judge, fake OCR, dependency upgrade, commit, or push was introduced.

Final `git status --short` contains only the authorized source/documentation/test/report changes listed above plus the pre-existing `.next` generated changes, eight pre-existing untracked replay JSON files, and the user-owned `docs/Completed_MVP_Product_Taxonomy_Formatted_v2.docx`. No replay, canonical taxonomy DOCX, taxonomy registry, evaluator registry, dependency file, or lockfile was changed by this task.
