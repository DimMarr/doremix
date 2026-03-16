from sqlalchemy import Column, Integer, String, Boolean, and_
from sqlalchemy.orm import relationship
from database import Base
import enum


class UserRole(enum.Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


_ROLE_MAPPING = {
    "Utilisateurs normaux": UserRole.USER,
    "Modérateurs": UserRole.MODERATOR,
    "Admins": UserRole.ADMIN,
}


class User(Base):
    __tablename__ = "users"

    idUser = Column("iduser", Integer, primary_key=True, index=True)
    email = Column("email", String(255), unique=True, nullable=False)
    password = Column("password", String(255), nullable=False)
    username = Column("username", String(255), nullable=False)
    banned = Column("banned", Boolean, default=False)
    isVerified = Column("isverified", Boolean, default=False)  # for email verification

    playlists = relationship(
        "Playlist", secondary="user_playlist", back_populates="users"
    )

    # Loads the single UserGroup where isBaseRole=True for this user
    _base_group = relationship(
        "UserGroup",
        secondary="group_user",
        primaryjoin="and_(User.idUser == foreign(GroupUser.idUser), GroupUser.isBaseRole)",
        secondaryjoin="UserGroup.idGroup == foreign(GroupUser.idGroup)",
        uselist=False,
        viewonly=True,
        lazy="joined",
    )

    @property
    def role(self) -> UserRole:
        """Derives the user's role from their base-role group (isBaseRole=True)."""
        if self._base_group is None:
            return UserRole.USER
        return _ROLE_MAPPING.get(self._base_group.groupName, UserRole.USER)
