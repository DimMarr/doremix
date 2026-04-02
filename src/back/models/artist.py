from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Artist(Base):
    __tablename__ = "artist"

    idArtist = Column("idartist", Integer, primary_key=True, index=True)
    name = Column("name", String(255), nullable=False, index=True)
    imageUrl = Column("imageurl", String(2048), nullable=True)

    tracks = relationship("Track", secondary="track_artist", back_populates="artists")
