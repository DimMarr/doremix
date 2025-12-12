from sqlalchemy import Column, Integer, String, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.sql import func
from database import Base
import enum

class PlaylistVisibility(enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    OPEN = "OPEN"
    SHARED = "SHARED"

class Playlist(Base):
    __tablename__ = "playlist"
    
    idPlaylist = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    idGenre = Column(Integer, ForeignKey("genre.idGenre"), nullable=False, default=1)
    idOwner = Column(Integer, ForeignKey("users.idUser", ondelete="CASCADE"), nullable=False)
    vote = Column(Integer, default=0)
    visibility = Column(Enum(PlaylistVisibility), default=PlaylistVisibility.PUBLIC)
    createdAt = Column(TIMESTAMP, server_default=func.now())
    updatedAt = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())