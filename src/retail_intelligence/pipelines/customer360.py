from __future__ import annotations

from collections import defaultdict
from datetime import date

from retail_intelligence.data.synthetic import BASE_DATE


def _days_since(value: str, as_of: date = BASE_DATE) -> int:
    return (as_of - date.fromisoformat(value)).days


def data_quality_summary(sources: dict[str, list[dict]]) -> list[dict]:
    customer_ids = {row["customer_id"] for row in sources["bronze_customers"] if row.get("customer_id")}
    summary = []
    for table_name, rows in sources.items():
        invalid_customer_id = 0
        invalid_amount = 0
        invalid_date = 0
        duplicate_keys = 0
        seen = set()
        for row in rows:
            key = next((row.get(k) for k in row if k.endswith("_id")), None)
            if key in seen:
                duplicate_keys += 1
            seen.add(key)
            if "customer_id" in row and (not row["customer_id"] or row["customer_id"] not in customer_ids):
                invalid_customer_id += 1
            if "amount_sek" in row and row["amount_sek"] <= 0:
                invalid_amount += 1
            for date_field in ("transaction_date", "event_date", "opened_date", "campaign_date", "signup_date"):
                if date_field in row:
                    try:
                        date.fromisoformat(row[date_field])
                    except ValueError:
                        invalid_date += 1
        summary.append(
            {
                "table_name": table_name,
                "record_count": len(rows),
                "invalid_customer_id_count": invalid_customer_id,
                "invalid_amount_count": invalid_amount,
                "invalid_date_count": invalid_date,
                "duplicate_key_count": duplicate_keys,
                "quality_status": "pass"
                if invalid_customer_id + invalid_amount + invalid_date + duplicate_keys == 0
                else "review",
            }
        )
    return summary


def build_customer_360(sources: dict[str, list[dict]]) -> list[dict]:
    txn = defaultdict(lambda: {"count": 0, "spend": 0.0, "returns": 0, "last_purchase_days": 9999, "recent": 0, "prior": 0})
    for row in sources["bronze_transactions"]:
        days = _days_since(row["transaction_date"])
        bucket = txn[row["customer_id"]]
        bucket["count"] += 1
        bucket["spend"] += float(row["amount_sek"])
        bucket["returns"] += int(bool(row["returned"]))
        bucket["last_purchase_days"] = min(bucket["last_purchase_days"], days)
        if days <= 60:
            bucket["recent"] += float(row["amount_sek"])
        elif days <= 180:
            bucket["prior"] += float(row["amount_sek"])

    support = defaultdict(lambda: {"tickets": 0, "open": 0, "low_csat": 0})
    for row in sources["bronze_support_tickets"]:
        bucket = support[row["customer_id"]]
        bucket["tickets"] += 1
        bucket["open"] += int(row["status"] in {"open", "pending"})
        bucket["low_csat"] += int(int(row["csat_score"]) <= 2)

    campaign = defaultdict(lambda: {"sent": 0, "opened": 0, "clicked": 0})
    for row in sources["bronze_campaign_interactions"]:
        bucket = campaign[row["customer_id"]]
        bucket["sent"] += 1
        bucket["opened"] += int(bool(row["opened"]))
        bucket["clicked"] += int(bool(row["clicked"]))

    loyalty = defaultdict(lambda: {"events": 0, "unused": 0, "redeemed": 0})
    for row in sources["bronze_loyalty_activity"]:
        bucket = loyalty[row["customer_id"]]
        bucket["events"] += 1
        bucket["unused"] += int(row["event_type"] == "benefit_unused")
        bucket["redeemed"] += int(row["event_type"] == "points_redeemed")

    rows = []
    for customer in sources["bronze_customers"]:
        customer_id = customer["customer_id"]
        t = txn[customer_id]
        s = support[customer_id]
        c = campaign[customer_id]
        l = loyalty[customer_id]
        prior_spend = t["prior"] or 1.0
        spend_trend_ratio = round(t["recent"] / prior_spend, 3)
        engagement_rate = round(c["opened"] / c["sent"], 3) if c["sent"] else 0.0
        rows.append(
            {
                "customer_id": customer_id,
                "full_name": f"{customer['first_name']} {customer['last_name']}",
                "email": customer["email"],
                "segment": customer["segment"],
                "loyalty_tier": customer["loyalty_tier"],
                "region": customer["region"],
                "age_band": customer["age_band"],
                "signup_date": customer["signup_date"],
                "churn_label": customer["churn_label"],
                "transaction_count": t["count"],
                "total_spend_sek": round(t["spend"], 2),
                "return_count": t["returns"],
                "last_purchase_days": t["last_purchase_days"],
                "spend_trend_ratio": spend_trend_ratio,
                "support_ticket_count": s["tickets"],
                "open_support_ticket_count": s["open"],
                "low_csat_count": s["low_csat"],
                "campaign_sent_count": c["sent"],
                "campaign_engagement_rate": engagement_rate,
                "loyalty_event_count": l["events"],
                "unused_loyalty_event_count": l["unused"],
                "unused_loyalty_points": customer["unused_loyalty_points"],
            }
        )
    return rows


def build_customer_activity(customer_360: list[dict]) -> list[dict]:
    rows = []
    for row in customer_360:
        rows.append(
            {
                "customer_id": row["customer_id"],
                "activity_health": "weak"
                if row["last_purchase_days"] > 75 or row["spend_trend_ratio"] < 0.45
                else "stable",
                "support_health": "needs_attention" if row["open_support_ticket_count"] > 0 else "ok",
                "engagement_health": "low" if row["campaign_engagement_rate"] < 0.20 else "ok",
            }
        )
    return rows

