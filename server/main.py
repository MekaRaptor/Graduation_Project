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



@app.post("/predict/")
async def predict_crop_yield(data: GeoJSONRequest):