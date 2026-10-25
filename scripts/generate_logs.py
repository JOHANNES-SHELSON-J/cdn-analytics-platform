import random
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT_ROOT / "data" / "raw" / "cdn_logs_july2026.csv"

REGIONS = ["us-east", "us-west", "eu-west", "ap-south", "sa-east"]
CUSTOMERS = [f"cust_{i:03d}" for i in range(1, 21)]        # cust_001 ... cust_020

START = datetime(2026, 7, 1)
DAYS = 31
ROWS_PER_DAY = 30_000                                       # ~930k rows total

# The planted fault: eu-west runs slow on these days
SLOW_REGION = "eu-west"
SLOW_DAYS = {18, 19, 20}
SLOW_MULTIPLIER = 3.0

def make_one_log(when):
    region = random.choice(REGIONS)
    cache = random.choices(["HIT", "MISS"], weights=[80, 20])[0]

    if cache == "HIT":
        latency = random.gauss(50, 15)
    else:
        latency = random.gauss(300, 80)

    # PLANTED PROBLEM 1: the slow days in one region
    if region == SLOW_REGION and when.day in SLOW_DAYS:
        latency *= SLOW_MULTIPLIER

    # PLANTED PROBLEM 2: ~2% of records lose their latency value
    if random.random() < 0.02:
        latency = None

    return {
        "timestamp": when,
        "region": region,
        "customer_id": random.choice(CUSTOMERS),
        "status_code": random.choices([200, 404, 500], weights=[96, 3, 1])[0],
        "latency_ms": round(max(latency, 1), 1) if latency is not None else None,
        "cache_status": cache,
        "bytes_sent": random.randint(500, 2_000_000),
    }

def random_time_on(day_start):
    """A random moment within that day."""
    seconds_into_day = random.randint(0, 86_399)
    return day_start + timedelta(seconds=seconds_into_day)

# --- generate the month ---
random.seed(42)          # same "random" data every run  -> reproducible
all_logs = []
for d in range(DAYS):
    day_start = START + timedelta(days=d)
    for _ in range(ROWS_PER_DAY):
        all_logs.append(make_one_log(random_time_on(day_start)))
    print(f"Generated day {day_start.date()}")

df = pd.DataFrame(all_logs).sort_values("timestamp")
df.to_csv(OUT_PATH, index=False)
print(f"\nSaved {len(df):,} rows to {OUT_PATH}")
print(f"Missing latency values: {df['latency_ms'].isna().sum():,}")