"""Azure config for Lagos Traffic Congestion Analytics."""
import os

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
AZURE_STREAM_ANALYTICS_JOB = os.getenv("AZURE_SA_JOB", "lagos-traffic-stream")
AZURE_EVENTHUB_GPS = os.getenv("AZURE_EVENTHUB_GPS", "")
AZURE_MAPS_KEY = os.getenv("AZURE_MAPS_KEY", "")
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "")


def get_stream_analytics_query() -> str:
    return """
    SELECT
        corridor, zone,
        AVG(speed_kmh) AS avg_speed,
        1 - AVG(speed_kmh) / 60.0 AS congestion_index,
        COUNT(*) AS probe_count,
        System.Timestamp AS window_end
    INTO [output-blob]
    FROM [gps-eventhub] TIMESTAMP BY timestamp
    GROUP BY corridor, zone, TumblingWindow(minute, 5)
    """


def get_azure_maps_route(origin_lat: float, origin_lon: float,
                          dest_lat: float, dest_lon: float) -> dict:
    return {
        "origin": [origin_lat, origin_lon],
        "destination": [dest_lat, dest_lon],
        "note": f"Call Azure Maps Route API with key {AZURE_MAPS_KEY[:6]}...",
    }
