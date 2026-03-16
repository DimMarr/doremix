from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from controllers.genre import GenreController
from schemas.genre import GenreSchema, GenreCreate, GenreUpdate
from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from models.enums import Actions, Ressources
from services.permission_service import PermissionService

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
    admin: User = Depends(get_current_user),
):
    if not PermissionService.hasPermissionsTo(
        db, admin, Actions.CREATE, Ressources.GENRE
    ):
        raise HTTPException(status_code=403, detail="Not allowed to create genres")

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
    admin: User = Depends(get_current_user),
):
    if not PermissionService.hasPermissionsTo(
        db, admin, Actions.EDIT, Ressources.GENRE
    ):
        raise HTTPException(status_code=403, detail="Not allowed to edit genres")

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
    admin: User = Depends(get_current_user),
):
    if not PermissionService.hasPermissionsTo(
        db, admin, Actions.DELETE, Ressources.GENRE
    ):
        raise HTTPException(status_code=403, detail="Not allowed to delete genres")

    GenreController.delete_genre(db, genre_id)
    return {"detail": "Genre supprimé avec succès"}
