# repricing_pipeline/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# API settings
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

# Database path
DB_PATH = os.getenv("DB_PATH", "data/products.db")

# Prefect flow name
PREFECT_FLOW_NAME = os.getenv("PREFECT_FLOW_NAME", "repricing_pipeline")
