from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shapely.geometry import shape
import numpy as np
import joblib
from PIL import Image
import io
from model_loader import AnomalyDetector
from typing import Dict
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
#model = joblib.load("model/yield_model.pkl")
anomaly_detector = AnomalyDetector()

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

@app.post("/predict/")
async def predict_crop_yield(data: GeoJSONRequest):
        polygon = shape(data.geometry)
        # Burada polygon ile işlem yapabilirsin, şimdilik sabit değer dönüyoruz
        ndvi_mean = 0.72
        tahmini_rekolte = 3500

        return {
        "ndvi": ndvi_mean,
        "tahmini_rekolte": tahmini_rekolte
    }



# tif dosyasını indirme.