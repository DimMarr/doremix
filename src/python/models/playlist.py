from pydantic import BaseModel
from visibility import Visibility
from datetime import datetime

class PlaylistBase(BaseModel):
    name: str
    idGenre: int
    idOwner: int
    vote: int = 0
    visibility: Visibility

class Playlist(PlaylistBase):
    idPlaylist: int
    createdAt: datetime
    updatedAt: datetime