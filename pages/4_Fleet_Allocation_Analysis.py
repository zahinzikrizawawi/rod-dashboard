import streamlit as st
import plotly.express as px

from utils import apply_style, load_data, PERIOD_OPTIONS, DAY_TYPE_OPTIONS

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Fleet Allocation Analysis",
    page_icon="🚐",
    layout="wide"
)
apply_style()

df = load_data()

# ============================================================
# HEADER
# ============================================================
st.title("🚐 Fleet Allocation Analysis")
st.markdown("Evaluate historical fleet deployment across zones and operating hours.")
st.divider()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("🔎 Filters")

    zone = st.selectbox("Zone", ["All"] + sorted(df["zone_name"].dropna().unique()))
    day_type = st.selectbox("Day Type", DAY_TYPE_OPTIONS)
    period = st.selectbox("Period", PERIOD_OPTIONS)

# ============================================================
# FILTER
# ============================================================
fleet = df.copy()

if zone != "All":
    fleet = fleet[fleet["zone_name"] == zone]
if day_type != "All":
    fleet = fleet[fleet["day_type"] == day_type]
if period != "All":
    fleet = fleet[fleet["period"] == period]

if fleet.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ============================================================
# DAILY ACTIVE VANS
# ============================================================
daily_vans = (
    fleet.groupby(["date", "zone_name"])["plate_number"]
    .nunique()
    .reset_index(name="active_vans")
)

# ============================================================
# KPI
# ============================================================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Unique Vans", fleet["plate_number"].nunique())
col2.metric("Average Active Vans / Day", f"{daily_vans['active_vans'].mean():.1f}")
col3.metric("Completed Trips", f"{len(fleet):,}")

trips_per_van = len(fleet) / fleet["plate_number"].nunique()
col4.metric("Trips per Van", f"{trips_per_van:.1f}")

st.divider()

# ============================================================
# CHART 1: VANS BY ZONE + BY HOUR
# ============================================================
left, right = st.columns(2)

with left:
    st.subheader("Average Active Vans by Zone")
    zone_vans = (
        daily_vans.groupby("zone_name")["active_vans"]
        .mean()
        .reset_index()
        .sort_values("active_vans", ascending=False)
    )
    fig = px.bar(
        zone_vans, x="active_vans", y="zone_name", orientation="h",
        color="active_vans", color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Average Active Vans by Hour")
    hourly = (
        fleet.groupby(["date", "hour"])["plate_number"]
        .nunique()
        .reset_index(name="active_vans")
    )
    hourly = hourly.groupby("hour")["active_vans"].mean().reset_index()
    fig = px.line(hourly, x="hour", y="active_vans", markers=True)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# DEMAND VS FLEET
# ============================================================
st.subheader("Demand vs Fleet Allocation")

orders = fleet.groupby(["date", "zone_name"]).size().reset_index(name="orders")
compare = orders.merge(daily_vans, on=["date", "zone_name"])

compare = (
    compare.groupby("zone_name")
    .agg(avg_orders=("orders", "mean"), avg_vans=("active_vans", "mean"))
    .reset_index()
)

fig = px.scatter(
    compare, x="avg_vans", y="avg_orders",
    size="avg_orders", hover_name="zone_name",
    labels={"avg_vans": "Average Active Vans", "avg_orders": "Average Daily Orders"}
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# SUMMARY TABLE
# ============================================================
st.subheader("Zone Fleet Summary")

summary = compare.copy()
summary["Trips per Van"] = (summary["avg_orders"] / summary["avg_vans"]).round(2)

summary = summary.rename(columns={
    "zone_name": "Zone",
    "avg_orders": "Average Daily Orders",
    "avg_vans": "Average Active Vans"
}).sort_values("Average Daily Orders", ascending=False)

st.dataframe(summary, use_container_width=True, hide_index=True)
