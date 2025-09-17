# repricing_pipeline/flow.py

from prefect import flow, task
from repricing_pipeline.load import init_db, upsert_products
from repricing_pipeline.db.seed_vendors import seed_vendors
from repricing_pipeline.api_client import fetch_all_products, fetch_categories, fetch_brands, fetch_shipping_tiers
from repricing_pipeline.transform import transform_products

# --- Tasks ---

@task
def initialize_database():
    print("Initializing database...")
    init_db()
    seed_vendors()

@task
def fetch_products_for_vendor(vendor_id: int):
    return fetch_all_products(vendor_id=vendor_id)

@task
def fetch_mappings_for_vendor(vendor_id: int):
    categories_resp = fetch_categories(vendor_id)
    categories = {c["category_id"]: c["name"] for c in categories_resp.get("data", [])}

    brands_resp = fetch_brands(vendor_id)
    brands = {b["brand_id"]: b["name"] for b in brands_resp.get("data", [])}

    shipping_resp = fetch_shipping_tiers(vendor_id)
    shipping_tiers = {
        s["shipping_tier_id"]: {
            "shipping_tier": s["shipping_tier"],
            "shipping_cost": s.get("shipping_cost", 0)
        }
        for s in shipping_resp.get("data", [])
    }

    return brands, categories, shipping_tiers

@task
def attach_mappings_to_products(products: list, brands: dict, categories: dict, shipping_tiers: dict):
    for p in products:
        p["brand_name"] = brands.get(p.get("brand_id"), "Unknown Brand")
        p["category_name"] = categories.get(p.get("category_id"), "Unknown Category")
        shipping_info = shipping_tiers.get(p.get("shipping_tier_id"), {})
        p["shipping_tier"] = shipping_info.get("shipping_tier", "Standard")
        p["shipping_cost"] = shipping_info.get("shipping_cost", 0)
    return products

@task
def transform(products):
    return transform_products(products)

@task
def load(products):
    upsert_products(products)

# --- Flow ---

@flow(name="repricing_pipeline")
def repricing_pipeline_flow():
    initialize_database()

    vendor_ids = [1, 2, 3, 4, 5]
    all_transformed = []

    for vid in vendor_ids:
        raw_products = fetch_products_for_vendor(vid)
        brands, categories, shipping_tiers = fetch_mappings_for_vendor(vid)
        products_with_mappings = attach_mappings_to_products(raw_products, brands, categories, shipping_tiers)
        transformed = transform(products_with_mappings)
        all_transformed.extend(transformed)

    load(all_transformed)
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    repricing_pipeline_flow()
