from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from controllers.genre import GenreController
from schemas.genre import GenreSchema
from database import get_db

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get(
    "/",
    response_model=List[GenreSchema],
    summary="Lister tous les genres",
    description="Retourne la liste complète des genres disponibles.",
)
def get_genres(db: Session = Depends(get_db)):
    genres = GenreController.get_all_genres(db)
    return genres
