# repricing_pipeline/flow.py

from prefect import flow, task
from repricing_pipeline.api_client import fetch_all_products
from repricing_pipeline.transform import transform_products
from repricing_pipeline.load import init_db, upsert_products
from repricing_pipeline.config import PREFECT_FLOW_NAME, VENDORS


@task
def extract_task():
    print("Extracting products from API...")
    products = fetch_all_products()
    print(f"Extracted {len(products)} products")
    return products


@task
def transform_task(products):
    print("🔹 Transforming products (applying pricing rules)...")
    transformed = transform_products(products)
    print(f"Transformed {len(transformed)} products")
    return transformed


@task
def load_task(products):
    print("Initializing database, seeding vendors, and loading products...")
    # Seed vendors if DB is empty or on first run
    init_db(seed_vendors=VENDORS)
    upsert_products(products)
    print("Load complete")


@flow(name=PREFECT_FLOW_NAME)
def repricing_pipeline_flow():
    raw_products = extract_task()
    transformed_products = transform_task(raw_products)
    load_task(transformed_products)


if __name__ == "__main__":
    repricing_pipeline_flow()
