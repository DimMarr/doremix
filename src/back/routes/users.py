from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from back.controllers import UserController
from back.schemas import UserSchema, PlaylistSchema
from back.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=List[UserSchema],
    summary="Lister tous les utilisateurs",
    description="Retourne la liste complète des utilisateurs enregistrés.",
)
def get_users(db: Session = Depends(get_db)):
    users = UserController.get_all_users(db)
    return users


@router.get(
    "/{idUser}",
    response_model=UserSchema,
    summary="Récupérer un utilisateur",
    description="Retourne les informations détaillées d'un utilisateur à partir de son identifiant.",
)
def get_user(idUser: int, db: Session = Depends(get_db)):
    user = UserController.get_user(db, idUser)
    return user


@router.get(
    "/{idUser}/playlists",
    response_model=List[PlaylistSchema],
    summary="Récupérer les playlists d'un utilisateur",
    description="Retourne la liste des playlists associées à un utilisateur spécifique.",
)
def get_user_playlists(idUser: int, db: Session = Depends(get_db)):
    playlists = UserController.get_user_playlists(db, idUser)
    return playlists
