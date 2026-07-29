from __future__ import annotations


FEATURE_COLUMNS = [
    "transaction_count",
    "total_spend_sek",
    "return_count",
    "last_purchase_days",
    "spend_trend_ratio",
    "support_ticket_count",
    "open_support_ticket_count",
    "low_csat_count",
    "campaign_sent_count",
    "campaign_engagement_rate",
    "loyalty_event_count",
    "unused_loyalty_event_count",
    "unused_loyalty_points",
]


def risk_category(churn_probability: float) -> str:
    if churn_probability >= 0.70:
        return "High"
    if churn_probability >= 0.35:
        return "Medium"
    return "Low"


def reason_codes(row: dict) -> list[str]:
    reasons = []
    if row.get("spend_trend_ratio", 1.0) < 0.45:
        reasons.append("Declining spend")
    if row.get("last_purchase_days", 0) > 75:
        reasons.append("Long purchase inactivity")
    if row.get("open_support_ticket_count", 0) > 0:
        reasons.append("Unresolved support issue")
    if row.get("low_csat_count", 0) > 0:
        reasons.append("Low service satisfaction")
    if row.get("campaign_sent_count", 0) > 0 and row.get("campaign_engagement_rate", 1.0) < 0.20:
        reasons.append("Low campaign engagement")
    if row.get("unused_loyalty_points", 0) >= 8000:
        reasons.append("Unused loyalty benefits")
    if row.get("transaction_count", 0) > 0 and row.get("return_count", 0) / row["transaction_count"] >= 0.20:
        reasons.append("Elevated return frequency")
    return reasons[:4] or ["Stable recent behavior"]


def business_signal_count(row: dict) -> int:
    return sum(
        [
            row.get("spend_trend_ratio", 1.0) < 0.45,
            row.get("last_purchase_days", 0) > 75,
            row.get("open_support_ticket_count", 0) > 0,
            row.get("low_csat_count", 0) > 0,
            row.get("campaign_sent_count", 0) > 0 and row.get("campaign_engagement_rate", 1.0) < 0.20,
            row.get("unused_loyalty_points", 0) >= 8000,
            row.get("transaction_count", 0) > 0 and row.get("return_count", 0) / row["transaction_count"] >= 0.20,
        ]
    )


def training_label(row: dict) -> int:
    return int(bool(row.get("churn_label", 0)) or business_signal_count(row) >= 3)


def model_feature_rows(customer_360: list[dict]) -> list[dict]:
    rows = []
    for row in customer_360:
        feature_row = {"customer_id": row["customer_id"], "label": training_label(row)}
        feature_row.update({name: float(row[name]) for name in FEATURE_COLUMNS})
        rows.append(feature_row)
    return rows
