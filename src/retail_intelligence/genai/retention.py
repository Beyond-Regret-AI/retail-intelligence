from __future__ import annotations


def policy_excerpts(documents: list[dict], customer: dict, prediction: dict) -> list[str]:
    areas = []
    reasons = set(prediction.get("reason_codes", []))
    if "Unresolved support issue" in reasons or "Low service satisfaction" in reasons:
        areas.append("support")
    if "Low campaign engagement" in reasons:
        areas.append("offers")
    if "Unused loyalty benefits" in reasons or customer.get("unused_loyalty_points", 0) >= 8000:
        areas.append("loyalty")
    if prediction.get("risk_category") == "High":
        areas.append("margin")

    selected = []
    for area in areas:
        selected.extend([doc["content"] for doc in documents if doc["policy_area"] == area])
    return selected[:3]


def recommended_action(customer: dict, prediction: dict) -> tuple[str, str]:
    reasons = set(prediction.get("reason_codes", []))
    if "Unresolved support issue" in reasons:
        return (
            "Resolve open support issues, then send a personal service recovery offer.",
            "phone",
        )
    if "Unused loyalty benefits" in reasons:
        return (
            "Send a loyalty-benefit reminder with a limited premium-tier incentive.",
            "app_push",
        )
    if "Low campaign engagement" in reasons:
        return (
            "Move customer to a lower-frequency winback campaign with a clearer value message.",
            "email",
        )
    return (
        "Continue standard lifecycle nurture and monitor purchase trend.",
        "email",
    )


def generate_retention_action(customer: dict, prediction: dict, documents: list[dict]) -> dict:
    excerpts = policy_excerpts(documents, customer, prediction)
    action, channel = recommended_action(customer, prediction)
    probability_pct = round(float(prediction["churn_probability"]) * 100)
    risk_category = prediction["risk_category"]
    reasons = prediction.get("reason_codes", [])
    reasons_text = ", ".join(reasons[:3]).lower() if reasons else "stable recent behavior"
    first_name = customer["full_name"].split()[0]
    credit = 500 if risk_category == "High" and customer.get("loyalty_tier") in {"Gold", "Platinum"} else 250
    estimated_revenue_at_risk = round(float(customer.get("total_spend_sek", 0.0)) * float(prediction["churn_probability"]), 2)

    return {
        "customer_id": customer["customer_id"],
        "risk_summary": f"{customer['full_name']} is {risk_category.lower()} risk at {probability_pct}% churn probability, driven by {reasons_text}.",
        "recommended_intervention": action,
        "personalized_message": (
            f"Hi {first_name}, we noticed your recent experience has not matched your {customer['loyalty_tier']} benefits. "
            f"We would like to resolve this personally and add SEK {credit} toward your next order."
        ),
        "suggested_channel": channel,
        "estimated_business_rationale": (
            f"Estimated revenue at risk is SEK {estimated_revenue_at_risk:,.2f}; action is prioritized using Customer 360, churn score, and policy guidance."
        ),
        "evidence_used": [
            "Customer 360",
            "Churn model output",
            "Retention campaign guidelines",
            "Recent support history",
        ],
        "policy_excerpts": excerpts,
        "generation_mode": "deterministic_fallback",
    }


def generate_retention_actions(
    customer_360: list[dict],
    predictions: list[dict],
    documents: list[dict],
) -> list[dict]:
    customers = {row["customer_id"]: row for row in customer_360}
    actions = []
    for prediction in predictions:
        customer = customers[prediction["customer_id"]]
        actions.append(generate_retention_action(customer, prediction, documents))
    return actions

