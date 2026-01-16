from sqlalchemy.orm import Session
from repositories.genre_repository import GenreRepository
from fastapi import HTTPException


class GenreController:
    @staticmethod
    def get_all_genres(db: Session):
        return GenreRepository.get_all(db)

    @staticmethod
    def get_genre(db: Session, genre_id: int):
        genre = GenreRepository.get_by_id(db, genre_id)
        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")
        return genre
