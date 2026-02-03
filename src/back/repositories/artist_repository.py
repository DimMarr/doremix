from sqlalchemy.orm import Session
from back.models.artist import Artist
from typing import Optional, List


class ArtistRepository:
    @staticmethod
    def create(db: Session, artist_name: str) -> Artist:
        """Create a new artist if it does not already exist."""
        artist = ArtistRepository.get_by_name(db, artist_name)
        if not artist:
            artist = Artist(name=artist_name)
            db.add(artist)
            db.commit()
            db.refresh(artist)
        return artist

    @staticmethod
    def get_all(db: Session) -> List[Artist]:
        artists: List[Artist] = db.query(Artist).all()
        return artists

    @staticmethod
    def get_by_id(db: Session, artist_id: int) -> Optional[Artist]:
        artists: Optional[Artist] = (
            db.query(Artist).filter(Artist.idArtist == artist_id).first()
        )
        return artists

    @staticmethod
    def get_by_name(db: Session, artist_name: str) -> Optional[Artist]:
        artists: Optional[Artist] = (
            db.query(Artist).filter(Artist.name == artist_name).first()
        )
        return artists
