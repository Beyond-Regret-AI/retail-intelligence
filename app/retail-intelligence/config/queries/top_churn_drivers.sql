SELECT
  reason_code,
  COUNT(*) AS customers
FROM workspace.retail_intelligence.gold_customer_churn_predictions
LATERAL VIEW explode(reason_codes) exploded AS reason_code
GROUP BY reason_code
ORDER BY customers DESC
LIMIT 6;

