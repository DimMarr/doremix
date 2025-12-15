from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TrackSchema(BaseModel):
    idTrack: int
    title: str
    youtubeLink: str = None
    listeningCount: int
    durationSeconds: Optional[int] = None
    createdAt: datetime

    model_config = {
        "from_attributes": True
    }