-- @param customer_id STRING
SELECT *
FROM workspace.retail_intelligence.gold_customer_retention_actions
WHERE customer_id = :customer_id;

