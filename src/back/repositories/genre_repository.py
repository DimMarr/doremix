from typing import Optional, cast
from models.genre import Genre
from sqlalchemy.orm import Session
from sqlalchemy import func


class GenreRepository:
    @staticmethod
    def get_all(db: Session) -> list[Genre]:
        return cast(list[Genre], db.query(Genre).all())

    @staticmethod
    def get_by_id(db: Session, genre_id: int) -> Optional[Genre]:
        return cast(
            Optional[Genre],
            db.query(Genre).filter(Genre.idGenre == genre_id).first(),
        )

    @staticmethod
    def get_by_label(db: Session, label: str) -> Optional[Genre]:
        return cast(
            Optional[Genre],
            db.query(Genre).filter(func.lower(Genre.label) == label.lower()).first(),
        )

    @staticmethod
    def create(db: Session, label: str) -> Genre:
        genre = Genre(label=label)
        db.add(genre)
        db.commit()
        db.refresh(genre)
        return genre

    @staticmethod
    def update(db: Session, genre_id: int, label: str) -> Optional[Genre]:
        genre = GenreRepository.get_by_id(db, genre_id)
        if not genre:
            return None
        genre.label = label
        db.commit()
        db.refresh(genre)
        return genre

    @staticmethod
    def delete(db: Session, genre_id: int) -> tuple[bool, str]:
        genre = GenreRepository.get_by_id(db, genre_id)
        if not genre:
            return False, "not_found"
        # Check FK constraint: any playlist still using this genre?
        from models.playlist import Playlist

        in_use = db.query(Playlist).filter(Playlist.idGenre == genre_id).first()
        if in_use:
            return False, "in_use"
        db.delete(genre)
        db.commit()
        return True, "deleted"
