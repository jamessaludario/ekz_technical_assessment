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

# --- Target margin / extra cost tests ---
def test_vendor_category_override():
    # Titan Labs + Electronics -> VC rule: 40%, extra -10
    p = make_product(vendor="Titan Labs", category="Electronics", cost=100, shipping_cost=10, shipping_tier_cost=5)
    result = calculate_price(p)
    assert result["target_margin"] == pytest.approx(0.4)
    assert result["extra_cost_applied"] == pytest.approx(-10)
    assert result["calculated_raw_price"] == pytest.approx(166.6667, rel=1e-3)

def test_brand_override_when_shipping_tier_null():
    # Shipping tier None triggers brand override
    p = make_product(vendor="Any Vendor", category="Unlisted", brand="StoneBridge", shipping_tier_cost=None, cost=50, shipping_cost=5)
    tm, ec = determine_target_margin_and_extra_cost(p)
    assert tm == pytest.approx(0.6)
    assert ec == pytest.approx(0.0)

def test_category_default_when_no_vendor_category():
    p = make_product(vendor="Brightside Trading", category="Electronics", cost=200, shipping_cost=0, shipping_tier_cost=1)
    tm, ec = determine_target_margin_and_extra_cost(p)
    assert tm == pytest.approx(0.35)  # category rule applies
    assert ec == pytest.approx(10.0)  # vendor extra cost

def test_vendor_rule_when_no_category_rules():
    p = make_product(vendor="Titan Labs", category="Unlisted", cost=100, shipping_cost=5)
    tm, ec = determine_target_margin_and_extra_cost(p)
    assert tm == pytest.approx(0.2)  # vendor rule
    assert ec == pytest.approx(20.0)

def test_extra_cost_waived():
    p = make_product(vendor="Evergreen Merchants", category="Automotive & Industrial", cost=100, shipping_cost=10)
    tm, ec = determine_target_margin_and_extra_cost(p)
    assert tm == pytest.approx(0.35)
    assert ec == pytest.approx(0.0)  # waived

def test_extra_cost_added():
    p = make_product(vendor="Prime Distributors", category="Toys & Kids", cost=50, shipping_cost=0)
    tm, ec = determine_target_margin_and_extra_cost(p)
    assert tm == pytest.approx(0.30)
    assert ec == pytest.approx(10.0)

# --- Rounding / calculated price tests ---
def test_rounding_decimal_ge_05():
    p = make_product(vendor="Prime Distributors", category="Toys & Kids", cost=75, shipping_cost=0, shipping_tier_cost=0)
    r = calculate_price(p)
    assert r["calculated_raw_price"] == pytest.approx(121.4286, rel=1e-3)
    assert isinstance(r["calculated_price"], float)
    # nearest lower odd: 121 -> decimal <0.5 -> 121.45
    assert r["calculated_price"] == pytest.approx(121.45)

def test_rounding_decimal_lt_05():
    p = make_product(cost=100, shipping_cost=0, shipping_tier_cost=0)
    r = calculate_price(p)
    raw = r["calculated_raw_price"]
    # nearest lower odd, decimal <0.5 -> .45
    whole = int(raw)
    if whole % 2 == 0: whole -= 1
    decimal = raw - int(raw)
    expected = whole + 0.45 if decimal < 0.5 else whole + 0.95
    assert r["calculated_price"] == pytest.approx(expected)

def test_rounding_whole_number_even():
    p = make_product(cost=200, shipping_cost=0, shipping_tier_cost=0)
    r = calculate_price(p)
    raw = r["calculated_raw_price"]
    whole = int(raw)
    if whole % 2 == 0: whole -= 1
    decimal = raw - int(raw)
    expected = whole + 0.45 if decimal < 0.5 else whole + 0.95
    assert r["calculated_price"] == pytest.approx(expected)

def test_shipping_tier_none_uses_brand_rule_and_zero_shipping():
    """Shipping tier null triggers brand rules and zero shipping tier cost."""
    p = make_product(vendor="Any Vendor", category="Unlisted", brand="Blue Horizon",
                     shipping_tier_cost=None, cost=50, shipping_cost=5)
    r = calculate_price(p)

    # Brand margin overrides
    assert r["target_margin"] == pytest.approx(0.4)

    # Total cost = cost + shipping_cost + extra cost (brand rule ignores shipping tier cost, not shipping_cost)
    expected_total_cost = 50 + 5 + 0  # cost + shipping_cost + extra_cost
    raw_price = expected_total_cost / (1 - 0.4)

    # Apply rounding rules
    whole = int(raw_price)
    if whole % 2 == 0:
        whole -= 1
    decimal = raw_price - int(raw_price)
    expected_final = whole + 0.45 if decimal < 0.5 else whole + 0.95

    assert r["calculated_price"] == pytest.approx(expected_final)


def test_no_vendor_category_brand():
    p = make_product(vendor="Unknown Vendor", category="Unknown Category", brand="Unknown Brand", cost=100, shipping_cost=10, shipping_tier_cost=5)
    tm, ec = determine_target_margin_and_extra_cost(p)
    assert tm == pytest.approx(0.12)
    assert ec == pytest.approx(0.0)
