from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Membuat File Database (SQLite)
# Nanti akan muncul file 'youtube_factory.db' otomatis
SQLALCHEMY_DATABASE_URL = "sqlite:///./youtube_factory.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 2. Definisi Tabel 'channels'
# Ini seperti mendesain kolom Excel: Ada ID, Nama Channel, Status, dll
class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String, index=True)
    channel_id = Column(String, unique=True, index=True) # ID unik dari Youtube
    status = Column(String, default="OFFLINE") # ONLINE / OFFLINE
    is_active = Column(Boolean, default=True)