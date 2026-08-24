# Dataset Strategy

Initial MVP data sources:

- Synthetic borrowers, transactions, documents, and support conversations.
- German Credit and LendingClub-style public credit data for credit scoring.
- Kaggle-style credit card fraud data for fraud diagnostics.
- Fairlearn or COMPAS-style datasets for fairness evaluator calibration.
- Jigsaw toxicity data for LLM response safety calibration.
- Synthetic temporal drift datasets for default prediction and repayment behavior.

Raw external datasets should not be committed. Store dataset manifests and schema
contracts here, then load records through privacy-preserving ingestion jobs.

