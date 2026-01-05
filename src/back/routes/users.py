from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from controllers import UserController
from schemas import UserSchema, PlaylistSchema
from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=List[UserSchema],
    summary="Lister tous les utilisateurs",
    description="Retourne la liste complète des utilisateurs enregistrés.",
)
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await UserController.get_all_users(db)
    return users


@router.get(
    "/{idUser}",
    response_model=UserSchema,
    summary="Récupérer un utilisateur",
    description="Retourne les informations détaillées d'un utilisateur à partir de son identifiant.",
)
async def get_user(idUser: int, db: AsyncSession = Depends(get_db)):
    user = await UserController.get_user(db, idUser)
    return user


@router.get(
    "/{idUser}/playlists",
    response_model=List[PlaylistSchema],
    summary="Récupérer les playlists d'un utilisateur",
    description="Retourne la liste des playlists associées à un utilisateur spécifique.",
)
async def get_user_playlists(idUser: int, db: AsyncSession = Depends(get_db)):
    playlists = await UserController.get_user_playlists(db, idUser)
    return playlists
