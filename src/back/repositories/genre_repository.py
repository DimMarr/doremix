from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.genre import Genre
from typing import Optional, List


class GenreRepository:
    @staticmethod
    def get_all(db: Session) -> List[Genre]:
        return db.query(Genre).all()

    @staticmethod
    def get_by_id(db: Session, genre_id: int) -> Optional[Genre]:
        return db.query(Genre).filter(Genre.idGenre == genre_id).first()

    @staticmethod
    def create(db: Session, label: str) -> Genre:
        genre = Genre(label=label)
        db.add(genre)
        db.commit()
        db.refresh(genre)
        return genre

    @staticmethod
    def update(db: Session, genre_id: int, label: str) -> Genre:
        genre = GenreRepository.get_by_id(db, genre_id)
        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Genre {genre_id} not found",
            )
        genre.label = label
        db.commit()
        db.refresh(genre)
        return genre

    @staticmethod
    def delete(db: Session, genre_id: int) -> bool:
        genre = GenreRepository.get_by_id(db, genre_id)
        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Genre {genre_id} not found",
            )
        # Check FK constraint: any playlist still using this genre?
        from models.playlist import Playlist
        in_use = db.query(Playlist).filter(Playlist.idGenre == genre_id).first()
        if in_use:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete genre: it is still used by one or more playlists",
            )
        db.delete(genre)
        db.commit()
        return True
