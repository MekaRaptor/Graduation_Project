from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shapely.geometry import shape
import numpy as np
import joblib
from PIL import Image
import io
from model_loader import AnomalyDetector

app = FastAPI()

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
