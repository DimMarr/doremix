from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class UserPlaylist(Base):
    __tablename__ = "user_playlist"

    idUser = Column(
        "iduser",
        Integer,
        ForeignKey("users.iduser", ondelete="CASCADE"),
        primary_key=True,
    )
    idPlaylist = Column(
        "idplaylist",
        Integer,
        ForeignKey("playlist.idplaylist", ondelete="CASCADE"),
        primary_key=True,
    )
    editor = Column("editor", Boolean, default=False)

    user = relationship("User", lazy="joined", overlaps="playlists,users")
