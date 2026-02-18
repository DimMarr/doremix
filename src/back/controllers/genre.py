from sqlalchemy.orm import Session
from repositories.genre_repository import GenreRepository
from models.genre import Genre
from typing import List, Optional


class GenreController:
    @staticmethod
    def get_all_genres(db: Session) -> List[Genre]:
        return GenreRepository.get_all(db)

    @staticmethod
    def get_genre(db: Session, genre_id: int) -> Optional[Genre]:
        return GenreRepository.get_by_id(db, genre_id)

    @staticmethod
    def create_genre(db: Session, label: str) -> Genre:
        return GenreRepository.create(db, label)

    @staticmethod
    def update_genre(db: Session, genre_id: int, label: str) -> Genre:
        return GenreRepository.update(db, genre_id, label)

    @staticmethod
    def delete_genre(db: Session, genre_id: int) -> bool:
        return GenreRepository.delete(db, genre_id)
