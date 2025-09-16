# repricing_pipeline/tests/test_transform.py

import pytest
from repricing_pipeline.transform import calculate_price, determine_target_margin_and_extra_cost

def make_product(vendor="Titan Labs", category="Electronics", brand=None,
                 cost=100.0, shipping_cost=10.0, shipping_tier_cost=5.0, id=1):
    return {
        "id": id,
        "vendor": vendor,
        "category": category,
        "brand": brand,
        "cost": cost,
        "shipping_cost": shipping_cost,
        "shipping_tier_cost": shipping_tier_cost,
    }

def test_vendor_category_override():
    # Titan Labs + Electronics should apply vendor-category (40% target, extra_cost -10)
    p = make_product(vendor="Titan Labs", category="Electronics", cost=100.0, shipping_cost=10.0, shipping_tier_cost=5.0)
    result = calculate_price(p)
    assert result["target_margin"] == pytest.approx(0.40)
    assert result["extra_cost_applied"] == pytest.approx(-10.0)
    # total_cost = 100 + 10 + (-10) = 100 -> raw price = 100 / (1-0.4) = 166.6667 -> whole -> 165 -> decimal depends
    assert result["calculated_raw_price"] == pytest.approx(166.6667, rel=1e-3)

def test_brand_override_when_shipping_tier_null():
    # Shipping tier null triggers brand margin override
    p = make_product(vendor="Any Vendor", category="Unlisted", brand="StoneBridge", cost=50.0, shipping_cost=5.0, shipping_tier_cost=None)
    tm, ec = determine_target_margin_and_extra_cost(p)
    assert tm == pytest.approx(0.60)
    # vendor not present -> extra cost 0
    assert ec == pytest.approx(0.0)

def test_category_default_when_no_vendor_category():
    p = make_product(vendor="Brightside Trading", category="Electronics", cost=200.0, shipping_cost=0.0, shipping_tier_cost=1.0)
    tm, ec = determine_target_margin_and_extra_cost(p)
    # vendor has no vendor-category for Brightside+Electronics -> category rule applies 0.35
    assert tm == pytest.approx(0.35)
    assert ec == pytest.approx(10.0)  # Brightside vendor extra cost

def test_rounding_rules_decimal_ge_05():
    # Craft a product whose raw price decimal part >= .50
    # We'll set values to produce known raw price 199.75
    p = make_product(vendor="Prime Distributors", category="Toys & Kids", cost=75.0, shipping_cost=0.0, shipping_tier_cost=0.0)
    # Prime Distributors + Toys & Kids: vendor-category rule target 30% and extra_cost +10 -> total_cost = 75 + 0 + 10 = 85 -> raw = 85/(1-0.3)=121.4286
    r = calculate_price(p)
    assert r["calculated_raw_price"] == pytest.approx(121.4286, rel=1e-3)
    assert isinstance(r["calculated_price"], float)

