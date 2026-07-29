SELECT
  risk_category,
  COUNT(*) AS customers
FROM workspace.retail_intelligence.gold_customer_churn_predictions
GROUP BY risk_category
ORDER BY
  CASE risk_category
    WHEN 'High' THEN 1
    WHEN 'Medium' THEN 2
    ELSE 3
  END;

