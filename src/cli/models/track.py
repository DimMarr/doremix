from pydantic import BaseModel
from typing import List
from datetime import datetime
from models.artist import ArtistSchema


class TrackSchema(BaseModel):
    idTrack: int
    title: str
    youtubeLink: str | None = None
    listeningCount: int
    durationSeconds: int | None = None
    createdAt: datetime
    artists: List[ArtistSchema]
