"""
Lagos Traffic Congestion Analytics — Streamlit Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from data.generate_data import generate_gps_probes, generate_incidents, generate_corridor_stats
from gis.spatial_analysis import build_congestion_map

st.set_page_config(page_title="Lagos Traffic Analytics", page_icon="🚦", layout="wide")
st.markdown("""
<style>
.kpi{background:#212121;color:white;padding:14px;border-radius:8px;text-align:center;border-left:4px solid #f44336;}
.kpi-val{font-size:1.9rem;font-weight:700;}
.kpi-lbl{font-size:.8rem;opacity:.8;}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    return generate_gps_probes(5000), generate_incidents(300), generate_corridor_stats()


def main():
    probes_df, incidents_df, corridors_df = load_data()
    probes_df["timestamp"] = pd.to_datetime(probes_df["timestamp"])

    with st.sidebar:
        st.title("🚦 Lagos Traffic")
        st.caption("Congestion Analytics")
        st.divider()
        zone_filter = st.multiselect("Zone", ["Island", "Mainland"], default=["Island", "Mainland"])
        hour_range = st.slider("Hour Range", 0, 23, (6, 22))
        day_filter = st.multiselect(
            "Day of Week",
            ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
            default=["Monday","Tuesday","Wednesday","Thursday","Friday"]
        )
        st.divider()
        st.markdown("**Azure Services**")
        st.info("Azure Stream Analytics")
        st.success("Azure Databricks")
        st.warning("Azure Maps Routing")

    probe_filtered = probes_df[
        probes_df["zone"].isin(zone_filter) &
        probes_df["hour"].between(hour_range[0], hour_range[1]) &
        probes_df["day_of_week"].isin(day_filter)
    ]
    inc_filtered = incidents_df[incidents_df["zone"].isin(zone_filter)]

    st.title("🚦 Lagos Traffic Congestion Analytics")
    st.caption("Real-time congestion monitoring · Hotspot detection · Powered by GIS + PySpark + Azure Stream Analytics")
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    avg_speed = probe_filtered["speed_kmh"].mean()
    avg_cong = probe_filtered["congestion_index"].mean()
    critical_corridors = len(corridors_df[corridors_df["congestion_index"] > 0.7])
    total_inc = len(inc_filtered)
    for col, val, lbl in zip(
        [c1, c2, c3, c4],
        [f"{avg_speed:.1f} km/h", f"{avg_cong:.2f}", critical_corridors, total_inc],
        ["Avg Speed", "Congestion Index", "Critical Corridors", "Incidents (filtered)"]
    ):
        col.markdown(f'<div class="kpi"><div class="kpi-val">{val}</div>'
                     f'<div class="kpi-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.divider()
    map_col, chart_col = st.columns([3, 2])

    with map_col:
        st.subheader("🗺 Live Congestion Heatmap")
        m = build_congestion_map(probe_filtered, inc_filtered, corridors_df)
        st_folium(m, width=700, height=460)

    with chart_col:
        st.subheader("📊 Speed by Corridor")
        corr_speed = (probe_filtered.groupby("corridor")["speed_kmh"]
                      .mean().sort_values().reset_index())
        fig = px.bar(corr_speed, x="speed_kmh", y="corridor", orientation="h",
                     color="speed_kmh", color_continuous_scale="RdYlGn",
                     labels={"speed_kmh": "Avg Speed (km/h)", "corridor": ""},
                     height=460)
        fig.update_layout(coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=0, r=10, t=5, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    col_hourly, col_inc = st.columns(2)

    with col_hourly:
        st.subheader("⏰ Congestion by Hour")
        hourly = (probe_filtered.groupby("hour")["congestion_index"]
                  .mean().reset_index())
        fig_h = px.area(hourly, x="hour", y="congestion_index",
                        color_discrete_sequence=["#f44336"],
                        labels={"hour": "Hour of Day", "congestion_index": "Congestion Index"})
        fig_h.add_vline(x=8, line_dash="dash", line_color="orange", annotation_text="AM Peak")
        fig_h.add_vline(x=18, line_dash="dash", line_color="orange", annotation_text="PM Peak")
        fig_h.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=0, r=0, t=5, b=0))
        st.plotly_chart(fig_h, use_container_width=True)

    with col_inc:
        st.subheader("⚠ Incident Types")
        inc_types = inc_filtered["type"].value_counts().reset_index()
        inc_types.columns = ["type", "count"]
        fig_inc = px.pie(inc_types, names="type", values="count", hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set1)
        fig_inc.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_inc, use_container_width=True)

    st.divider()
    st.subheader("📋 Worst Congestion Corridors")
    worst = corridors_df.sort_values("congestion_index", ascending=False).head(15)
    st.dataframe(
        worst[["corridor", "zone", "congestion_index", "avg_peak_speed_kmh",
               "daily_vehicle_count", "congestion_hours_daily"]]
        .style.background_gradient(subset=["congestion_index"], cmap="RdYlGn_r"),
        use_container_width=True, height=320,
    )
    st.caption("Data: Synthetic — replace with HERE Maps API, LASTMA feeds, OpenStreetMap. "
               "Pipeline: Azure Databricks + Azure Stream Analytics.")


if __name__ == "__main__":
    main()
