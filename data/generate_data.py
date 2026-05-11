import pandas as pd
import numpy as np
import os

LAGOS_CORRIDORS = [
    ("Carter Bridge", 6.4541, 3.3947, "Island"),
    ("Eko Bridge", 6.4560, 3.3740, "Island"),
    ("Third Mainland Bridge", 6.4698, 3.3957, "Island"),
    ("Apapa-Oshodi Expressway", 6.4531, 3.3608, "Mainland"),
    ("Lagos-Ibadan Expressway", 6.6000, 3.3600, "Mainland"),
    ("Lekki-Epe Expressway", 6.4300, 3.5800, "Island"),
    ("Ikorodu Road", 6.5300, 3.4200, "Mainland"),
    ("Lagos-Badagry Expressway", 6.4400, 3.2400, "Mainland"),
    ("Agege Motor Road", 6.6200, 3.3100, "Mainland"),
    ("Funsho Williams Ave", 6.4630, 3.3530, "Island"),
    ("Allen Avenue, Ikeja", 6.5956, 3.3469, "Mainland"),
    ("Broad Street", 6.4530, 3.3950, "Island"),
    ("Victoria Island Spine", 6.4282, 3.4219, "Island"),
    ("Oshodi-Apapa Road", 6.5550, 3.3550, "Mainland"),
    ("Mile 2-Orile Road", 6.4750, 3.3450, "Mainland"),
    ("Ojota-Ketu Road", 6.5800, 3.4000, "Mainland"),
    ("Badore Road, Ajah", 6.4650, 3.5650, "Island"),
    ("Ojo-Amuwo Road", 6.5100, 3.3100, "Mainland"),
    ("Idumota-Lagos Island", 6.4560, 3.3940, "Island"),
    ("Surulere-Ring Road", 6.4950, 3.3590, "Mainland"),
]

INCIDENT_TYPES = ["Accident", "Breakdown", "Flooding", "Road Work", "VIP Movement",
                  "Traffic Signal Fault", "Protest/March", "Pedestrian Overflow"]


def generate_gps_probes(n: int = 10000) -> pd.DataFrame:
    np.random.seed(42)
    records = []
    base_date = pd.Timestamp("2024-01-01")
    for i in range(n):
        corridor = LAGOS_CORRIDORS[np.random.randint(len(LAGOS_CORRIDORS))]
        name, clat, clon, zone = corridor
        hour = int(np.random.choice(range(24), p=[
            0.01, 0.01, 0.01, 0.01, 0.02, 0.04, 0.07, 0.10,
            0.08, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05, 0.06,
            0.07, 0.09, 0.07, 0.05, 0.04, 0.03, 0.02, 0.01
        ]))
        is_peak = hour in range(7, 10) or hour in range(16, 20)
        base_speed = 8 if is_peak else 35
        records.append({
            "probe_id": f"PROBE-{i+1:06d}",
            "timestamp": base_date + pd.Timedelta(days=int(np.random.randint(90)),
                                                    hours=hour,
                                                    minutes=int(np.random.randint(60))),
            "corridor": name,
            "zone": zone,
            "lat": clat + np.random.uniform(-0.02, 0.02),
            "lon": clon + np.random.uniform(-0.02, 0.02),
            "speed_kmh": max(1, base_speed + np.random.normal(0, 5)),
            "heading_deg": float(np.random.randint(0, 360)),
            "hour": hour,
            "is_peak_hour": is_peak,
            "day_of_week": (base_date + pd.Timedelta(days=int(np.random.randint(90)))).day_name(),
        })
    df = pd.DataFrame(records)
    df["speed_kmh"] = df["speed_kmh"].round(1)
    df["congestion_index"] = (1 - df["speed_kmh"] / 60).clip(0, 1).round(3)
    return df


def generate_incidents(n: int = 300) -> pd.DataFrame:
    np.random.seed(42)
    records = []
    base_date = pd.Timestamp("2024-01-01")
    for i in range(n):
        corridor = LAGOS_CORRIDORS[np.random.randint(len(LAGOS_CORRIDORS))]
        name, clat, clon, zone = corridor
        records.append({
            "incident_id": f"INC-{i+1:04d}",
            "timestamp": base_date + pd.Timedelta(days=int(np.random.randint(90)),
                                                    hours=int(np.random.randint(24))),
            "corridor": name,
            "zone": zone,
            "lat": clat + np.random.uniform(-0.015, 0.015),
            "lon": clon + np.random.uniform(-0.015, 0.015),
            "type": np.random.choice(INCIDENT_TYPES),
            "duration_min": int(np.random.exponential(45)),
            "lanes_blocked": np.random.randint(1, 4),
            "severity": np.random.choice(["Low", "Medium", "High"], p=[0.4, 0.4, 0.2]),
        })
    return pd.DataFrame(records)


def generate_corridor_stats() -> pd.DataFrame:
    np.random.seed(42)
    records = []
    for name, clat, clon, zone in LAGOS_CORRIDORS:
        records.append({
            "corridor": name, "zone": zone, "lat": clat, "lon": clon,
            "avg_peak_speed_kmh": round(np.random.uniform(5, 25), 1),
            "avg_offpeak_speed_kmh": round(np.random.uniform(25, 55), 1),
            "daily_vehicle_count": int(np.random.uniform(30000, 250000)),
            "congestion_hours_daily": round(np.random.uniform(2, 8), 1),
            "accident_rate_monthly": round(np.random.uniform(0.5, 12), 1),
            "congestion_index": round(np.random.uniform(0.3, 0.95), 3),
        })
    return pd.DataFrame(records)


def save_all(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    generate_gps_probes().to_csv(f"{output_dir}/gps_probes.csv", index=False)
    generate_incidents().to_csv(f"{output_dir}/incidents.csv", index=False)
    generate_corridor_stats().to_csv(f"{output_dir}/corridor_stats.csv", index=False)
    print("Traffic data generated.")


if __name__ == "__main__":
    save_all()
