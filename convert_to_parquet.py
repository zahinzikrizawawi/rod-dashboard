"""
Run this once locally to convert your CSV dataset to Parquet.
Parquet is compressed and columnar, so it's typically 5-10x smaller
than CSV and much lighter to load into memory - important for staying
under Streamlit Community Cloud's 1 GB RAM limit.

Usage:
    pip install pandas pyarrow
    python convert_to_parquet.py
"""

import pandas as pd
from pathlib import Path

SRC = Path("data/rod_clean_daily_order_with_coordinates.csv")
DST = Path("data/rod_clean_daily_order_with_coordinates.parquet")

print(f"Reading {SRC} ...")
df = pd.read_csv(SRC)

print(f"Original CSV size: {SRC.stat().st_size / 1_000_000:.1f} MB")
print(f"Rows: {len(df):,}, Columns: {len(df.columns)}")

df.to_parquet(DST, compression="snappy", index=False)

print(f"Saved {DST}")
print(f"Parquet size: {DST.stat().st_size / 1_000_000:.1f} MB")
print("Done. You can now delete or .gitignore the original CSV.")
