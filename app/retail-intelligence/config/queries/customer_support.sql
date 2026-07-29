-- @param customer_id STRING
SELECT
  opened_date,
  issue_type,
  status,
  priority,
  csat_score
FROM workspace.retail_intelligence.bronze_support_tickets
WHERE customer_id = :customer_id
ORDER BY opened_date DESC
LIMIT 12;

