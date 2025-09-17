# repricing_pipeline/tests/test_load.py

import pytest
from repricing_pipeline.load import init_db, upsert_products, _get_connection


@pytest.fixture
def db(tmp_path):
    """Provide a unique temporary database for each test."""
    db_file = tmp_path / "test.db"
    init_db(db_file)
    return db_file

def make_product(
    id,
    vendor_id=None,
    vendor_name=None,
    sku=None,
    name=None,
    brand_id=None,
    brand_name=None,
    category_id=None,
    category_name=None,
    cost=None,
    shipping_cost=None,
    shipping_tier_id=None,
    shipping_tier=None,
    extra_cost_applied=None,
    target_margin=None,
    calculated_price=None,
    calculated_raw_price=None,
):
    """Return a product dict with default/fallback values for testing."""
    return {
        "id": id,
        "vendor_id": vendor_id,
        "vendor_name": vendor_name,
        "sku": sku or f"SKU{id}",
        "name": name or f"Product{id}",
        "brand_id": brand_id,
        "brand_name": brand_name,
        "category_id": category_id,
        "category_name": category_name,
        "cost": cost or 0.0,
        "shipping_cost": shipping_cost or 0.0,
        "shipping_tier_id": shipping_tier_id,
        "shipping_tier": shipping_tier,
        "extra_cost_applied": extra_cost_applied or 0.0,
        "target_margin": target_margin or 0.0,
        "calculated_price": calculated_price or 0.0,
        "calculated_raw_price": calculated_raw_price or 0.0,
    }

def test_vendor_upsert(db):
    products = [
        make_product(id=1, vendor_id=1, vendor_name="VendorA"),
        make_product(id=2, vendor_id=1, vendor_name="VendorA"),  # duplicate vendor
        make_product(id=3, vendor_id=2, vendor_name="VendorB"),
    ]
    upsert_products(products, db_path=db)

    conn = _get_connection(db)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM vendors ORDER BY vendor_id")
        vendors = [row[0] for row in cur.fetchall()]
    finally:
        conn.close()

    assert vendors == ["VendorA", "VendorB"]


def test_brand_category_shipping_upsert(db):
    products = [
        make_product(
            id=1,
            vendor_id=1,
            vendor_name="VendorA",
            brand_id=10,
            brand_name="BrandX",
            category_id=20,
            category_name="CatA",
            shipping_tier_id=100,
            shipping_tier="Standard",
            shipping_cost=5.0,
        )
    ]
    upsert_products(products, db_path=db)

    conn = _get_connection(db)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM brands")
        brands = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT name FROM categories")
        categories = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT shipping_tier FROM shipping_tiers")
        shipping_tiers = [row[0] for row in cur.fetchall()]
    finally:
        conn.close()

    assert brands == ["BrandX"]
    assert categories == ["CatA"]
    assert shipping_tiers == ["Standard"]


def test_product_upsert_updates(db):
    product = make_product(
        id=1,
        vendor_id=1,
        vendor_name="VendorA",
        cost=100.0,
        calculated_price=120.0
    )
    upsert_products([product], db_path=db)

    # Update same product
    product_update = make_product(
        id=1,
        vendor_id=1,
        vendor_name="VendorA",
        cost=200.0,
        calculated_price=250.0
    )
    upsert_products([product_update], db_path=db)

    conn = _get_connection(db)
    try:
        cur = conn.cursor()
        cur.execute("SELECT cost, calculated_price FROM products WHERE id=?", (1,))
        row = cur.fetchone()
    finally:
        conn.close()

    assert row[0] == 200.0
    assert row[1] == 250.0


def test_integrity_constraints(db):
    """Test foreign key constraints by inserting invalid product."""
    invalid_product = make_product(
        id=99,
        vendor_id=999,
        brand_id=999,
        category_id=999,
        shipping_tier_id=999
    )

    # Should not raise error because upsert skips invalid foreign keys
    upsert_products([invalid_product], db_path=db)
