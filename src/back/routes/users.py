from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from controllers import UserController
from schemas import UserSchema, PlaylistSchema
from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from models.enums import Actions, Ressources
from services.permission_service import PermissionService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=List[UserSchema],
    summary="Lister tous les utilisateurs",
    description="Retourne la liste complète des utilisateurs enregistrés.",
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not PermissionService.hasPermissionsTo(
        db, current_user, Actions.READ, Ressources.USER
    ):
        raise HTTPException(status_code=403, detail="Not allowed to list users")
    users = UserController.get_all_users(db)
    return users


@router.get(
    "/{idUser}",
    response_model=UserSchema,
    summary="Récupérer un utilisateur",
    description="Retourne les informations détaillées d'un utilisateur à partir de son identifiant.",
)
def get_user(
    idUser: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not PermissionService.hasPermissionsTo(
        db, current_user, Actions.READ, Ressources.USER
    ):
        raise HTTPException(status_code=403, detail="Not allowed to view user details")
    user = UserController.get_user(db, idUser)
    return user


@router.get(
    "/{idUser}/playlists",
    response_model=List[PlaylistSchema],
    summary="Récupérer les playlists d'un utilisateur",
    description="Retourne la liste des playlists associées à un utilisateur spécifique.",
)
def get_user_playlists(
    idUser: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not PermissionService.hasPermissionsTo(
        db, current_user, Actions.READ, Ressources.USER
    ):
        raise HTTPException(
            status_code=403, detail="Not allowed to view user playlists"
        )
    playlists = UserController.get_user_playlists(db, idUser)
    return playlists
