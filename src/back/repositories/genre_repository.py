from sqlalchemy.orm import Session
from models.genre import Genre
from typing import Optional, List


class GenreRepository:
    @staticmethod
    def get_all(db: Session) -> List[Genre]:
        return db.query(Genre).all()

    @staticmethod
    def get_by_id(db: Session, genre_id: int) -> Optional[Genre]:
        return db.query(Genre).filter(Genre.idGenre == genre_id).first()
