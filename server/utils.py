from shapely.geometry import shape
import os

def get_bbox_from_geojson(geojson_polygon):
    polygon = shape(geojson_polygon)
    return polygon.bounds  # (minx, miny, maxx, maxy)

def ndvi_file_exists(bbox, ndvi_dir="./locations/"):
    filename = f"ndvi_{bbox[0]:.4f}_{bbox[1]:.4f}_{bbox[2]:.4f}_{bbox[3]:.4f}.tif"
    filepath = os.path.join(ndvi_dir, filename)
    return os.path.exists(filepath), filepath
