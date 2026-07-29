SELECT
  COUNT(*) AS total_customers,
  SUM(CASE WHEN p.risk_category = 'High' THEN 1 ELSE 0 END) AS high_risk_customers,
  ROUND(SUM(CASE WHEN p.risk_category = 'High' THEN c.total_spend_sek * p.churn_probability ELSE 0 END), 2) AS revenue_at_risk_sek,
  SUM(CASE WHEN p.risk_category IN ('High', 'Medium') THEN 1 ELSE 0 END) AS retention_opportunities,
  MAX(p.scoring_timestamp) AS last_scoring_timestamp
FROM workspace.retail_intelligence.gold_customer_churn_predictions p
JOIN workspace.retail_intelligence.silver_customer_360 c
  ON p.customer_id = c.customer_id;

