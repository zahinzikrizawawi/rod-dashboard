import streamlit as st
import plotly.express as px

from utils import apply_style, load_data, PERIOD_OPTIONS

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="OD Strategic Flow Analysis",
    page_icon="🔀",
    layout="wide"
)
apply_style()

df = load_data()

# ============================================================
# HEADER
# ============================================================
st.title("🔀 OD Strategic Flow Analysis (Fleet Staging View)")
st.markdown("Focus: Pickup hotspots → dominant movement flows → staging recommendation.")
st.divider()

# ============================================================
# SIDEBAR FILTERS
# ============================================================
with st.sidebar:
    st.header("🔎 Filters")

    zone = st.selectbox("Zone", ["All"] + sorted(df["zone_name"].dropna().unique()))
    period = st.selectbox("Time Period", PERIOD_OPTIONS)
    top_n = st.slider("Top Pickup Stops", min_value=3, max_value=10, value=5)

# ============================================================
# FILTER DATA
# ============================================================
dff = df.copy()

if zone != "All":
    dff = dff[dff["zone_name"] == zone]

if period != "All":
    dff = dff[dff["period"] == period]

if dff.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ============================================================
# TOP PICKUP STOPS
# ============================================================
st.subheader("1️⃣ Top Pickup Stops")

pickup = (
    dff.groupby(
        ["pickup_stop_name", "zone_name", "period",
         "pickup_latitude", "pickup_longitude"]
    )
    .size()
    .reset_index(name="demand")
    .sort_values("demand", ascending=False)
)

top_stops = pickup.head(top_n)

st.dataframe(top_stops, use_container_width=True)

if top_stops.empty:
    st.warning("No pickup stops found for the selected filters.")
    st.stop()

selected_stop = st.selectbox(
    "Select Pickup Stop",
    top_stops["pickup_stop_name"].unique()
)

stop_df = dff[dff["pickup_stop_name"] == selected_stop]

# ============================================================
# OD ANALYSIS (TOP 5 ONLY)
# ============================================================
st.subheader("2️⃣ Dominant OD Pairs")

od = (
    stop_df.groupby("dropoff_stop_name")
    .size()
    .reset_index(name="trips")
    .sort_values("trips", ascending=False)
    .head(5)
)

if od.empty:
    st.warning("No dropoff destinations found for this pickup stop.")
    st.stop()

od["percentage"] = (od["trips"] / od["trips"].sum() * 100).round(1)

st.dataframe(od, use_container_width=True)

# ============================================================
# FLOW MAP
# ============================================================
st.subheader("3️⃣ OD Flow Map")

origin = stop_df[[
    "pickup_stop_name",
    "pickup_latitude",
    "pickup_longitude"
]].dropna().head(1)

if origin.empty:
    st.warning("Not enough coordinate data for a flow map.")
else:
    origin_lat = origin["pickup_latitude"].values[0]
    origin_lon = origin["pickup_longitude"].values[0]

    # Attach coordinates for each destination
    dest = od.merge(
        df[[
            "dropoff_stop_name",
            "dropoff_latitude",
            "dropoff_longitude"
        ]].drop_duplicates(),
        on="dropoff_stop_name",
        how="left"
    ).dropna()

    if dest.empty:
        st.warning("No destination coordinates available for the flow map.")
    else:
        fig = px.scatter_mapbox(
            dest,
            lat="dropoff_latitude",
            lon="dropoff_longitude",
            size="trips",
            color="trips",
            color_continuous_scale="Reds",
            hover_name="dropoff_stop_name",
            zoom=11,
            height=650
        )

        # Origin marker
        fig.add_scattermapbox(
            lat=[origin_lat],
            lon=[origin_lon],
            mode="markers",
            marker=dict(size=18, color="blue"),
            name="Pickup Origin"
        )

        # Flow lines from origin to each destination
        for _, row in dest.iterrows():
            fig.add_scattermapbox(
                lat=[origin_lat, row["dropoff_latitude"]],
                lon=[origin_lon, row["dropoff_longitude"]],
                mode="lines",
                line=dict(width=2),
                showlegend=False
            )

        fig.update_layout(
            mapbox_style="open-street-map",
            margin=dict(l=0, r=0, t=0, b=0)
        )

        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

# ============================================================
# INSIGHT BOX
# ============================================================
st.subheader("📊 Insight Summary")

top_dest = od.iloc[0]["dropoff_stop_name"]
top_pct = od.iloc[0]["percentage"]

st.info(
    f"""
    **Key Insight**

    - Selected stop: **{selected_stop}**
    - Primary destination: **{top_dest}**
    - Flow concentration: **{top_pct}%**

    **Operational meaning:**
    - High demand concentration indicates strong staging potential.
    - Vans should be positioned near this pickup stop during peak period.
    """
)
