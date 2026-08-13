"""
Shared helpers for the Rapid On-Demand Dashboard.
Imported by Home.py and every page in /pages so the data is loaded
once (thanks to st.cache_data) and every page shares the same look.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

# ============================================================
# PATHS
# ============================================================
DATA_DIR = Path(__file__).parent / "data"
PARQUET_PATH = DATA_DIR / "rod_clean_daily_order_with_coordinates.parquet"
CSV_PATH = DATA_DIR / "rod_clean_daily_order_with_coordinates.csv"


# ============================================================
# DATA LOADING (cached once across all pages)
# ============================================================
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and lightly clean the master order dataset.

    Prefers the Parquet file (smaller, faster, lighter on memory).
    Falls back to CSV if no Parquet file is present.
    """
    if PARQUET_PATH.exists():
        df = pd.read_parquet(PARQUET_PATH)
    elif CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH)
    else:
        raise FileNotFoundError(
            f"No dataset found. Expected {PARQUET_PATH.name} or {CSV_PATH.name} "
            f"inside {DATA_DIR}"
        )

    # Parse dates/times if present so grouping/sorting behaves correctly
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df


# ============================================================
# SHARED STYLING
# ============================================================
CUSTOM_CSS = """
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 12px 16px;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
    }
    section[data-testid="stSidebar"] {
        border-right: 1px solid #e6e6e6;
    }
</style>
"""


def apply_style() -> None:
    """Inject the shared CSS. Call once near the top of every page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# SHARED CONSTANTS
# ============================================================
WEEKDAY_ORDER = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

PERIOD_OPTIONS = ["All", "Morning Peak", "Evening Peak", "Off-Peak"]
DAY_TYPE_OPTIONS = ["All", "Weekday", "Weekend"]
