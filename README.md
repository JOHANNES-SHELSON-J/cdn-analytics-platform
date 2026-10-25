# CDN Analytics Platform

An end-to-end cloud data engineering and analytics platform built to process, transform, validate, and analyze Content Delivery Network (CDN) request logs.

## Project Overview

The platform simulates realistic CDN traffic across five geographical regions and 20 customers. It enables performance monitoring, cache analysis, data quality validation, and regional incident investigation.

## Technology Stack

- Python, Pandas, NumPy
- AWS S3
- AWS Glue
- Apache Spark / PySpark
- Amazon Athena
- Snowflake
- SQL
- Apache Parquet
- Jupyter Notebook
- Matplotlib and Seaborn
- AWS IAM and Boto3

## Architecture

```text
Python Synthetic Data Generator
              |
              v
     Amazon S3 (Raw CSV)
              |
              v
    AWS Glue Crawler & Catalog
              |
              v
      AWS Glue ETL (PySpark)
              |
              v
    Amazon S3 (Curated Parquet)
          /           \
         v             v
  Amazon Athena     Snowflake
         |             |
    Validation     Star Schema
                       |
                 Reporting Views

Python / Jupyter Notebook
    Incident Investigation
```

## Key Results

| Metric | Result |
|---|---:|
| Raw records generated | 930,000 |
| Cleaned records | 911,513 |
| Invalid records removed | 18,487 |
| Daily partitions | 31 |
| Geographical regions | 5 |
| Customers | 20 |
| CSV to Parquet size reduction | Approximately 79% |
| Incident latency increase | 2.98x |
| Total project cost | Approximately $1 |

## Data Engineering Pipeline

### 1. Synthetic Data Generation

Generated 930,000 realistic CDN request logs for July 2026 using seeded randomness and weighted probability distributions.

The dataset contains:

- timestamp
- region
- customer_id
- status_code
- latency_ms
- cache_status
- bytes_sent

Two intentional data issues were introduced to validate the pipeline and analytical methodology:

- Approximately 2% missing latency values.
- A threefold latency increase in the eu-west region between July 18 and 20.

### 2. AWS S3 Data Lake

Uploaded daily CSV files to Amazon S3 using Boto3.

Implemented Hive-style date partitioning:

```text
raw/year=2026/month=07/day=01/logs.csv
```

Partitioning allows query engines to skip irrelevant date partitions, reducing unnecessary data scans.

### 3. AWS Glue ETL

- Automatic schema discovery using Glue Crawler.
- Metadata management using Glue Data Catalog.
- Removal of records with missing latency values.
- Timestamp data type correction.
- Conversion from CSV to compressed Parquet.
- Preservation of daily partitions.

Validated that exactly 911,513 clean records remained after transformation.

### 4. Amazon Athena

Used serverless SQL queries to:

- Validate record counts.
- Check missing values.
- Analyze regional latency.
- Verify data transformation results.
- Query partitioned files directly from S3.

### 5. Snowflake Data Warehouse

Configured an X-SMALL compute warehouse with automatic suspension after 60 seconds.

Established secure S3 connectivity using an IAM role, storage integration, and external stage.

Implemented a dimensional star schema:

| Table | Responsibility |
|---|---|
| fact_requests | CDN request events and measures |
| dim_region | Region and continent information |
| dim_customer | Customer, tier and industry |
| dim_date | Date and weekday/weekend attributes |

Created two reusable reporting views:

- vw_requests_enriched
- vw_daily_region_summary

Reporting metrics include request volume, average latency, p95 latency, cache hit percentage, server errors, and bandwidth consumption.

## Incident Investigation

Conducted exploratory data analysis using Python and Jupyter Notebook to investigate a simulated regional performance incident.

| Metric | Normal | Incident |
|---|---:|---:|
| Regional average latency | 100 ms | 298.6 ms |
| P95 latency | 353 ms | 1,051 ms |
| Cache hit rate | 80.0% | 80.1% |
| Cache HIT latency | 50 ms | 149.7 ms |

### Findings

- Global average latency concealed the severity of the localized incident.
- Regional analysis isolated the issue to eu-west during July 18–20.
- Cache hit rates remained stable.
- Increased latency affected even cache HIT requests.
- Results were consistent with the intentionally simulated infrastructure degradation.

**Recommendation:** Implement region-level p95 latency monitoring and alerting instead of relying exclusively on global averages.

## Data Quality and Reconciliation

Validated the pipeline by comparing Athena and Snowflake results across independent storage and query systems.

Both systems returned:

- 911,513 cleaned records.
- Approximately 911.5 GB of total simulated bandwidth served.

## Technical Challenges

### AWS IAM 403 Forbidden Error

The initial Glue ETL job failed because its IAM role lacked permission to write objects to the curated S3 location.

Identified the missing s3:PutObject permission, updated the role permissions, and successfully completed the transformation.

A production implementation would use narrowly scoped IAM policies following the principle of least privilege.

### Schema Inference

The Glue crawler initially inferred timestamps as strings because CSV files do not contain embedded type information.

Corrected the timestamp type during ETL and converted the curated dataset to Parquet.

## Project Structure

```text
cdn_analytics/
├── scripts/
│   ├── generate_logs.py
│   ├── upload_to_s3.py
│   └── verify_data.py
├── sql/
│   ├── snowflake_setup.sql
│   ├── star_schema.sql
│   └── validation.sql
├── notebooks/
│   └── incident_investigation.ipynb
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

Clone the repository:

```bash
git clone https://github.com/JOHANNES-SHELSON-J/cdn-analytics-platform.git
cd cdn-analytics-platform
```

Create a Python environment and install dependencies:

```bash
python3 -m venv cdn_venv
source cdn_venv/bin/activate
pip install -r requirements.txt
```

Review the configuration and scripts before execution. AWS and Snowflake operations require separately configured cloud accounts and may incur charges.

Replace account-specific placeholders and S3 bucket locations with your own configuration.

## Security and Cost Management

- No cloud credentials are intentionally stored in the repository.
- AWS authentication is managed outside the source code.
- S3 public access was blocked.
- Snowflake uses IAM-based storage integration.
- Snowflake compute was configured to auto-suspend.
- Unnecessary Glue resources were removed after project completion.
- Large datasets and virtual environments are excluded from Git.

## Future Improvements

- Incremental data ingestion.
- Automated pipeline orchestration using Apache Airflow.
- Automated data quality tests.
- Infrastructure as Code using Terraform.
- Power BI reporting dashboard.
- Regional anomaly detection and automated alerts.

## Author

Johannes Johnson

- [LinkedIn](https://www.linkedin.com/in/johannes-johnson-882636257/)
- [Portfolio](https://johannes-johnson-portfolio.vercel.app)
- [GitHub](https://github.com/JOHANNES-SHELSON-J)

This project uses synthetic CDN telemetry for educational and portfolio purposes.