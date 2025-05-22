from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shapely.geometry import shape
import numpy as np
import joblib
from PIL import Image
import io
from model_loader import anomaly_detector
import os
import uvicorn
import torch
from torchvision.models.segmentation import deeplabv3_resnet50

app = FastAPI()

# CORS: React frontend'e izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelleri yükle
# Model dosyasının var olup olmadığını kontrol et
yield_model_path = "model/yield_model.pkl"
try:
    model = joblib.load(yield_model_path) if os.path.exists(yield_model_path) else None
except Exception as e:
    print(f"Yield model yüklenemedi: {e}")
    model = None

# Anomali tespit modelini yükle    
# model_path = "server/app/models/deeplabv3_rgbnir_finalv4_best.pth"
# model.load_state_dict(torch.load(model_path))

model = deeplabv3_resnet50(weights=None, aux_loss=True)

class GeoJSONRequest(BaseModel):
    geometry: dict

@app.post("/predict/")
async def predict_crop_yield(data: GeoJSONRequest):
    polygon = shape(data.geometry)  # GeoJSON → shapely
    ndvi_mean = 0.72  # (test için sabit — sonra NDVI raster'dan hesaplanacak)

    if model is not None:
        predicted_yield = model.predict([[ndvi_mean]])[0]
        return {
            "ndvi": ndvi_mean,
            "tahmini_rekolte": round(predicted_yield, 2)
        }
    else:
        return {
            "ndvi": ndvi_mean,
            "tahmini_rekolte": 0,
            "error": "Yield model yüklü değil"
        }

@app.post("/detect-anomaly/")
async def detect_anomaly(file: UploadFile = File(...)):
    # Gelen dosyayı oku ve PIL Image'e çevir
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # Sadece finalv4 ile anomali tespiti yap
    result = anomaly_detector.detect_anomaly(image)
    
    return {
        "filename": file.filename,
        "anomaly_score": result.get("anomaly_score", 0),
        "is_anomaly": result.get("is_anomaly", False),
        "status": result.get("status", "unknown"),
        "primary_class": result.get("primary_class", {"name": "unknown", "probability": 0}),
        "detected_anomalies": result.get("detected_anomalies", []),
        "confidence_scores": result.get("confidence_scores", {}),
        "raw_scores": result.get("raw_scores", {})
    }

@app.get("/")
async def root():
    return {"message": "API active, use /detect-anomaly/ endpoint"}

# Bu bölüm ana modül olarak çalıştırıldığında API'yı başlatır
if __name__ == "__main__":
    print("Anomali tespiti API'si başlatılıyor...")
    print("API URL: http://localhost:8000")
    print("Swagger docs: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
