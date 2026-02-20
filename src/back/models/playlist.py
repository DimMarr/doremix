from sqlalchemy import Column, Integer, String, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum
from .enums import PlaylistVisibility


class Playlist(Base):
    __tablename__ = "playlist"

    idPlaylist = Column("idplaylist", Integer, primary_key=True, index=True)
    name = Column("name", String(255), nullable=False, index=True)
    idGenre = Column(
        "idgenre", Integer, ForeignKey("genre.idgenre"), nullable=False, default=1
    )
    idOwner = Column(
        "idowner",
        Integer,
        ForeignKey("users.iduser", ondelete="CASCADE"),
        nullable=False,
    )
    owner = relationship("User", foreign_keys=[idOwner])
    vote = Column("vote", Integer, default=0)
    visibility = Column(
        "visibility", Enum(PlaylistVisibility), default=PlaylistVisibility.PRIVATE
    )
    coverImage = Column("coverimage", String(500), nullable=True)
    createdAt = Column("createdat", TIMESTAMP, server_default=func.now())
    updatedAt = Column(
        "updatedat", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    genre = relationship("Genre", foreign_keys=[idGenre])

    tracks = relationship(
        "Track", secondary="track_playlist", back_populates="playlists"
    )

    users = relationship("User", secondary="user_playlist", back_populates="playlists")
