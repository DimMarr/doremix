from sqlalchemy import Column, Integer, String
from database import Base

class Genre(Base):
    __tablename__ = "genre"
    
    idGenre = Column(Integer, primary_key=True, index=True)
    label = Column(String(255), nullable=False)