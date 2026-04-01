from sqlalchemy import CheckConstraint, Column, ForeignKey, SmallInteger

from database import Base


class PlaylistVote(Base):
    __tablename__ = "playlist_vote"
    __table_args__ = (
        CheckConstraint("value IN (-1, 1)", name="playlist_vote_value_check"),
    )

    idUser = Column(
        "iduser",
        ForeignKey("users.iduser", ondelete="CASCADE"),
        primary_key=True,
    )
    idPlaylist = Column(
        "idplaylist",
        ForeignKey("playlist.idplaylist", ondelete="CASCADE"),
        primary_key=True,
    )
    value = Column("value", SmallInteger, nullable=False)
