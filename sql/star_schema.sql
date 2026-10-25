-- Star schema: dimensions, fact load, governed views
USE WAREHOUSE cdn_wh;
USE DATABASE cdn_analytics;
USE SCHEMA warehouse;

CREATE OR REPLACE TABLE dim_region (
    region_key INTEGER, region_code VARCHAR, region_name VARCHAR, continent VARCHAR
);
INSERT INTO dim_region VALUES
    (1, 'us-east',  'US East (Ohio)',        'North America'),
    (2, 'us-west',  'US West (Oregon)',      'North America'),
    (3, 'eu-west',  'EU West (Ireland)',     'Europe'),
    (4, 'ap-south', 'Asia Pacific (Mumbai)', 'Asia'),
    (5, 'sa-east',  'South America (SP)',    'South America');

CREATE OR REPLACE TABLE dim_date AS
SELECT
    DATEADD(day, seq, '2026-07-01'::DATE)          AS date_key,
    DAYNAME(DATEADD(day, seq, '2026-07-01'::DATE)) AS day_name,
    CASE WHEN DAYNAME(DATEADD(day, seq, '2026-07-01'::DATE)) IN ('Sat','Sun')
         THEN TRUE ELSE FALSE END                  AS is_weekend
FROM (SELECT SEQ4() AS seq FROM TABLE(GENERATOR(ROWCOUNT => 31)));

CREATE OR REPLACE TABLE dim_customer AS
SELECT
    seq + 1                                              AS customer_key,
    'cust_' || LPAD(seq + 1, 3, '0')                     AS customer_id,
    CASE MOD(seq, 3) WHEN 0 THEN 'Enterprise'
                     WHEN 1 THEN 'Business' ELSE 'Startup' END AS tier,
    CASE MOD(seq, 5) WHEN 0 THEN 'Media' WHEN 1 THEN 'Gaming'
                     WHEN 2 THEN 'E-commerce' WHEN 3 THEN 'SaaS'
                     ELSE 'Education' END                AS industry
FROM (SELECT SEQ4() AS seq FROM TABLE(GENERATOR(ROWCOUNT => 20)));

CREATE OR REPLACE TABLE fact_requests (
    request_ts TIMESTAMP_NTZ, date_key DATE, region_key INTEGER, customer_key INTEGER,
    status_code INTEGER, latency_ms FLOAT, is_cache_hit BOOLEAN, bytes_sent BIGINT
);

INSERT INTO fact_requests
SELECT
    raw.$1:timestamp::TIMESTAMP_NTZ,
    raw.$1:timestamp::TIMESTAMP_NTZ::DATE,
    r.region_key,
    c.customer_key,
    raw.$1:status_code::INTEGER,
    raw.$1:latency_ms::FLOAT,
    (raw.$1:cache_status::VARCHAR = 'HIT'),
    raw.$1:bytes_sent::BIGINT
FROM @cdn_stage (FILE_FORMAT => 'parquet_fmt') raw
JOIN dim_region   r ON raw.$1:region::VARCHAR      = r.region_code
JOIN dim_customer c ON raw.$1:customer_id::VARCHAR = c.customer_id;

CREATE OR REPLACE VIEW vw_requests_enriched AS
SELECT
    f.request_ts, f.date_key, d.day_name, d.is_weekend,
    r.region_code, r.region_name, r.continent,
    c.customer_id, c.tier, c.industry,
    f.status_code,
    CASE WHEN f.status_code >= 500 THEN 'Server Error'
         WHEN f.status_code >= 400 THEN 'Client Error'
         ELSE 'Success' END AS status_class,
    f.latency_ms, f.is_cache_hit, f.bytes_sent
FROM fact_requests f
JOIN dim_region   r ON f.region_key   = r.region_key
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_date     d ON f.date_key     = d.date_key;

CREATE OR REPLACE VIEW vw_daily_region_summary AS
SELECT
    date_key, region_name, continent,
    COUNT(*)                                                      AS requests,
    ROUND(AVG(latency_ms), 1)                                     AS avg_latency_ms,
    ROUND(APPROX_PERCENTILE(latency_ms, 0.95), 1)                 AS p95_latency_ms,
    ROUND(AVG(CASE WHEN is_cache_hit THEN 1 ELSE 0 END) * 100, 1) AS cache_hit_pct,
    SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END)           AS server_errors,
    ROUND(SUM(bytes_sent) / 1e9, 2)                               AS gb_served
FROM vw_requests_enriched
GROUP BY date_key, region_name, continent;
