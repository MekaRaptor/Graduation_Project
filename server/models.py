# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=True)
    date = Column(String, nullable=True)  # YYYY-MM-DD
    bbox_minx = Column(Float)
    bbox_miny = Column(Float)
    bbox_maxx = Column(Float)
    bbox_maxy = Column(Float)
    ndvi_mean = Column(Float)
    yield_kg_ha = Column(Float)
    anomaly = Column(String, default="unknown")  # "yes", "no", "unknown"
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
