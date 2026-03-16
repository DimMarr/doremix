from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from database import Base


class UserGroup(Base):
    __tablename__ = "user_group"
    idGroup = Column("idgroup", Integer, primary_key=True, index=True)
    groupName = Column("groupname", String(255), unique=True, nullable=False)


class GroupUser(Base):
    __tablename__ = "group_user"
    idUser = Column(
        "iduser",
        Integer,
        ForeignKey("users.iduser", ondelete="CASCADE"),
        primary_key=True,
    )
    idGroup = Column(
        "idgroup",
        Integer,
        ForeignKey("user_group.idgroup", ondelete="CASCADE"),
        primary_key=True,
    )
    isBaseRole = Column("isbaserole", Boolean, default=False)


class GroupPlaylist(Base):
    __tablename__ = "group_playlist"
    idGroup = Column(
        "idgroup",
        Integer,
        ForeignKey("user_group.idgroup", ondelete="CASCADE"),
        primary_key=True,
    )
    idPlaylist = Column(
        "idplaylist",
        Integer,
        ForeignKey("playlist.idplaylist", ondelete="CASCADE"),
        primary_key=True,
    )
