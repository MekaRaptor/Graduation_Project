from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from shapely.geometry import shape
from PIL import Image
import io
import numpy as np
import traceback
from ..models.anomaly_detector import AnomalyDetector

router = APIRouter()
anomaly_detector = AnomalyDetector()

class GeoJSONRequest(BaseModel):
    geometry: dict

@router.post("/predict/")
async def predict_crop_yield(data: GeoJSONRequest):
    polygon = shape(data.geometry)
    ndvi_mean = 0.72  # (test için sabit — sonra NDVI raster'dan hesaplanacak)

    # TODO: Implement yield prediction model
    predicted_yield = 0  # model.predict([[ndvi_mean]])[0]

    return {
        "ndvi": ndvi_mean,
        "tahmini_rekolte": round(predicted_yield, 2)
    }

@router.post("/detect-anomaly/")
async def detect_anomaly(file: UploadFile = File(...)):
    try:
        # Gelen dosyayı oku ve PIL Image'e çevir
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Görüntü formatını kontrol et
        print(f"Image format: {image.format}, size: {image.size}, mode: {image.mode}")
        
        # Anomali tespiti yap
        result = anomaly_detector.detect_anomaly(image)
        return result
    except Exception as e:
        # Hata detaylarını yazdır
        error_details = traceback.format_exc()
        print(f"Error details: {error_details}")
        
        # Hata mesajını istemciye döndür
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "traceback": error_details
            }
        ) 