SELECT 'Bronze' AS layer, SUM(records) AS records
FROM (
  SELECT COUNT(*) AS records FROM workspace.retail_intelligence.bronze_customers
  UNION ALL SELECT COUNT(*) FROM workspace.retail_intelligence.bronze_transactions
  UNION ALL SELECT COUNT(*) FROM workspace.retail_intelligence.bronze_loyalty_activity
  UNION ALL SELECT COUNT(*) FROM workspace.retail_intelligence.bronze_support_tickets
  UNION ALL SELECT COUNT(*) FROM workspace.retail_intelligence.bronze_campaign_interactions
  UNION ALL SELECT COUNT(*) FROM workspace.retail_intelligence.bronze_retention_documents
)
UNION ALL
SELECT 'Silver', SUM(records)
FROM (
  SELECT COUNT(*) AS records FROM workspace.retail_intelligence.silver_customer_360
  UNION ALL SELECT COUNT(*) FROM workspace.retail_intelligence.silver_customer_activity
  UNION ALL SELECT COUNT(*) FROM workspace.retail_intelligence.silver_churn_features
  UNION ALL SELECT COUNT(*) FROM workspace.retail_intelligence.silver_retention_documents
  UNION ALL SELECT COUNT(*) FROM workspace.retail_intelligence.silver_data_quality_summary
)
UNION ALL
SELECT 'Gold', SUM(records)
FROM (
  SELECT COUNT(*) AS records FROM workspace.retail_intelligence.gold_customer_churn_predictions
  UNION ALL SELECT COUNT(*) FROM workspace.retail_intelligence.gold_customer_retention_actions
  UNION ALL SELECT COUNT(*) FROM workspace.retail_intelligence.gold_model_metrics
);

