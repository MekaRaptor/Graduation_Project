# init_db.py
from database import engine
from models import Base

print("⏳ Veritabanı tabloları oluşturuluyor...")
Base.metadata.create_all(bind=engine)
print("✅ Tablolar başarıyla oluşturuldu.")
