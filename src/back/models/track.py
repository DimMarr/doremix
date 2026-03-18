from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Track(Base):
    __tablename__ = "track"

    idTrack = Column("idtrack", Integer, primary_key=True, index=True)
    title = Column("title", String(255), nullable=False, index=True)
    youtubeLink = Column("youtubelink", String(2048), nullable=True)
    listeningCount = Column("listeningcount", Integer, default=0)
    durationSeconds = Column("durationseconds", Integer, nullable=True)
    createdAt = Column("createdat", TIMESTAMP, server_default=func.now())

    playlists = relationship(
        "Playlist", secondary="track_playlist", back_populates="tracks"
    )

    artists = relationship(
        "Artist", secondary="track_artist", back_populates="tracks", lazy="selectin"
    )
