from sqlalchemy.orm import Session
from back.repositories.artist_repository import ArtistRepository
from fastapi import HTTPException


class ArtistController:
    @staticmethod
    def get_all_artists(db: Session):
        return ArtistRepository.get_all(db)

    @staticmethod
    def get_artist(db: Session, artist_id: int):
        artist = ArtistRepository.get_by_id(db, artist_id)
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")
        return artist
