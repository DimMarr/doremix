from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class PlaylistVisibility(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    OPEN = "OPEN"


class PlaylistSchema(BaseModel):
    idPlaylist: int
    name: str
    idGenre: int
    idOwner: int
    vote: int
    isShared: bool = False
    visibility: PlaylistVisibility
    coverImage: str | None = None
    createdAt: datetime
    updatedAt: datetime


class SharedUserSchema(BaseModel):
    idUser: int
    idPlaylist: int
    editor: bool
    username: str
    email: str
