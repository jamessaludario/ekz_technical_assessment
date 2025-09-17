import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent  # ekh_technical_assessment

# Database path (absolute, inside project folder)
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "data/products.db")).resolve()
SCHEMA_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "repricing_pipeline/db/schema.sql")).resolve()

# API settings
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

# Prefect flow name
PREFECT_FLOW_NAME = os.getenv("PREFECT_FLOW_NAME", "repricing_pipeline")
