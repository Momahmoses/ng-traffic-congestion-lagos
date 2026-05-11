"""
GIS analysis: Lagos congestion heatmap, incident clustering, corridor mapping.
"""
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, LineString
import folium
from folium.plugins import HeatMap, MarkerCluster
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.generate_data import generate_gps_probes, generate_incidents, generate_corridor_stats

SPEED_COLORS = {"A - Free Flow": "#1b5e20", "B - Reasonably Free": "#388e3c",
                "C - Stable": "#f9a825", "D - Approaching Unstable": "#e65100",
                "E/F - Congested": "#b71c1c"}


def build_probe_gdf(probes_df: pd.DataFrame) -> gpd.GeoDataFrame:
    geom = [Point(r.lon, r.lat) for _, r in probes_df.iterrows()]
    return gpd.GeoDataFrame(probes_df, geometry=geom, crs="EPSG:4326")


def build_congestion_map(probes_df: pd.DataFrame,
                          incidents_df: pd.DataFrame,
                          corridors_df: pd.DataFrame) -> folium.Map:
    m = folium.Map(location=[6.524, 3.379], zoom_start=11, tiles="CartoDB dark_matter")

    # Congestion heatmap
    heat_data = [[r.lat, r.lon, r.congestion_index] for _, r in probes_df.iterrows()]
    HeatMap(heat_data, radius=16, blur=14, min_opacity=0.4,
            gradient={"0.2": "blue", "0.4": "cyan", "0.6": "yellow",
                       "0.8": "orange", "1.0": "red"}).add_to(m)

    # Corridor markers
    for _, row in corridors_df.iterrows():
        color = "#d32f2f" if row["congestion_index"] > 0.7 else \
                "#f57c00" if row["congestion_index"] > 0.5 else "#388e3c"
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=max(6, row["congestion_index"] * 20),
            color=color, fill=True, fill_opacity=0.8,
            popup=(f"<b>{row['corridor']}</b><br>"
                   f"Congestion: {row['congestion_index']:.2f}<br>"
                   f"Peak Speed: {row['avg_peak_speed_kmh']} km/h<br>"
                   f"Daily Vehicles: {row['daily_vehicle_count']:,}"),
            tooltip=row["corridor"],
        ).add_to(m)

    # Incident cluster
    cluster = MarkerCluster(name="Incidents").add_to(m)
    for _, inc in incidents_df.iterrows():
        icon_color = {"High": "red", "Medium": "orange", "Low": "blue"}.get(inc["severity"], "gray")
        folium.Marker(
            location=[inc.lat, inc.lon],
            popup=(f"<b>{inc['type']}</b><br>{inc['corridor']}<br>"
                   f"Duration: {inc['duration_min']} min<br>Severity: {inc['severity']}"),
            icon=folium.Icon(color=icon_color, icon="warning-sign", prefix="glyphicon"),
        ).add_to(cluster)

    folium.LayerControl().add_to(m)
    return m


if __name__ == "__main__":
    probes = generate_gps_probes(2000)
    incidents = generate_incidents()
    corridors = generate_corridor_stats()
    m = build_congestion_map(probes, incidents, corridors)
    os.makedirs("app", exist_ok=True)
    m.save("app/traffic_map.html")
    print("Map saved.")
