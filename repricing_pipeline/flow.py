from prefect import flow, task, get_run_logger
from repricing_pipeline.load import init_db, upsert_products
from repricing_pipeline.db.seed_vendors import seed_vendors
from repricing_pipeline.api_client import fetch_all_products, fetch_categories, fetch_brands, fetch_shipping_tiers
from repricing_pipeline.transform import transform_products

# --- Tasks ---

@task
def initialize_database():
    logger = get_run_logger()
    logger.info("Initializing database...")
    init_db()
    seed_vendors()
    logger.info("Database initialized and vendors seeded.")


@task
def fetch_products_for_vendor(vendor_id: int):
    logger = get_run_logger()
    logger.info(f"Fetching products for vendor {vendor_id}...")
    products = fetch_all_products(vendor_id=vendor_id)
    logger.info(f"Fetched {len(products)} products for vendor {vendor_id}.")
    return products


@task
def fetch_mappings_for_vendor(vendor_id: int):
    logger = get_run_logger()
    logger.info(f"Fetching mappings (brands, categories, shipping tiers) for vendor {vendor_id}...")

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

    logger.info(f"Fetched {len(brands)} brands, {len(categories)} categories, {len(shipping_tiers)} shipping tiers for vendor {vendor_id}.")
    return brands, categories, shipping_tiers


@task
def attach_mappings_to_products(products: list, brands: dict, categories: dict, shipping_tiers: dict):
    logger = get_run_logger()
    logger.info(f"Attaching mappings to {len(products)} products...")

    for p in products:
        p["brand_name"] = brands.get(p.get("brand_id"), "Unknown Brand")
        p["category_name"] = categories.get(p.get("category_id"), "Unknown Category")
        shipping_info = shipping_tiers.get(p.get("shipping_tier_id"), {})
        p["shipping_tier"] = shipping_info.get("shipping_tier", "Standard")
        p["shipping_cost"] = shipping_info.get("shipping_cost", 0)

    logger.info(f"Completed attaching mappings to products.")
    return products


@task
def transform(products):
    logger = get_run_logger()
    logger.info(f"Transforming {len(products)} products...")
    transformed = transform_products(products)
    logger.info(f"Transformation complete. {len(transformed)} products transformed.")
    return transformed


@task
def load(products):
    logger = get_run_logger()
    logger.info(f"Upserting {len(products)} products into database...")
    upsert_products(products)
    logger.info("Load completed successfully.")


# --- Flow ---

@flow(name="repricing_pipeline")
def repricing_pipeline_flow():
    initialize_database()

    vendor_ids = [1, 2, 3, 4, 5]  # Example vendor IDs
    all_transformed = []

    for vid in vendor_ids:
        raw_products = fetch_products_for_vendor(vid)
        brands, categories, shipping_tiers = fetch_mappings_for_vendor(vid)
        products_with_mappings = attach_mappings_to_products(raw_products, brands, categories, shipping_tiers)
        transformed = transform(products_with_mappings)
        all_transformed.extend(transformed)

    load(all_transformed)
    logger = get_run_logger()
    logger.info("Pipeline completed successfully!")


if __name__ == "__main__":
    repricing_pipeline_flow()
