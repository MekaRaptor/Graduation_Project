import os
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shapely.geometry import shape, box
import numpy as np
import joblib
from PIL import Image
import io
import rasterio
#from model_loader import AnomalyDetector
from typing import Dict
from database import SessionLocal
from utils.get_ndvi import get_ndvi_series
from utils.get_rain import get_rain_sum_from_open_meteo
from utils.get_loc import get_district_from_geometry
import pandas as pd


app = FastAPI()

class GeoJSONRequest(BaseModel):
    geometry: Dict

# CORS: React frontend'e izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelleri yükle
model = joblib.load("./model/rf_model.pkl")
#anomaly_detector = AnomalyDetector()



# Anomali tespiti için sınıf
@app.post("/detect-anomaly/")
async def detect_anomaly(file: UploadFile = File(...)):
    # Gelen dosyayı oku ve PIL Image'e çevir
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # Anomali tespiti yap
    result = anomaly_detector.detect_anomaly(image)
    
    return {
        "filename": file.filename,
        "anomaly_score": result["anomaly_score"],
        "is_anomaly": result["is_anomaly"],
        "status": result["status"]
    }




# Rekolte tahmini için sınıf

START_DATE = "2023-10-10"
END_DATE = "2024-05-15"



@app.post("/get_polygon/")
async def send_data(data: GeoJSONRequest):
    # 1. NDVI zaman serisini al (max 15 değer)
    ndvi_input = get_ndvi_series(
        geometry_geojson=data.geometry,
        start_date=START_DATE,
        end_date=END_DATE
    )

    # 2. Eksik NDVI'ları 0.0 ile doldur (NDVI_1–15)
    for i in range(1, 16):
        key = f"NDVI_{i}"
        if key not in ndvi_input:
            ndvi_input[key] = 0.0

    # 3. NDVI ortalamasını hesapla ve ekle
    ndvi_values = [ndvi_input[f"NDVI_{i}"] for i in range(1, 16)]
    ndvi_mean = sum(ndvi_values) / len(ndvi_values) if ndvi_values else 0.0
    ndvi_input["NDVI_mean"] = round(ndvi_mean, 4)

    # 4. Yağış verisini al
    rain_sum = get_rain_sum_from_open_meteo(
        geometry_geojson=data.geometry,
        start_date=START_DATE,
        end_date=END_DATE
    )

    # 5. İlçeyi bul
    ilce = get_district_from_geometry(data.geometry)

    # 6. Model girdisi oluştur
    input_features = ndvi_input.copy()
    input_features["rain_sum"] = rain_sum

    df_input = pd.DataFrame([input_features])

    # 7. Tahmin
    prediction = model.predict(df_input)[0]

    return {
        "ilce": ilce,
        "rain_sum": rain_sum,
        "ndvi_input": ndvi_input,
        "tahmini_rekolte": round(prediction, 2)
    }