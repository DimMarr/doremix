from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class Track(Base):
    __tablename__ = "track"
    
    idTrack = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    youtubeLink = Column(String(2048), nullable=True)
    listeningCount = Column(Integer, default=0)
    durationSeconds = Column(Integer, nullable=True)
    createdAt = Column(TIMESTAMP, server_default=func.now())