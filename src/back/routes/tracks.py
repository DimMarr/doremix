from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from controllers import TrackController
from schemas import TrackSchema
from database import get_db

router = APIRouter(prefix="/tracks", tags=["Tracks"])


@router.get(
    "/",
    response_model=List[TrackSchema],
    summary="Lister tous les morceaux",
    description="Retourne la liste complète des morceaux disponibles."
)
def get_tracks(db: Session = Depends(get_db)):
    tracks = TrackController.get_all_tracks(db)
    return tracks


@router.get(
    "/{track_id}",
    response_model=TrackSchema,
    summary="Récupérer un morceau",
    description="Retourne les informations détaillées d'un morceau à partir de son identifiant."
)
def get_track(track_id: int, db: Session = Depends(get_db)):
    track = TrackController.get_track(db, track_id)
    return track