from retail_intelligence.data.synthetic import DEMO_CUSTOMER_ID, generate_all_sources
from retail_intelligence.genai.retention import generate_retention_action, generate_retention_actions
from retail_intelligence.ml.churn import reason_codes
from retail_intelligence.pipelines.customer360 import build_customer_360


def test_retention_action_preserves_customer_id():
    sources = generate_all_sources()
    customer_360 = build_customer_360(sources)
    demo = next(row for row in customer_360 if row["customer_id"] == DEMO_CUSTOMER_ID)
    prediction = {
        "customer_id": DEMO_CUSTOMER_ID,
        "churn_probability": 0.91,
        "risk_category": "High",
        "reason_codes": reason_codes(demo),
    }
    action = generate_retention_action(demo, prediction, sources["bronze_retention_documents"])
    assert action["customer_id"] == DEMO_CUSTOMER_ID
    assert action["generation_mode"] == "deterministic_fallback"


def test_retention_action_uses_customer_model_and_policy_context():
    sources = generate_all_sources()
    customer_360 = build_customer_360(sources)
    demo = next(row for row in customer_360 if row["customer_id"] == DEMO_CUSTOMER_ID)
    prediction = {
        "customer_id": DEMO_CUSTOMER_ID,
        "churn_probability": 0.91,
        "risk_category": "High",
        "reason_codes": reason_codes(demo),
    }
    action = generate_retention_action(demo, prediction, sources["bronze_retention_documents"])
    assert "Customer 360" in action["evidence_used"]
    assert "Churn model output" in action["evidence_used"]
    assert action["policy_excerpts"]
    assert "SEK" in action["estimated_business_rationale"]


def test_generate_retention_actions_matches_prediction_ids():
    sources = generate_all_sources()
    customer_360 = build_customer_360(sources)
    predictions = [
        {
            "customer_id": row["customer_id"],
            "churn_probability": 0.8,
            "risk_category": "High",
            "reason_codes": reason_codes(row),
        }
        for row in customer_360[:3]
    ]
    actions = generate_retention_actions(customer_360, predictions, sources["bronze_retention_documents"])
    assert [row["customer_id"] for row in actions] == [row["customer_id"] for row in predictions]
