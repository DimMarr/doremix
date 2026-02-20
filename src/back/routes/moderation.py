from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from controllers import UserController
from database import get_db
from middleware.auth_middleware import require_role, get_current_user_id
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
    moderator_id: int = Depends(get_current_user_id),
    _moderator=Depends(require_role(["MODERATOR"])),
):
    return UserController.get_ban_candidates(db, moderator_id)


@router.post(
    "/users/{idUser}/ban",
    response_model=BanUserResponse,
    summary="Ban a user",
    description="Ban a non-admin user and revoke all their tokens. Reserved to moderators.",
)
def ban_user(
    idUser: int,
    db: Session = Depends(get_db),
    moderator_id: int = Depends(get_current_user_id),
    _moderator=Depends(require_role(["MODERATOR"])),
):
    user = UserController.ban_user(db, moderator_id, idUser)
    return {
        "idUser": user.idUser,
        "banned": user.banned,
        "detail": "User banned and tokens revoked",
    }
