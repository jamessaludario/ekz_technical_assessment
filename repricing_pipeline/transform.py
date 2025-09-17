# repricing_pipeline/transform.py

from typing import Dict, Tuple, List
import math

# Default margin
DEFAULT_TARGET_MARGIN = 0.12

# Vendor-level rules
VENDOR_RULES = {
    "Evergreen Merchants": {"extra_cost": 15.0, "target_margin": 0.16},
    "Titan Labs": {"extra_cost": 20.0, "target_margin": 0.20},
    "Prime Distributors": {"extra_cost": 10.0, "target_margin": 0.15},
    "Pacific Supply Group": {"extra_cost": 0.0, "target_margin": 0.16},
    "Brightside Trading": {"extra_cost": 10.0, "target_margin": 0.15},
}

# Category rules
CATEGORY_RULES = {
    "Automotive & Industrial": 0.30,
    "Electronics": 0.35,
    "Toys & Kids": 0.25,
    "Beauty & Health": 0.20,
    "Furniture & Home": 0.25,
}

# Vendor + Category overrides
VENDOR_CATEGORY_RULES = {
    ("Evergreen Merchants", "Automotive & Industrial"): {"target_margin": 0.35, "extra_cost": 0.0},
    ("Titan Labs", "Electronics"): {"target_margin": 0.40, "extra_cost": -10.0},
    ("Prime Distributors", "Toys & Kids"): {"target_margin": 0.30, "extra_cost": 10.0},
    ("Pacific Supply Group", "Furniture & Home"): {"target_margin": 0.35, "extra_cost": 20.0},
}

# Brand rules (applied if no shipping tier cost)
BRAND_RULES = {
    "StoneBridge": 0.60,
    "BrightLeaf": 0.60,
    "Night Owl": 0.50,
    "SilverFox": 0.45,
    "Blue Horizon": 0.40,
    "StormForge": 0.35,
    "RapidStream": 0.50,
}


def _apply_rounding(raw_price: float) -> float:
    """Rounds the price to nearest odd whole + .45/.95 decimal as per rules."""
    if raw_price is None:
        return None
    if raw_price < 0:
        raise ValueError("raw_price must be non-negative")

    whole = int(math.floor(raw_price))
    if whole % 2 == 0:
        whole -= 1
    if whole < 1:
        whole = 1

    decimal = raw_price - math.floor(raw_price)
    final = whole + (0.95 if decimal >= 0.5 else 0.45)
    return round(final, 2)


def determine_target_margin_and_extra_cost(product: Dict) -> Tuple[float, float]:
    """Determine target margin and extra cost based on brand, vendor, and category rules."""
    vendor = product.get("vendor")
    category = product.get("category")
    brand = product.get("brand")

    shipping_tier_cost_raw = product.get("shipping_tier_cost", None)
    has_shipping_tier_cost = shipping_tier_cost_raw not in (None, "", 0, 0.0)

    # Brand rules override everything if no shipping tier cost
    if not has_shipping_tier_cost and brand in BRAND_RULES:
        return BRAND_RULES[brand], 0.0

    # Vendor rules
    vendor_rule = VENDOR_RULES.get(vendor, {"extra_cost": 0.0, "target_margin": DEFAULT_TARGET_MARGIN})
    vendor_extra = vendor_rule.get("extra_cost", 0.0)
    vendor_margin = vendor_rule.get("target_margin", DEFAULT_TARGET_MARGIN)

    # Vendor + Category overrides
    key = (vendor, category)
    if key in VENDOR_CATEGORY_RULES:
        vcr = VENDOR_CATEGORY_RULES[key]
        return vcr.get("target_margin", vendor_margin), vcr.get("extra_cost", vendor_extra)

    # Category rules
    if category in CATEGORY_RULES:
        return CATEGORY_RULES[category], vendor_extra

    # Default vendor rules
    return vendor_margin, vendor_extra


def calculate_price(product: Dict) -> Dict:
    """Calculate raw and final prices based on rules and rounding."""
    cost = float(product.get("cost", 0.0) or 0.0)
    shipping_cost = float(product.get("shipping_cost", 0.0) or 0.0)

    target_margin, extra_cost_applied = determine_target_margin_and_extra_cost(product)

    # Total cost includes extra cost
    total_cost = cost + shipping_cost + (extra_cost_applied or 0.0)

    if (1 - target_margin) <= 0:
        raise ValueError("Invalid target margin >= 1")

    raw_price = total_cost / (1 - target_margin)
    final_price = _apply_rounding(raw_price)

    # Ensure IDs are present for DB schema
    brand_id = product.get("brand_id") or product.get("brand_id_from_api")
    category_id = product.get("category_id") or product.get("category_id_from_api")
    shipping_tier_id = product.get("shipping_tier_id") or product.get("shipping_tier_id_from_api")

    return {
        **product,
        "brand_id": brand_id,
        "category_id": category_id,
        "shipping_tier_id": shipping_tier_id,
        "target_margin": target_margin,
        "extra_cost_applied": extra_cost_applied,
        "total_cost": total_cost,
        "calculated_raw_price": round(raw_price, 4),
        "calculated_price": final_price,
    }


def transform_products(products: List[Dict]) -> List[Dict]:
    """Apply pricing transformation to a list of products."""
    transformed = []
    for p in products:
        try:
            transformed.append(calculate_price(p))
        except Exception as e:
            print(f"Skipping product {p.get('id', 'unknown')} due to error: {e}")
    return transformed
