from pydantic import BaseModel, ConfigDict
from typing import List
from .track import TrackSchema
from .playlist import PlaylistSchema


class SearchResponse(BaseModel):
    tracks: List[TrackSchema]
    playlists: List[PlaylistSchema]

    model_config = ConfigDict(from_attributes=True)
