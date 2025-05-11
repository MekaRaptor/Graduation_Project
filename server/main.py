from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shapely.geometry import shape
import numpy as np
import joblib

app = FastAPI()

# CORS: React frontend'e izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modeli yükle
#model = joblib.load("model/yield_model.pkl")

class GeoJSONRequest(BaseModel):
    geometry: dict

@app.post("/predict/")
async def predict_crop_yield(data: GeoJSONRequest):
    polygon = shape(data.geometry)  # GeoJSON → shapely
    ndvi_mean = 0.72  # (test için sabit — sonra NDVI raster'dan hesaplanacak)

    predicted_yield = model.predict([[ndvi_mean]])[0]

    return {
        "ndvi": ndvi_mean,
        "tahmini_rekolte": round(predicted_yield, 2)
    }
