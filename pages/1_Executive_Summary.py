import streamlit as st
import plotly.express as px

from utils import apply_style, load_data, WEEKDAY_ORDER

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Executive Summary",
    page_icon="📊",
    layout="wide"
)
apply_style()

df = load_data()

# ============================================================
# HEADER
# ============================================================
st.title("📊 Executive Summary")
st.markdown("High-level overview of demand, fleet, and service performance.")
st.divider()

# ============================================================
# KPI CALCULATIONS
# ============================================================
total_orders = len(df)
total_zones = df["zone_name"].nunique()
total_pickup_stops = df["pickup_stop_name"].nunique()
total_dropoff_stops = df["dropoff_stop_name"].nunique()
total_vans = df["plate_number"].nunique()

avg_wait = df["waiting_time_in_mins"].mean()
avg_travel = df["travel_time_in_mins"].mean()
avg_total = df["total_time_in_mins"].mean()
avg_distance = df["distance_in_km"].mean()

daily_orders = df.groupby("date").size().mean()

# ============================================================
# KPI ROW 1
# ============================================================
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Completed Trips", f"{total_orders:,}")
c2.metric("Zones", total_zones)
c3.metric("Pickup Stops", f"{total_pickup_stops:,}")
c4.metric("Dropoff Stops", f"{total_dropoff_stops:,}")
c5.metric("Active Vans", total_vans)

# ============================================================
# KPI ROW 2
# ============================================================
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Avg Waiting Time", f"{avg_wait:.2f} min")
c2.metric("Avg Travel Time", f"{avg_travel:.2f} min")
c3.metric("Avg Total Time", f"{avg_total:.2f} min")
c4.metric("Avg Distance", f"{avg_distance:.2f} km")
c5.metric("Avg Daily Orders", f"{daily_orders:.0f}")

st.divider()

# ============================================================
# DAILY DEMAND TREND
# ============================================================
st.subheader("📈 Daily Demand Trend")

daily = df.groupby("date").size().reset_index(name="Orders")

fig = px.line(daily, x="date", y="Orders", markers=True)
fig.update_layout(height=420)
st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TWO CHARTS: HOUR + WEEKDAY
# ============================================================
left, right = st.columns(2)

with left:
    st.subheader("Demand by Hour")
    hourly = df.groupby("hour").size().reset_index(name="Orders")
    fig = px.line(hourly, x="hour", y="Orders", markers=True)
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Demand by Weekday")
    weekday = (
        df.groupby("weekday").size()
        .reindex(WEEKDAY_ORDER)
        .reset_index(name="Orders")
    )
    fig = px.bar(
        weekday, x="weekday", y="Orders",
        color="Orders", color_continuous_scale="Blues"
    )
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# TWO CHARTS: PERIOD + TOP ZONES
# ============================================================
left, right = st.columns(2)

with left:
    st.subheader("Demand by Period")
    period = df.groupby("period").size().reset_index(name="Orders")
    fig = px.pie(period, names="period", values="Orders", hole=0.45)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Top 10 Zones")
    zone = (
        df.groupby("zone_name").size()
        .reset_index(name="Orders")
        .sort_values("Orders", ascending=False)
        .head(10)
    )
    fig = px.bar(
        zone, x="Orders", y="zone_name", orientation="h",
        color="Orders", color_continuous_scale="Viridis"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# ZONE SUMMARY TABLE
# ============================================================
st.subheader("📋 Zone Summary")

summary = (
    df.groupby("zone_name")
    .agg(
        Orders=("issue_id", "count"),
        Avg_Waiting=("waiting_time_in_mins", "mean"),
        Avg_Travel=("travel_time_in_mins", "mean"),
        Avg_Total=("total_time_in_mins", "mean"),
        Avg_Distance=("distance_in_km", "mean"),
        Vans=("plate_number", "nunique")
    )
    .reset_index()
    .sort_values("Orders", ascending=False)
)

st.dataframe(summary, use_container_width=True, hide_index=True)
