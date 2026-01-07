from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from models.track import Track
from models.artist import Artist
from typing import Optional, List


class TrackRepository:
    @staticmethod
    def get_all(db: Session) -> List[Track]:
        return db.query(Track).all()

    @staticmethod
    def get_by_id(db: Session, track_id: int) -> Optional[Track]:
        return db.query(Track).filter(Track.idTrack == track_id).first()

    @staticmethod
    def search_tracks(db: Session, query: str, limit: int = 10):
        tracks = (
            db.query(Track)
            .join(Track.artists)
            .options(joinedload(Track.artists))
            .filter(
                or_(
                    Track.title.ilike(f"%{query}%"),
                    Artist.name.ilike(f"%{query}%")
                )
            )
            .distinct()
            .limit(limit)
            .all()
        )
        
        return tracks

