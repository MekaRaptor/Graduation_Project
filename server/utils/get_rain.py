# utils/meteo_utils.py
import requests
from shapely.geometry import shape

def get_centroid_lat_lon(geometry_geojson):
    polygon = shape(geometry_geojson)
    lon, lat = polygon.centroid.xy
    return lat[0], lon[0]

def get_rain_sum_from_open_meteo(geometry_geojson, start_date, end_date):
    lat, lon = get_centroid_lat_lon(geometry_geojson)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "precipitation_sum",
        "timezone": "Europe/Istanbul"
    }

    res = requests.get(url, params=params)
    if res.status_code != 200:
        raise Exception("Open-Meteo API Hatası: " + res.text)

    data = res.json()
    rain_list = data["daily"]["precipitation_sum"]
    return sum(rain_list)
