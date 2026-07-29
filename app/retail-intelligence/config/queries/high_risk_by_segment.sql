SELECT
  c.segment,
  c.loyalty_tier,
  COUNT(*) AS high_risk_customers,
  ROUND(SUM(c.total_spend_sek * p.churn_probability), 2) AS revenue_at_risk_sek
FROM workspace.retail_intelligence.gold_customer_churn_predictions p
JOIN workspace.retail_intelligence.silver_customer_360 c
  ON p.customer_id = c.customer_id
WHERE p.risk_category = 'High'
GROUP BY c.segment, c.loyalty_tier
ORDER BY revenue_at_risk_sek DESC
LIMIT 8;

