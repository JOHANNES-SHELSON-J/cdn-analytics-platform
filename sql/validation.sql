-- Reconciliation: both engines must agree on row count AND value sum

-- Run in ATHENA:
SELECT COUNT(*) AS rows_curated, ROUND(SUM(bytes_sent)/1e9, 2) AS gb_total
FROM curated;

-- Run in SNOWFLAKE:
SELECT COUNT(*) AS rows_fact, ROUND(SUM(bytes_sent)/1e9, 2) AS gb_total
FROM cdn_analytics.warehouse.fact_requests;
