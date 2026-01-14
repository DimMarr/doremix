from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional


class PlaylistVisibility(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    OPEN = "OPEN"
    SHARED = "SHARED"


class PlaylistSchema(BaseModel):
    idPlaylist: int
    name: str
    idGenre: int
    idOwner: int
    vote: int
    visibility: PlaylistVisibility
    coverImage: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class PlaylistSchemaCreate(BaseModel):
    name: str
    idGenre: Optional[int] = 1
    idOwner: Optional[int] = 1  # This should be set when we will have authentication
    vote: Optional[int] = 0
    visibility: Optional[PlaylistVisibility] = PlaylistVisibility.PUBLIC
    coverImage: Optional[str] = None
