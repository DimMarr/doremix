from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .artist import ArtistSchema


class TrackSchema(BaseModel):
    idTrack: int
    title: str
    youtubeLink: Optional[str] = None
    listeningCount: int
    durationSeconds: Optional[int] = None
    createdAt: datetime
    artists: List[ArtistSchema]

    model_config = ConfigDict(from_attributes=True)
