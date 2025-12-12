from sqlalchemy import Column, Integer, String
from database import Base

class Artist(Base):
    __tablename__ = "artist"
    
    idArtist = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)