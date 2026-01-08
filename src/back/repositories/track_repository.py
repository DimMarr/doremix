from sqlalchemy.orm import Session
from models.track import Track
from typing import Optional, List


class TrackRepository:
    @staticmethod
    def create(db: Session, track: Track) -> Track:
        db.add(track)
        db.commit()
        db.refresh(track)
        return track

    @staticmethod
    def get_all(db: Session) -> List[Track]:
        return db.query(Track).all()

    @staticmethod
    def get_by_id(db: Session, track_id: int) -> Optional[Track]:
        return db.query(Track).filter(Track.idTrack == track_id).first()

    @staticmethod
    def get_by_youtube_link(db: Session, youtube_link: str) -> Optional[Track]:
        return db.query(Track).filter(Track.youtubeLink == youtube_link).first()
