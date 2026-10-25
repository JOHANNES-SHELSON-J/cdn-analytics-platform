"""Split the raw CSV by day and upload each day to its S3 partition folder."""
import boto3
import pandas as pd
from pathlib import Path

BUCKET = "cdn-analytics-joey-2026"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "cdn_logs_july2026.csv"
STAGING = PROJECT_ROOT / "data" / "processed" / "daily_files"
STAGING.mkdir(parents=True, exist_ok=True)

s3 = boto3.client("s3")          # the remote control, using your aws configure credentials

print("Reading the full CSV...")
df = pd.read_csv(RAW_CSV, parse_dates=["timestamp"])
df["date"] = df["timestamp"].dt.date

for day, day_df in df.groupby("date"):
    # 1. save that day's rows as a local file
    local_file = STAGING / f"logs_{day}.csv"
    day_df.drop(columns=["date"]).to_csv(local_file, index=False)

    # 2. build the S3 partition path:  raw/year=2026/month=07/day=18/logs.csv
    key = f"raw/year={day.year}/month={day.month:02d}/day={day.day:02d}/logs.csv"

    # 3. upload
    s3.upload_file(str(local_file), BUCKET, key)
    print(f"Uploaded {len(day_df):>6,} rows  ->  s3://{BUCKET}/{key}")

print("\nAll days uploaded.")