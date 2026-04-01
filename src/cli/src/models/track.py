from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime
from .artist import ArtistSchema

TrackStatus = Literal["ok", "unavailable"]


class TrackSchema(BaseModel):
    idTrack: int
    title: str
    youtubeLink: str | None = None
    listeningCount: int
    durationSeconds: int | None = None
    createdAt: datetime
    artists: List[ArtistSchema]
    status: TrackStatus = "ok"

    def is_playable(self) -> bool:
        return self.status == "ok"
