from sqlalchemy import Column, Integer, ForeignKey
from back.database import Base


class TrackPlaylist(Base):
    __tablename__ = "track_playlist"

    idTrack = Column(
        "idtrack",
        Integer,
        ForeignKey("track.idtrack", ondelete="CASCADE"),
        primary_key=True,
    )
    idPlaylist = Column(
        "idplaylist",
        Integer,
        ForeignKey("playlist.idplaylist", ondelete="CASCADE"),
        primary_key=True,
    )
