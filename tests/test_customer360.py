from retail_intelligence.data.synthetic import DEMO_CUSTOMER_ID, generate_all_sources
from retail_intelligence.pipelines.customer360 import build_customer_360, data_quality_summary


def test_customer_360_preserves_customer_id():
    sources = generate_all_sources()
    customer_360 = build_customer_360(sources)
    source_ids = {row["customer_id"] for row in sources["bronze_customers"]}
    silver_ids = {row["customer_id"] for row in customer_360}
    assert source_ids == silver_ids


def test_demo_customer_has_expected_risk_signals():
    customer_360 = build_customer_360(generate_all_sources())
    demo = next(row for row in customer_360 if row["customer_id"] == DEMO_CUSTOMER_ID)
    assert demo["open_support_ticket_count"] >= 4
    assert demo["campaign_engagement_rate"] == 0
    assert demo["unused_loyalty_points"] >= 15000


def test_data_quality_summary_passes_for_generated_sources():
    summary = data_quality_summary(generate_all_sources())
    assert {row["quality_status"] for row in summary} == {"pass"}

