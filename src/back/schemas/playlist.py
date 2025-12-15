from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime

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