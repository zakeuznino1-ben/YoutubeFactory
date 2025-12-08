from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Lokasi Database SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./youtube_factory.db"

# Engine Database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Struktur Tabel Channel
class Channel(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String, index=True)
    youtube_id = Column(String)
    video_source = Column(String)
    status = Column(String)

# --- FUNGSI BARU UNTUK V5.0 ---
def init_db():
    """Memastikan tabel database dibuat jika belum ada."""
    Base.metadata.create_all(bind=engine)