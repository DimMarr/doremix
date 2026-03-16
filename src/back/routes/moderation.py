from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from controllers import UserController
from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from models.enums import Actions, Ressources
from services.permission_service import PermissionService
from schemas.user import ModerationUserSchema, BanUserResponse

router = APIRouter(prefix="/moderation", tags=["Moderation"])


@router.get(
    "/ban-candidates",
    response_model=List[ModerationUserSchema],
    summary="List users that can be banned",
    description="Returns non-admin users that are not banned yet. Reserved to moderators.",
)
def get_ban_candidates(
    db: Session = Depends(get_db),
    moderator: User = Depends(get_current_user),
):
    if not PermissionService.hasPermissionsTo(
        db, moderator, Actions.BAN, Ressources.USER
    ):
        raise HTTPException(status_code=403, detail="Not allowed to ban users")

    return UserController.get_ban_candidates(db, moderator.idUser)


@router.post(
    "/users/{idUser}/ban",
    response_model=BanUserResponse,
    summary="Ban a user",
    description="Ban a non-admin user and revoke all their tokens. Reserved to moderators.",
)
def ban_user(
    idUser: int,
    db: Session = Depends(get_db),
    moderator: User = Depends(get_current_user),
):
    if not PermissionService.hasPermissionsTo(
        db, moderator, Actions.BAN, Ressources.USER, idUser
    ):
        raise HTTPException(status_code=403, detail="Not allowed to ban this user")

    user = UserController.ban_user(db, moderator.idUser, idUser)
    return {
        "idUser": user.idUser,
        "banned": user.banned,
        "detail": "User banned and tokens revoked",
    }
