from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class TrackPlaylist(Base):
    __tablename__ = "track_playlist"
    
    idTrack = Column(Integer, ForeignKey("track.idTrack", ondelete="CASCADE"), primary_key=True)
    idPlaylist = Column(Integer, ForeignKey("playlist.idPlaylist", ondelete="CASCADE"), primary_key=True)