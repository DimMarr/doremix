from sqlalchemy.orm import Session
from fastapi import HTTPException, status
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
        if GenreRepository.get_by_label(db, label):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Genre already exists",
            )
        return GenreRepository.create(db, label)

    @staticmethod
    def update_genre(db: Session, genre_id: int, label: str) -> Genre:
        existing = GenreRepository.get_by_label(db, label)
        if existing and existing.idGenre != genre_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Genre already exists",
            )

        genre = GenreRepository.update(db, genre_id, label)
        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Genre {genre_id} not found",
            )
        return genre

    @staticmethod
    def delete_genre(db: Session, genre_id: int) -> bool:
        deleted, reason = GenreRepository.delete(db, genre_id)
        if not deleted:
            if reason == "not_found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Genre {genre_id} not found",
                )
            if reason == "in_use":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete genre: it is still used by one or more playlists",
                )
        return deleted
