from pydantic import BaseModel
from typing import List
from datetime import datetime
from .artist import ArtistSchema


class TrackSchema(BaseModel):
    idTrack: int
    titleFromYoutube: str
    youtubeLink: str | None = None
    listeningCount: int
    durationSeconds: int | None = None
    createdAt: datetime
    artists: List[ArtistSchema]
