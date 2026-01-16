from sqlalchemy.orm import Session
from repositories.genre_repository import GenreRepository
from fastapi import HTTPException


class GenreController:
    @staticmethod
    def get_all_genres(db: Session):
        return GenreRepository.get_all(db)
