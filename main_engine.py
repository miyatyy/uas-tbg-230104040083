import os
import random
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, window, hour
from sklearn.linear_model import LinearRegression
import pandas as pd
import pickle

# ==========================================
# 0. INITIALIZATION & ABSOLUTE PATH CONFIG
# ==========================================
BASE_PATH = "/home/nurmiyaty/uas-bigdata/output"

os.makedirs(f"{BASE_PATH}/energy_total", exist_ok=True)
os.makedirs(f"{BASE_PATH}/energy_time", exist_ok=True)
os.makedirs(f"{BASE_PATH}/ml_energy", exist_ok=True)
os.makedirs(f"{BASE_PATH}/model_ai", exist_ok=True)

# Inisialisasi Spark Session
spark = SparkSession.builder \
    .appName("SmartEnergyAnalytics") \
    .config("spark.sql.session.timeZone", "UTC") \
    .getOrCreate()

print("--> Spark Session Berhasil Dijalankan.")

# ==========================================
# 1. GENERATE DUMMY DATA (150 Menit)
# ==========================================
print("--> Generating data sensor IoT...")
sectors = ["Industrial_A", "Industrial_B", "Residential_C"]
start_time = datetime.now() - timedelta(minutes=150)
raw_data = []

# Generate data per menit untuk setiap sektor selama 150 menit
for minute in range(150):
    current_timestamp = start_time + timedelta(minutes=minute)
    for sector in sectors:
        power_usage = round(random.uniform(100.0, 1000.0), 2)
        raw_data.append((current_timestamp, sector, power_usage))

# Buat DataFrame Spark
schema = ["timestamp", "sector", "power_usage"]
df_energy = spark.createDataFrame(raw_data, schema=schema)

# ==========================================
# 2. SPARK PROCESSING & TRANSFORMATIONS
# ==========================================
print("--> Melakukan Spark Processing & Agregasi...")

# Agregasi 1: Total konsumsi energi per sektor
df_total_sector = df_energy.groupBy("sector").agg(_sum("power_usage").alias("total_power"))

# Agregasi 2: Agregasi konsumsi tiap 10 menit
df_time_10min = df_energy.groupBy(
    window(col("timestamp"), "10 minutes"), 
    col("sector")
).agg(_sum("power_usage").alias("total_power_10m")) \
 .withColumn("window_start", col("window.start")) \
 .drop("window")

# Agregasi 3: Dataset AI berdasarkan hour (jam)
df_ml_source = df_energy.withColumn("hour", hour(col("timestamp"))) \
    .groupBy("hour") \
    .agg(_sum("power_usage").alias("total_power_hourly"))

# ==========================================
# 3. SAVE TO PARQUET (Overwrite mode)
# ==========================================
print("--> Menyimpan hasil agregasi ke format Parquet...")
df_total_sector.write.mode("overwrite").parquet(f"{BASE_PATH}/energy_total")
df_time_10min.write.mode("overwrite").parquet(f"{BASE_PATH}/energy_time")
df_ml_source.write.mode("overwrite").parquet(f"{BASE_PATH}/ml_energy")
print("--> File Parquet berhasil dibuat di folder output.")

# ==========================================
# 4. AI PREDICTION - LINEAR REGRESSION (Scikit-Learn)
# ==========================================
print("--> Melatih Model AI Linear Regression...")
pandas_ml_df = df_ml_source.toPandas()

X = pandas_ml_df[['hour']]
y = pandas_ml_df['total_power_hourly']

# Inisialisasi dan training model
model = LinearRegression()
model.fit(X, y)

# Simpan model AI di folder model_ai agar tidak mengganggu folder Parquet
model_path = f"{BASE_PATH}/model_ai/linear_model.pkl"
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print(f"--> Model AI Berhasil dilatih dan disimpan di: {model_path}")
spark.stop()