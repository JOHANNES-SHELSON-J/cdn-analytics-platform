import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "cdn_logs_july2026.csv", parse_dates=["timestamp"])

df["day"] = df["timestamp"].dt.day

# Average latency per region, for normal days vs the fault days
pivot = df.pivot_table(
    values="latency_ms",
    index="region",
    columns=df["day"].isin([18, 19, 20]).map({False: "normal_days", True: "fault_days"}),
    aggfunc="mean",
).round(1)

print(pivot)