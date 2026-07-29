from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import random


SEED = 20260729
BASE_DATE = date(2026, 7, 29)
DEMO_CUSTOMER_ID = "CUST-0007"


@dataclass(frozen=True)
class DataSizes:
    customers: int = 500
    transactions: int = 4200
    loyalty_events: int = 500
    support_tickets: int = 300
    campaign_interactions: int = 300


FIRST_NAMES = [
    "Amina",
    "Erik",
    "Fatima",
    "Jonas",
    "Leila",
    "Mikael",
    "Noor",
    "Sara",
    "Sofia",
    "Yasmin",
]
LAST_NAMES = [
    "Andersson",
    "Berg",
    "Dahl",
    "Eklund",
    "Forsberg",
    "Holm",
    "Lind",
    "Nilsson",
    "Svensson",
    "Wallin",
]
SEGMENTS = ["Urban family", "Value seeker", "Premium home", "Digital native", "Suburban commuter"]
TIERS = ["Bronze", "Silver", "Gold", "Platinum"]
REGIONS = ["Stockholm", "Goteborg", "Malmo", "Uppsala", "Vasteras"]
CATEGORIES = ["Grocery", "Home", "Beauty", "Electronics", "Kids", "Apparel"]


def _customer_id(idx: int) -> str:
    return f"CUST-{idx:04d}"


def generate_customers(size: int = 500, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed)
    customers = []
    for idx in range(1, size + 1):
        tier = rng.choices(TIERS, weights=[0.40, 0.30, 0.20, 0.10], k=1)[0]
        segment = rng.choices(SEGMENTS, weights=[0.23, 0.28, 0.16, 0.20, 0.13], k=1)[0]
        signup_days_ago = rng.randint(90, 1800)
        customer = {
            "customer_id": _customer_id(idx),
            "first_name": rng.choice(FIRST_NAMES),
            "last_name": rng.choice(LAST_NAMES),
            "email": f"customer{idx:04d}@example-retail.se",
            "segment": segment,
            "loyalty_tier": tier,
            "region": rng.choice(REGIONS),
            "age_band": rng.choice(["18-29", "30-44", "45-59", "60+"]),
            "signup_date": (BASE_DATE - timedelta(days=signup_days_ago)).isoformat(),
            "unused_loyalty_points": rng.randint(0, 18000),
            "churn_label": 0,
        }
        customers.append(customer)

    for customer in customers:
        if customer["loyalty_tier"] in {"Gold", "Platinum"} and customer["unused_loyalty_points"] > 8000:
            customer["churn_label"] = int(rng.random() < 0.30)
        elif customer["segment"] == "Value seeker":
            customer["churn_label"] = int(rng.random() < 0.18)
        else:
            customer["churn_label"] = int(rng.random() < 0.09)

    demo = customers[6]
    demo.update(
        {
            "first_name": "Maja",
            "last_name": "Lindgren",
            "email": "maja.lindgren@example-retail.se",
            "segment": "Premium home",
            "loyalty_tier": "Platinum",
            "region": "Stockholm",
            "age_band": "30-44",
            "unused_loyalty_points": 15600,
            "churn_label": 1,
        }
    )
    return customers


def generate_transactions(customers: list[dict], size: int = 4200, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed + 1)
    customer_ids = [c["customer_id"] for c in customers]
    rows = []
    for idx in range(1, size + 1):
        customer_id = rng.choice(customer_ids)
        if customer_id == DEMO_CUSTOMER_ID:
            days_ago = rng.choice(list(range(75, 170)) + list(range(15, 75)))
            amount = round(rng.uniform(120, 520), 2)
            returned = rng.random() < 0.22
        else:
            days_ago = int(rng.triangular(1, 180, 35))
            base = rng.lognormvariate(5.75, 0.65)
            amount = round(max(35.0, min(base, 6500.0)), 2)
            returned = rng.random() < (0.05 if days_ago < 90 else 0.10)
        rows.append(
            {
                "transaction_id": f"TXN-{idx:06d}",
                "customer_id": customer_id,
                "transaction_date": (BASE_DATE - timedelta(days=days_ago)).isoformat(),
                "amount_sek": amount,
                "category": rng.choice(CATEGORIES),
                "returned": returned,
                "source_system": "mysql_transactions",
            }
        )

    rows.extend(
        [
            {
                "transaction_id": f"TXN-DEMO-{idx}",
                "customer_id": DEMO_CUSTOMER_ID,
                "transaction_date": (BASE_DATE - timedelta(days=135 - idx * 18)).isoformat(),
                "amount_sek": amount,
                "category": "Home",
                "returned": idx >= 4,
                "source_system": "mysql_transactions",
            }
            for idx, amount in enumerate([2450.0, 1880.0, 1220.0, 760.0, 330.0], start=1)
        ]
    )
    return rows


