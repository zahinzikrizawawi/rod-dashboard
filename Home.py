import streamlit as st

from utils import apply_style, load_data

# ============================================================
# PAGE CONFIG (only needs to be set once here for the app-wide
# defaults; each page in /pages sets its own title/icon too)
# ============================================================
st.set_page_config(
    page_title="Rapid On-Demand Dashboard",
    page_icon="🚐",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_style()

# ============================================================
# HEADER
# ============================================================
st.title("🚐 Rapid On-Demand Dashboard")
st.markdown(
    "A multi-page view of Rapid On-Demand's operations — demand, "
    "spatial patterns, fleet allocation, and zone performance."
)
st.divider()

# ============================================================
# QUICK DATA HEALTH CHECK
# ============================================================
try:
    df = load_data()
    st.success(f"Data loaded successfully — {len(df):,} trip records found.")
except FileNotFoundError:
    st.error(
        "Couldn't find `data/rod_clean_daily_order_with_coordinates.csv`. "
        "Place your dataset in the `data/` folder using that exact filename."
    )
    st.stop()

# ============================================================
# NAVIGATION CARDS
# ============================================================
st.subheader("📂 Explore the Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 📊 Executive Summary")
        st.write("High-level KPIs, daily demand trends, and top zones.")
        st.page_link("pages/1_Executive_Summary.py", label="Open page →", icon="📊")

    with st.container(border=True):
        st.markdown("### 🚐 Fleet Allocation Analysis")
        st.write("Van deployment across zones and hours vs. demand.")
        st.page_link("pages/4_Fleet_Allocation_Analysis.py", label="Open page →", icon="🚐")

with col2:
    with st.container(border=True):
        st.markdown("### 📍 Spatial Demand Analysis")
        st.write("Interactive pickup/dropoff heat map by zone and stop.")
        st.page_link("pages/2_Spatial_Demand_Analysis.py", label="Open page →", icon="📍")

    with st.container(border=True):
        st.markdown("### 📈 Zone Performance Analysis")
        st.write("Waiting, travel, and total time performance by zone.")
        st.page_link("pages/5_Zone_Performance_Analysis.py", label="Open page →", icon="📈")

with col3:
    with st.container(border=True):
        st.markdown("### 🔀 OD Strategic Flow Analysis")
        st.write("Pickup hotspots, dominant OD pairs, and fleet staging recommendations.")
        st.page_link("pages/3_OD_Flow_Analysis.py", label="Open page →", icon="🔀")

st.divider()
st.caption("Use the sidebar to navigate between pages at any time.")
