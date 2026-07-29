-- @param customer_id STRING
SELECT *
FROM workspace.retail_intelligence.silver_customer_360
WHERE customer_id = :customer_id;

