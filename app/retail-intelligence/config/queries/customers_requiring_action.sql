SELECT
  p.customer_id,
  c.full_name,
  c.segment,
  c.loyalty_tier,
  p.risk_category,
  ROUND(p.churn_probability, 4) AS churn_probability,
  ROUND(c.total_spend_sek * p.churn_probability, 2) AS revenue_at_risk_sek,
  a.recommended_intervention,
  a.suggested_channel
FROM workspace.retail_intelligence.gold_customer_churn_predictions p
JOIN workspace.retail_intelligence.silver_customer_360 c
  ON p.customer_id = c.customer_id
JOIN workspace.retail_intelligence.gold_customer_retention_actions a
  ON p.customer_id = a.customer_id
WHERE p.risk_category IN ('High', 'Medium')
ORDER BY
  CASE p.risk_category WHEN 'High' THEN 1 ELSE 2 END,
  p.churn_probability DESC,
  revenue_at_risk_sek DESC
LIMIT 25;

