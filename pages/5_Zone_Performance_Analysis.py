import streamlit as st
import plotly.express as px

from utils import apply_style, load_data, PERIOD_OPTIONS, DAY_TYPE_OPTIONS

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Zone Performance Analysis",
    page_icon="📈",
    layout="wide"
)
apply_style()

df = load_data()

# ============================================================
# HEADER
# ============================================================
st.title("📈 Zone Performance Analysis")
st.markdown("Evaluate operational performance across zones using demand and service indicators.")
st.divider()

# ============================================================
# SIDEBAR FILTERS
# ============================================================
with st.sidebar:
    st.header("🔎 Filters")

    zone = st.selectbox("Zone", ["All"] + sorted(df["zone_name"].dropna().unique()))
    day_type = st.selectbox("Day Type", DAY_TYPE_OPTIONS)
    period = st.selectbox("Time Period", PERIOD_OPTIONS)

# ============================================================
# FILTER DATA
# ============================================================
data = df.copy()

if zone != "All":
    data = data[data["zone_name"] == zone]
if day_type != "All":
    data = data[data["day_type"] == day_type]
if period != "All":
    data = data[data["period"] == period]

if data.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ============================================================
# KPI
# ============================================================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Completed Trips", f"{len(data):,}")
c2.metric("Average Waiting Time", f"{data['waiting_time_in_mins'].mean():.2f} min")
c3.metric("Average Travel Time", f"{data['travel_time_in_mins'].mean():.2f} min")
c4.metric("Average Total Time", f"{data['total_time_in_mins'].mean():.2f} min")

st.divider()

# ============================================================
# ZONE SUMMARY (BASE FOR CHARTS)
# ============================================================
zone_summary = (
    data.groupby("zone_name")
    .agg(
        Orders=("issue_id", "count"),
        Avg_Waiting=("waiting_time_in_mins", "mean"),
        Avg_Travel=("travel_time_in_mins", "mean"),
        Avg_Total=("total_time_in_mins", "mean"),
        Avg_Distance=("distance_in_km", "mean")
    )
    .reset_index()
)

# ============================================================
# WAITING + TRAVEL TIME
# ============================================================
left, right = st.columns(2)

with left:
    st.subheader("Average Waiting Time by Zone")
    fig = px.bar(
        zone_summary.sort_values("Avg_Waiting"),
        x="Avg_Waiting", y="zone_name", orientation="h",
        color="Avg_Waiting", color_continuous_scale="YlOrRd"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Average Travel Time by Zone")
    fig = px.bar(
        zone_summary.sort_values("Avg_Travel"),
        x="Avg_Travel", y="zone_name", orientation="h",
        color="Avg_Travel", color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# TOTAL TIME + DEMAND VS WAITING
# ============================================================
left, right = st.columns(2)

with left:
    st.subheader("Average Total Journey Time")
    fig = px.bar(
        zone_summary.sort_values("Avg_Total"),
        x="Avg_Total", y="zone_name", orientation="h",
        color="Avg_Total", color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Demand vs Waiting Time")
    fig = px.scatter(
        zone_summary, x="Orders", y="Avg_Waiting",
        size="Orders", hover_name="zone_name",
        labels={"Orders": "Completed Trips", "Avg_Waiting": "Average Waiting Time (min)"}
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# SUMMARY TABLE
# ============================================================
st.subheader("Zone Performance Summary")

summary = zone_summary.copy()
for col in ["Avg_Waiting", "Avg_Travel", "Avg_Total", "Avg_Distance"]:
    summary[col] = summary[col].round(2)

summary = summary.rename(columns={
    "zone_name": "Zone",
    "Orders": "Completed Trips",
    "Avg_Waiting": "Avg Waiting (min)",
    "Avg_Travel": "Avg Travel (min)",
    "Avg_Total": "Avg Total (min)",
    "Avg_Distance": "Avg Distance (km)"
}).sort_values("Completed Trips", ascending=False)

st.dataframe(summary, use_container_width=True, hide_index=True)
