# repricing_pipeline/config.py

import os
from dotenv import load_dotenv

# Load variables from .env (if file exists)
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Local API (the provided local API in api/ folder)
API_URL = os.environ.get("REPRICING_API_URL", "http://127.0.0.1:8000/api/v1")

# API Key for authentication
API_KEY = os.environ.get("REPRICING_API_KEY")

# SQLite DB path
DB_PATH = os.environ.get("REPRICING_DB", os.path.join(BASE_DIR, "db\\products.db"))

# Prefect settings (optional runtime overrides)
PREFECT_FLOW_NAME = "repricing_pipeline_flow"
