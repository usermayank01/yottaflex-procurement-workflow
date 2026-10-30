# Design and Reasoning

## Assumptions
INR is the default procurement currency. Department thresholds determine approval. Competitive purchases use RFQs with at least three quotes. Quote selection is explainable using valid landed cost, then delivery time.

## Why SQLite?
It is relational, local, inspectable and requires no server.

## Why a fixed seed?
The same seed makes data and file hashes reproducible.

## Why separate ground truth?
Known anomalies must not silently become input features. They are kept in a separate file for evaluation.

## Why event history?
State changes are recorded explicitly so history is not overwritten.

## Known limitation
The supplied brief does not require a hosted UI/API, so the implementation prioritizes the explicit workflow, data, validation, traceability and reproducibility requirements.
