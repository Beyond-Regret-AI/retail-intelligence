-- @param customer_id STRING
SELECT
  transaction_date,
  category,
  amount_sek,
  returned
FROM workspace.retail_intelligence.bronze_transactions
WHERE customer_id = :customer_id
ORDER BY transaction_date DESC
LIMIT 12;

