# utils/location_utils.py
import requests
from shapely.geometry import shape

def get_district_from_geometry(geometry_geojson):
    polygon = shape(geometry_geojson)
    lon, lat = polygon.centroid.xy
    lat, lon = lat[0], lon[0]

    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json"
    }

    headers = {
        "User-Agent": "crop-yield-app"
    }

    res = requests.get(url, params=params, headers=headers)
    if res.status_code == 200:
        address = res.json().get("address", {})
        return address.get("county", "Bilinmiyor")
    else:
        return "Bilinmiyor"
