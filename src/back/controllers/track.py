from sqlalchemy.orm import Session
from repositories import TrackRepository
from fastapi import HTTPException


class TrackController:
    @staticmethod
    def get_all_tracks(db: Session):
        return TrackRepository.get_all(db)

    @staticmethod
    def get_track(db: Session, track_id: int):
        track = TrackRepository.get_by_id(db, track_id)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        return track
    
    @staticmethod
    def search(db: Session, query: str):
        if not query or len(query) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        
        tracks = TrackRepository.search_tracks(db, query)
        return tracks
