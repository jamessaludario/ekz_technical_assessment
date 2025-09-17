from prefect import flow, task
from repricing_pipeline.load import init_db, upsert_products
from repricing_pipeline.db.seed_vendors import seed_vendors
from repricing_pipeline.api_client import fetch_all_products
from repricing_pipeline.transform import transform_products


@task
def initialize_database():
    print("Initializing database...")
    init_db()
    seed_vendors()


@task
def fetch_products():
    print("Fetching products from API...")
    products = fetch_all_products()
    print(f"Fetched total products: {len(products)}")
    if products:
        print("Sample product:", products[0])
    return products


@task
def transform(products):
    print("Transforming products...")
    return transform_products(products)


@task
def load(products):
    print("Loading products into database...")
    upsert_products(products)

@flow(name="repricing_pipeline")
def repricing_pipeline_flow():
    initialize_database()
    raw_products = fetch_products()
    transformed = transform(raw_products)
    load(transformed)
    print("Pipeline completed successfully!")


if __name__ == "__main__":
    repricing_pipeline_flow()
