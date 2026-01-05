from sqlalchemy.orm import Session
from models import Track
from typing import Optional, List


class TrackRepository:
    @staticmethod
    def get_all(db: Session) -> List[Track]:
        return db.query(Track).all()

    @staticmethod
    def get_by_id(db: Session, track_id: int) -> Optional[Track]:
        return db.query(Track).filter(Track.idTrack == track_id).first()
