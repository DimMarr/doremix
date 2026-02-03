from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from back.controllers.artist import ArtistController
from back.schemas.artist import ArtistSchema
from back.database import get_db

router = APIRouter(prefix="/artists", tags=["Artists"])


@router.get(
    "/",
    response_model=List[ArtistSchema],
    summary="Lister tous les artistes",
    description="Retourne la liste complète des artistes disponibles.",
)
def get_artists(db: Session = Depends(get_db)):
    artists = ArtistController.get_all_artists(db)
    return artists


@router.get(
    "/{artist_id}",
    response_model=ArtistSchema,
    summary="Récupérer un artiste",
    description="Retourne les informations détaillées d'un artiste à partir de son identifiant.",
)
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = ArtistController.get_artist(db, artist_id)
    return artist
