from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional
from models.enums import PlaylistVisibility
from schemas.genre import GenreSchema


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
    genre: Optional[GenreSchema] = None

    model_config = ConfigDict(from_attributes=True)


class PlaylistCreate(BaseModel):
    name: str
    idGenre: int = 1
    visibility: PlaylistVisibility = PlaylistVisibility.PRIVATE
    # idOwner: int  # TODO: À récupérer depuis le token JWT quand l'auth sera en place


class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    idGenre: Optional[int] = None
    visibility: Optional[PlaylistVisibility] = None
    model_config = ConfigDict(from_attributes=True)


class SharePlaylistRequest(BaseModel):
    target_email: str  # L'email de la personne à inviter
    is_editor: bool = False  # False = Lecture seule, True = Peut modifier


class ShareGroupRequest(BaseModel):
    group_name: str


class ReorderTrackRequest(BaseModel):
    track_id: int
    after_track_id: Optional[int] = None
