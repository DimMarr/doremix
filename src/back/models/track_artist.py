from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class TrackArtist(Base):
    __tablename__ = "track_artist"
    
    idTrack = Column(Integer, ForeignKey("track.idTrack", ondelete="CASCADE"), primary_key=True)
    idArtist = Column(Integer, ForeignKey("artist.idArtist", ondelete="CASCADE"), primary_key=True)