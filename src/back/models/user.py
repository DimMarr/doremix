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
    role = Column("role", Enum(UserRole), default=UserRole.USER)
    banned = Column("banned", Boolean, default=False)

    playlists = relationship(
        "Playlist",
        secondary="user_playlist",
        back_populates="users"
    )