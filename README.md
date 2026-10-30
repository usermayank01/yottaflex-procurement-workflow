# YottaFlex Procurement Workflow — Candidate Project

Local-first, reproducible procurement workflow simulator and synthetic-data generator.

## Workflow
Purchase Request -> Approval -> RFQ -> Supplier Quotes -> Quote Comparison -> Award -> Purchase Order -> Delivery

## Requirements
- Python 3.10+
- No paid/cloud service
- SQLite + CSV/JSON outputs

## Install
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
python -m src.cli generate --scale starter --seed 20261022
python -m src.cli validate --input artifacts/starter
python -m src.cli reproducibility --seed 20261022
python -m src.cli demo
pytest -q
```

For the challenge-sized dataset:
```bash
python -m src.cli generate --scale full --seed 20261022
```

## Full targets
300 requesters, 120 suppliers, 1,200 requests, 500 RFQs, 1,500 quotes and 900 POs.

## Outputs
`artifacts/<scale>/` contains CSV/JSON tables, `procurement.db`, `ground_truth.csv`, `manifest.json`, and validation reports.

## Important design choices
- SQLite keeps the relational model locally runnable.
- Fixed seed makes generation reproducible.
- Request totals are derived from request lines.
- PO values reconcile to awarded quote landed cost.
- Workflow history is stored as explicit events.
- Ground truth is separate from input data.
- Edge cases are explicitly labelled instead of silently corrupting unrelated rows.

## Edge cases
PO without approval; expired quote; non-cheapest quote without rationale; inactive supplier; budget overrun; duplicate request; quote currency mismatch.

## AI disclosure
See `prompts/prompt_history.md`. AI was used for scaffolding, review and documentation. The candidate must personally review, execute, test and understand the implementation before submission.