def generate_loyalty_activity(customers: list[dict], size: int = 500, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed + 2)
    customer_ids = [c["customer_id"] for c in customers]
    event_types = ["points_earned", "points_redeemed", "benefit_viewed", "benefit_unused"]
    rows = []
    for idx in range(1, size + 1):
        customer_id = rng.choice(customer_ids)
        event_type = rng.choices(event_types, weights=[0.45, 0.20, 0.20, 0.15], k=1)[0]
        if customer_id == DEMO_CUSTOMER_ID:
            event_type = rng.choice(["benefit_viewed", "benefit_unused"])
        rows.append(
            {
                "loyalty_event_id": f"LOY-{idx:05d}",
                "customer_id": customer_id,
                "event_date": (BASE_DATE - timedelta(days=rng.randint(1, 180))).isoformat(),
                "event_type": event_type,
                "points_delta": rng.randint(-3500, 1200),
                "source_system": "postgres_loyalty",
            }
        )
    return rows


def generate_support_tickets(customers: list[dict], size: int = 300, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed + 3)
    customer_ids = [c["customer_id"] for c in customers]
    issue_types = ["delivery_delay", "return_problem", "damaged_item", "loyalty_issue", "billing_question"]
    statuses = ["resolved", "resolved", "closed", "open", "pending"]
    rows = []
    for idx in range(1, size + 1):
        customer_id = DEMO_CUSTOMER_ID if idx <= 4 else rng.choice(customer_ids)
        opened_days_ago = rng.randint(1, 120)
        status = rng.choice(["open", "pending"]) if customer_id == DEMO_CUSTOMER_ID and idx <= 4 else rng.choice(statuses)
        rows.append(
            {
                "ticket_id": f"TCK-{idx:05d}",
                "customer_id": customer_id,
                "opened_date": (BASE_DATE - timedelta(days=opened_days_ago)).isoformat(),
                "issue_type": rng.choice(issue_types),
                "status": status,
                "priority": "high" if customer_id == DEMO_CUSTOMER_ID and idx <= 4 else rng.choice(["low", "medium", "high"]),
                "csat_score": 1 if customer_id == DEMO_CUSTOMER_ID and idx <= 4 else rng.randint(1, 5),
                "source_system": "saas_support",
            }
        )
    return rows


def generate_campaign_interactions(customers: list[dict], size: int = 300, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed + 4)
    customer_ids = [c["customer_id"] for c in customers if c["customer_id"] != DEMO_CUSTOMER_ID]
    rows = []
    for idx in range(1, size + 1):
        customer_id = DEMO_CUSTOMER_ID if idx <= 5 else rng.choice(customer_ids)
        opened = False if customer_id == DEMO_CUSTOMER_ID and idx <= 5 else rng.random() < 0.54
        clicked = opened and rng.random() < 0.22
        rows.append(
            {
                "campaign_interaction_id": f"CAM-{idx:05d}",
                "customer_id": customer_id,
                "campaign_date": (BASE_DATE - timedelta(days=rng.randint(1, 120))).isoformat(),
                "campaign_name": rng.choice(["summer_home", "loyalty_bonus", "winback_offer", "new_arrivals"]),
                "channel": rng.choice(["email", "sms", "app_push"]),
                "opened": opened,
                "clicked": clicked,
                "source_system": "saas_campaign",
            }
        )
    return rows


def generate_retention_documents(seed: int = SEED) -> list[dict]:
    return [
        {
            "document_id": "DOC-001",
            "title": "Retention campaign guidelines",
            "policy_area": "offers",
            "content": "High-risk Platinum customers with unresolved support issues qualify for personal outreach and a targeted service recovery offer.",
            "source_system": "internal_documents",
        },
        {
            "document_id": "DOC-002",
            "title": "Loyalty benefit policy",
            "policy_area": "loyalty",
            "content": "Customers with unused loyalty benefits should receive reminders before discounting. Escalate if benefit inactivity coincides with falling spend.",
            "source_system": "internal_documents",
        },
        {
            "document_id": "DOC-003",
            "title": "Customer-service playbook",
            "policy_area": "support",
            "content": "Open high-priority tickets should be resolved before sending broad marketing campaigns. A service apology is preferred over generic promotion.",
            "source_system": "internal_documents",
        },
        {
            "document_id": "DOC-004",
            "title": "Offer guardrails",
            "policy_area": "margin",
            "content": "Use SEK 250-500 retention credits for premium customers when projected revenue at risk exceeds SEK 2,000.",
            "source_system": "internal_documents",
        },
    ]


def generate_all_sources(sizes: DataSizes | None = None, seed: int = SEED) -> dict[str, list[dict]]:
    sizes = sizes or DataSizes()
    customers = generate_customers(sizes.customers, seed)
    return {
        "bronze_customers": customers,
        "bronze_transactions": generate_transactions(customers, sizes.transactions, seed),
        "bronze_loyalty_activity": generate_loyalty_activity(customers, sizes.loyalty_events, seed),
        "bronze_support_tickets": generate_support_tickets(customers, sizes.support_tickets, seed),
        "bronze_campaign_interactions": generate_campaign_interactions(customers, sizes.campaign_interactions, seed),
        "bronze_retention_documents": generate_retention_documents(seed),
    }
