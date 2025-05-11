# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123@localhost:5432/cropyield")

# SQLAlchemy engine ve session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM model taban sınıfı
Base = declarative_base()
