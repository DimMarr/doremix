from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional, List
from .playlist import PlaylistSchema


class UserRole(str, Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class UserSchema(BaseModel):
    idUser: int
    email: str
    username: str
    role: UserRole
    banned: bool
    playlists: Optional[List[PlaylistSchema]] = None

    model_config = ConfigDict(from_attributes=True)
