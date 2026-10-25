-- Snowflake setup: compute, storage, and the secure S3 bridge
USE ROLE ACCOUNTADMIN;

CREATE WAREHOUSE IF NOT EXISTS cdn_wh
  WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;
CREATE DATABASE IF NOT EXISTS cdn_analytics;
CREATE SCHEMA IF NOT EXISTS cdn_analytics.warehouse;

USE WAREHOUSE cdn_wh;
USE DATABASE cdn_analytics;
USE SCHEMA warehouse;

-- Trust handshake with AWS (replace <AWS_ACCOUNT_ID> with your account number)
CREATE OR REPLACE STORAGE INTEGRATION s3_cdn_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::<AWS_ACCOUNT_ID>:role/snowflake-s3-role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://cdn-analytics-joey-2026/curated/');

-- Returns Snowflake's IAM user ARN + external ID, used to build the AWS role trust policy
DESC INTEGRATION s3_cdn_integration;

CREATE OR REPLACE FILE FORMAT parquet_fmt TYPE = PARQUET;

CREATE OR REPLACE STAGE cdn_stage
  STORAGE_INTEGRATION = s3_cdn_integration
  URL = 's3://cdn-analytics-joey-2026/curated/'
  FILE_FORMAT = (TYPE = PARQUET);

LIST @cdn_stage;
