from sqlalchemy import Column, Integer, String, ForeignKey, Enum, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
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
    vote = Column("vote", Integer, default=0)
    visibility = Column(
        "visibility",
        Enum(PlaylistVisibility, native_enum=False),
        default=PlaylistVisibility.PRIVATE,
    )
    coverImage = Column("coverimage", String(500), nullable=True)
    isLikedPlaylist = Column("islikedplaylist", Boolean, nullable=False, default=False)
    createdAt = Column("createdat", TIMESTAMP, server_default=func.now())
    updatedAt = Column(
        "updatedat", TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("User", foreign_keys=[idOwner], lazy="selectin")
    genre = relationship("Genre", foreign_keys=[idGenre], lazy="selectin")
    tracks = relationship(
        "Track",
        secondary="track_playlist",
        primaryjoin="Playlist.idPlaylist == foreign(track_playlist.c.idplaylist)",
        secondaryjoin="Track.idTrack == foreign(track_playlist.c.idtrack)",
        back_populates="playlists",
        lazy="selectin",
    )
    users = relationship(
        "User", secondary="user_playlist", back_populates="playlists", lazy="selectin"
    )
