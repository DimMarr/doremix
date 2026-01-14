from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
