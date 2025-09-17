-- Vendors table
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id INTEGER PRIMARY KEY,
    name TEXT
);

-- Brands table
CREATE TABLE IF NOT EXISTS brands (
    brand_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    vendor_id INTEGER NOT NULL,
    UNIQUE(name, vendor_id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    vendor_id INTEGER NOT NULL,
    UNIQUE(name, vendor_id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

-- Shipping tiers table
CREATE TABLE IF NOT EXISTS shipping_tiers (
    shipping_tier_id INTEGER PRIMARY KEY,
    shipping_tier TEXT NOT NULL,
    shipping_cost REAL NOT NULL,
    vendor_id INTEGER NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

-- Products table (IDs from API)
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY, -- API-provided ID
    vendor_id INTEGER NOT NULL,
    sku TEXT,
    name TEXT,
    brand_id INTEGER,
    category_id INTEGER,
    cost REAL,
    shipping_cost REAL,
    shipping_tier_id INTEGER,
    extra_cost_applied REAL,
    target_margin REAL,
    calculated_price REAL,
    calculated_raw_price REAL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (brand_id) REFERENCES brands(brand_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (shipping_tier_id) REFERENCES shipping_tiers(shipping_tier_id)
);
