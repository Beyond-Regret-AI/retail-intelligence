-- @param customer_id STRING
SELECT
  campaign_date,
  campaign_name,
  channel,
  opened,
  clicked
FROM workspace.retail_intelligence.bronze_campaign_interactions
WHERE customer_id = :customer_id
ORDER BY campaign_date DESC
LIMIT 12;

