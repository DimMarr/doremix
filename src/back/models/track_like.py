from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from database import Base


class TrackLike(Base):
    __tablename__ = "track_like"

    idUser = Column(
        "iduser",
        Integer,
        ForeignKey("users.iduser", ondelete="CASCADE"),
        primary_key=True,
    )
    idTrack = Column(
        "idtrack",
        Integer,
        ForeignKey("track.idtrack", ondelete="CASCADE"),
        primary_key=True,
    )
    createdAt = Column("createdat", TIMESTAMP, server_default=func.now())
