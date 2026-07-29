from retail_intelligence.data.synthetic import DEMO_CUSTOMER_ID, generate_all_sources


def test_synthetic_data_is_deterministic():
    first = generate_all_sources()
    second = generate_all_sources()
    assert first == second


def test_demo_customer_has_cross_source_story():
    sources = generate_all_sources()
    demo = next(row for row in sources["bronze_customers"] if row["customer_id"] == DEMO_CUSTOMER_ID)
    assert demo["loyalty_tier"] == "Platinum"
    assert demo["churn_label"] == 1
    assert any(row["customer_id"] == DEMO_CUSTOMER_ID for row in sources["bronze_transactions"])
    assert any(row["customer_id"] == DEMO_CUSTOMER_ID for row in sources["bronze_support_tickets"])
    assert any(row["customer_id"] == DEMO_CUSTOMER_ID for row in sources["bronze_campaign_interactions"])

