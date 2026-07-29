-- @param customer_id STRING
SELECT *
FROM workspace.retail_intelligence.gold_customer_churn_predictions
WHERE customer_id = :customer_id;

