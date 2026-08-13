import streamlit as st
import plotly.express as px

from utils import apply_style, load_data, PERIOD_OPTIONS

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Spatial Demand Analysis",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_style()

df = load_data()

# ============================================================
# HEADER
# ============================================================
st.title("📍 Spatial Demand Analysis")
st.markdown("Interactive map of pickup and dropoff demand by zone and stop.")
st.divider()

# ============================================================
# SIDEBAR CONTROLS
# ============================================================
with st.sidebar:
    st.header("🔎 Filters")

    view = st.radio("Demand Type", ["Pickup Demand", "Dropoff Demand"])

    selected_zone = st.selectbox(
        "Zone",
        ["All"] + sorted(df["zone_name"].dropna().unique().tolist())
    )

    period_filter = st.selectbox("Time Period", PERIOD_OPTIONS)

    st.divider()
    color_scale = st.selectbox(
        "Map Color Scale (highest demand = red)",
        ["YlOrRd", "Reds", "OrRd", "Turbo"],
        index=0
    )

    max_marker_size = st.slider(
        "Max Marker Size",
        min_value=8, max_value=30, value=18,
        help="Lower this if markers overlap in dense zones."
    )

# ============================================================
# PICK COLUMNS
# ============================================================
if view == "Pickup Demand":
    lat, lon, stop = "pickup_latitude", "pickup_longitude", "pickup_stop_name"
else:
    lat, lon, stop = "dropoff_latitude", "dropoff_longitude", "dropoff_stop_name"

# ============================================================
# FILTER DATA
# ============================================================
df_map = df.copy()

if selected_zone != "All":
    df_map = df_map[df_map["zone_name"] == selected_zone]

if period_filter != "All":
    df_map = df_map[df_map["period"] == period_filter]

df_map = df_map.dropna(subset=[lat, lon])

# ============================================================
# GROUP DATA (STOP LEVEL)
# ============================================================
df_grouped = df_map.groupby(
    [stop, "zone_name", "period", lat, lon]
).size().reset_index(name="demand")

# ============================================================
# KPI ROW
# ============================================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Demand", f"{df_grouped['demand'].sum():,}")
col2.metric("Active Stops", f"{df_grouped[stop].nunique():,}")
col3.metric(
    "Top Stop",
    df_grouped.sort_values("demand", ascending=False)[stop].iloc[0]
    if not df_grouped.empty else "—"
)
col4.metric(
    "Avg Demand / Stop",
    f"{df_grouped['demand'].mean():.1f}" if not df_grouped.empty else "0"
)

st.write("")

# ============================================================
# MAP
# ============================================================
st.subheader("📍 Demand Heat Map")

if df_grouped.empty:
    st.warning("No data available for the selected filters.")
else:
    center_lat = df_grouped[lat].mean()
    center_lon = df_grouped[lon].mean()

    fig = px.scatter_mapbox(
        df_grouped,
        lat=lat,
        lon=lon,
        size="demand",
        size_max=max_marker_size,
        color="demand",
        color_continuous_scale=color_scale,
        hover_name=stop,
        hover_data={
            "zone_name": True,
            "period": True,
            "demand": True,
            lat: False,
            lon: False
        },
        center={"lat": center_lat, "lon": center_lon},
        zoom=12,
        height=700
    )

    fig.update_traces(marker=dict(opacity=0.85))
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="Demand")
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displaylogo": False,
            "modeBarButtonsToAdd": ["zoomInMapbox", "zoomOutMapbox", "resetViewMapbox"]
        }
    )

# ============================================================
# TOP STOPS
# ============================================================
st.divider()
st.subheader("🏆 Top Stops in Selected Zone")

top_stops = (
    df_grouped.sort_values("demand", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

st.dataframe(
    top_stops.style.background_gradient(subset=["demand"], cmap="YlOrRd"),
    use_container_width=True
)
