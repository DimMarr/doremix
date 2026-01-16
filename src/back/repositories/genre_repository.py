from sqlalchemy.orm import Session
from models.genre import Genre
from typing import Optional, List


class GenreRepository:
    @staticmethod
    def get_all(db: Session) -> List[Genre]:
        return db.query(Genre).all()
