import ee
from datetime import datetime, timedelta
from shapely.geometry import shape

import ee
ee.Authenticate()
ee.Initialize(project='rekolte') 



def get_ndvi_series(geometry_geojson: dict, start_date: str, end_date: str) -> dict:
    # GeoJSON'u ee.Geometry'ye çevir
    polygon = shape(geometry_geojson)
    ee_geometry = ee.Geometry.Polygon(list(polygon.exterior.coords))

    # Tarihleri ayarla
    start = datetime.strptime(start_date[:10], "%Y-%m-%d")
    end = datetime.strptime(end_date[:10], "%Y-%m-%d")

    result = {}
    index = 1

    while start < end and index <= 15:
        interval_end = start + timedelta(days=15)

        # Sentinel-2 verilerini filtrele ve NDVI hesapla
        collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterDate(start.strftime("%Y-%m-%d"), interval_end.strftime("%Y-%m-%d")) \
            .filterBounds(ee_geometry) \
            .map(lambda img: img.normalizedDifference(['B8', 'B4']).rename('NDVI'))

        # Ortanca NDVI'yı hesapla
        mean_ndvi = collection.select("NDVI").median().reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=ee_geometry,
            scale=10,
            maxPixels=1e9
        ).get("NDVI")

        value = mean_ndvi.getInfo() if mean_ndvi else None
        result[f"NDVI_{index}"] = round(value, 4) if value is not None else None

        # Sonraki döneme geç
        start = interval_end
        index += 1

    return result
