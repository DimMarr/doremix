from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


class UserRole(enum.Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    idUser = Column("iduser", Integer, primary_key=True, index=True)
    email = Column("email", String(255), unique=True, nullable=False)
    password = Column("password", String(255), nullable=False)
    username = Column("username", String(255), nullable=False)
    idRole = Column("idrole", Integer, default=1)
    banned = Column("banned", Boolean, default=False)
    isVerified = Column("isverified", Boolean, default=False)  # for email verification

    playlists = relationship(
        "Playlist", secondary="user_playlist", back_populates="users", lazy="selectin"
    )

    @property
    def role(self) -> UserRole:
        if self.idRole == 2:
            return UserRole.MODERATOR
        elif self.idRole == 3:
            return UserRole.ADMIN
        # Default :
        return UserRole.USER

    # To be able to do user.role = UserRole.ADMIN
    @role.setter
    def role(self, role_enum: UserRole):
        if role_enum == UserRole.MODERATOR:
            self.idRole = 2
        elif role_enum == UserRole.ADMIN:
            self.idRole = 3
        else:
            self.idRole = 1
