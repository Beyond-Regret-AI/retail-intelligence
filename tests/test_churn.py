from retail_intelligence.data.synthetic import DEMO_CUSTOMER_ID, generate_all_sources
from retail_intelligence.ml.churn import business_signal_count, model_feature_rows, reason_codes, risk_category, training_label
from retail_intelligence.pipelines.customer360 import build_customer_360


def test_risk_category_thresholds():
    assert risk_category(0.10) == "Low"
    assert risk_category(0.35) == "Medium"
    assert risk_category(0.70) == "High"


def test_reason_codes_are_business_readable():
    customer_360 = build_customer_360(generate_all_sources())
    demo = next(row for row in customer_360 if row["customer_id"] == DEMO_CUSTOMER_ID)
    reasons = reason_codes(demo)
    assert "Declining spend" in reasons
    assert "Unresolved support issue" in reasons
    assert "Low campaign engagement" in reasons


def test_feature_rows_preserve_customer_id_and_label():
    customer_360 = build_customer_360(generate_all_sources())
    features = model_feature_rows(customer_360)
    assert {row["customer_id"] for row in features} == {row["customer_id"] for row in customer_360}
    demo = next(row for row in features if row["customer_id"] == DEMO_CUSTOMER_ID)
    assert demo["label"] == 1


def test_training_label_uses_unified_business_signals():
    customer_360 = build_customer_360(generate_all_sources())
    demo = next(row for row in customer_360 if row["customer_id"] == DEMO_CUSTOMER_ID)
    assert business_signal_count(demo) >= 3
    assert training_label(demo) == 1
