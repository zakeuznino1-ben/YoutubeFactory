from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Setup Database SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./youtube_factory.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String, index=True)
    channel_id = Column(String, unique=True, index=True)
    stream_key = Column(String, nullable=True) # Persiapan masa depan
    video_source = Column(String, default="test.mp4") # <--- KOLOM BARU KITA
    status = Column(String, default="OFFLINE")