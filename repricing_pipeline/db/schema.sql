-- repricing_pipeline/db/schema.sql

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY, -- assume API provides integer id
    vendor_id INTEGER,
    sku TEXT,
    title TEXT,
    brand TEXT,
    category TEXT,
    cost REAL,
    shipping_cost REAL,
    shipping_tier_cost REAL,
    extra_cost_applied REAL,
    target_margin REAL,
    calculated_price REAL,
    calculated_raw_price REAL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_products_sku_vendor ON products(sku, vendor_id);
