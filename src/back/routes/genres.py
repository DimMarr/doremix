from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from controllers.genre import GenreController
from schemas.genre import GenreSchema, GenreCreate, GenreUpdate
from database import get_db
from middleware.auth_middleware import require_role

router = APIRouter(prefix="/genres", tags=["Genres"])
admin_router = APIRouter(prefix="/admin/genres", tags=["Admin Genres"])


@router.get(
    "/",
    response_model=List[GenreSchema],
    summary="Lister tous les genres",
    description="Retourne la liste de tous les genres musicaux disponibles.",
)
def get_all_genres(db: Session = Depends(get_db)):
    return GenreController.get_all_genres(db)


@admin_router.post(
    "/",
    response_model=GenreSchema,
    status_code=201,
    summary="Créer un genre",
    description="Crée un nouveau genre musical. Réservé aux administrateurs.",
)
def create_genre(
    body: GenreCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    return GenreController.create_genre(db, body.label)


@admin_router.put(
    "/{genre_id}",
    response_model=GenreSchema,
    summary="Modifier un genre",
    description="Met à jour le libellé d'un genre. Réservé aux administrateurs.",
)
def update_genre(
    genre_id: int,
    body: GenreUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    return GenreController.update_genre(db, genre_id, body.label)


@admin_router.delete(
    "/{genre_id}",
    response_model=dict,
    summary="Supprimer un genre",
    description="Supprime un genre s'il n'est utilisé par aucune playlist. Réservé aux administrateurs.",
)
def delete_genre(
    genre_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    GenreController.delete_genre(db, genre_id)
    return {"detail": "Genre supprimé avec succès"}
