# Repricing Pipeline - run instructions

1. Start the provided local API:
   - From the repo root run: `python -m api` or follow `api/README.md` instructions to start the API server (it usually runs at http://127.0.0.1:8000).

2. Install dependencies (prefer a venv):

3. Run the pipeline locally (Prefect):
This will:
- extract products from the local API,
- transform (calculate repriced values),
- init SQLite DB and upsert results to `repricing_pipeline/products.db`.

4. Run tests:

Notes:
- To change DB or API URL, set environment vars: `REPRICING_DB` and `REPRICING_API_URL`.
- To run as a scheduled Prefect flow, configure Prefect server/agent and register this flow (Prefect docs).
