"""
Lagos Traffic Congestion PySpark Pipeline — Azure Databricks
Processes GPS probes to compute congestion indices and predict travel times.
"""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml import Pipeline
import os


def get_spark() -> SparkSession:
    return (SparkSession.builder.appName("LagosTrafficPipeline")
            .config("fs.azure.account.key.<STORAGE_ACCOUNT>.blob.core.windows.net",
                    os.getenv("AZURE_STORAGE_KEY", ""))
            .getOrCreate())


def load_data(spark, path="data/"):
    probes = spark.read.csv(f"{path}gps_probes.csv", header=True, inferSchema=True)
    incidents = spark.read.csv(f"{path}incidents.csv", header=True, inferSchema=True)
    corridors = spark.read.csv(f"{path}corridor_stats.csv", header=True, inferSchema=True)
    return probes, incidents, corridors


def compute_corridor_congestion(probes_df):
    """Per-corridor, per-hour average speed and congestion index."""
    return (
        probes_df
        .groupBy("corridor", "zone", "hour", "is_peak_hour", "day_of_week")
        .agg(
            F.avg("speed_kmh").alias("avg_speed_kmh"),
            F.avg("congestion_index").alias("avg_congestion_index"),
            F.count("*").alias("probe_count"),
            F.min("speed_kmh").alias("min_speed_kmh"),
            F.stddev("speed_kmh").alias("speed_stddev"),
        )
        .withColumn(
            "level_of_service",
            F.when(F.col("avg_speed_kmh") >= 40, "A - Free Flow")
             .when(F.col("avg_speed_kmh") >= 30, "B - Reasonably Free")
             .when(F.col("avg_speed_kmh") >= 20, "C - Stable")
             .when(F.col("avg_speed_kmh") >= 10, "D - Approaching Unstable")
             .otherwise("E/F - Congested")
        )
    )


def identify_hotspots(probes_df, threshold: float = 0.7):
    """Return corridors with avg congestion_index above threshold."""
    return (
        probes_df
        .groupBy("corridor", "lat", "lon")
        .agg(F.avg("congestion_index").alias("avg_congestion"))
        .filter(F.col("avg_congestion") >= threshold)
        .orderBy(F.col("avg_congestion").desc())
    )


def predict_travel_time(probes_df):
    """Predict congestion index from time-of-day and corridor features."""
    zone_idx = StringIndexer(inputCol="zone", outputCol="zone_idx", handleInvalid="keep")
    corridor_idx = StringIndexer(inputCol="corridor", outputCol="corridor_idx", handleInvalid="keep")
    assembler = VectorAssembler(
        inputCols=["hour", "zone_idx", "corridor_idx"],
        outputCol="features"
    )
    rf = RandomForestRegressor(featuresCol="features", labelCol="congestion_index",
                               numTrees=50, maxDepth=6)
    pipeline = Pipeline(stages=[zone_idx, corridor_idx, assembler, rf])
    train, test = probes_df.randomSplit([0.8, 0.2], seed=42)
    model = pipeline.fit(train)
    return model, model.transform(test)


if __name__ == "__main__":
    spark = get_spark()
    probes_df, incidents_df, corridors_df = load_data(spark)
    congestion_df = compute_corridor_congestion(probes_df)
    congestion_df.show(10)
    hotspots = identify_hotspots(probes_df)
    hotspots.show(10)
    model, preds = predict_travel_time(probes_df)
    preds.select("corridor", "hour", "congestion_index", "prediction").show(10)
    spark.stop()
