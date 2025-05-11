from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shapely.geometry import shape
import numpy as np
import joblib
from pydantic import BaseModel
from typing import Dict
from utils import get_bbox_from_geojson, ndvi_file_exists


app = FastAPI()

class PredictRequest(BaseModel):
    polygon: Dict

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
    polygon = shape(data.geometry)
    bbox = get_bbox_from_geojson(data.geometry)
    exists, raster_path = ndvi_file_exists(bbox)

    if exists:
        ndvi_mean = 0.72
        predicted_yield = model.predict([[ndvi_mean]])[0]

        return {
            "status": "Raster bulundu",
            "ndvi": ndvi_mean,
            "tahmini_rekolte": round(predicted_yield, 2),
            "raster_path": raster_path
        }
    else:
        return {
            "status": "Raster bulunamadı",
            "bbox": bbox
        }

# raster
