SELECT
  table_name,
  record_count,
  quality_status
FROM workspace.retail_intelligence.silver_data_quality_summary
ORDER BY table_name;
