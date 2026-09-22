# Dataset Strategy

Initial MVP data sources:

- Synthetic borrowers, transactions, documents, and support conversations.
- Public dataset references such as German Credit, LendingClub-style credit
  data, Kaggle-style fraud data, Fairlearn/COMPAS-style fairness data, and
  Jigsaw toxicity data are manifest/planning references only unless explicitly
  wired by executable code.
- Synthetic temporal drift datasets for default prediction and repayment behavior.

Raw external datasets should not be committed. Store dataset manifests and schema
contracts here, then load records through privacy-preserving ingestion jobs.

Customer dataset upload is a planned contract only. The current executable MVP
uses synthetic generators and generated perturbation evidence for Golden
Workflow demonstrations.
