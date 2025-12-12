from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class TrackArtist(Base):
    __tablename__ = "track_artist"
    
    idTrack = Column("idtrack", Integer, ForeignKey("track.idtrack", ondelete="CASCADE"), primary_key=True)
    idArtist = Column("idartist", Integer, ForeignKey("artist.idartist", ondelete="CASCADE"), primary_key=True)