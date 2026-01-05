from sqlalchemy.orm import Session
from repositories import TrackRepository
from fastapi import HTTPException


class TrackController:
    @staticmethod
    async def get_all_tracks(db: Session):
        return await TrackRepository.get_all(db)

    @staticmethod
    async def get_track(db: Session, track_id: int):
        track = await TrackRepository.get_by_id(db, track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        return track
