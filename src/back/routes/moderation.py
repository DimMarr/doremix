from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from controllers import UserController
from database import get_db
from middleware.auth_middleware import require_role, get_current_user_id
from schemas.user import ModerationUserSchema, UserBanStatusResponse

router = APIRouter(prefix="/moderation", tags=["Moderation"])


@router.get(
    "/ban-candidates",
    response_model=list[ModerationUserSchema],
    summary="List users that can be banned",
    description="Returns non-admin users that are not banned yet. Reserved to moderators.",
)
async def get_ban_candidates(
    db: AsyncSession = Depends(get_db),
    moderator_id: int = Depends(get_current_user_id),
    _moderator=Depends(require_role(["MODERATOR"])),
):
    return await UserController.get_ban_candidates(db, moderator_id)


@router.get(
    "/unban-candidates",
    response_model=List[ModerationUserSchema],
    summary="List users that can be unbanned",
    description="Returns banned users. Reserved to moderators.",
)
async def get_unban_candidates(
    db: AsyncSession = Depends(get_db),
    _moderator=Depends(require_role(["MODERATOR"])),
):
    return await UserController.get_unban_candidates(db)


@router.post(
    "/users/{idUser}/ban",
    response_model=UserBanStatusResponse,
    summary="Ban a user",
    description="Ban a non-admin user and revoke all their tokens. Reserved to moderators.",
)
async def ban_user(
    idUser: int,
    db: AsyncSession = Depends(get_db),
    moderator_id: int = Depends(get_current_user_id),
    _moderator=Depends(require_role(["MODERATOR"])),
):
    user = await UserController.ban_user(db, moderator_id, idUser)
    return {
        "idUser": user.idUser,
        "banned": user.banned,
        "detail": "User banned and tokens revoked",
    }


@router.post(
    "/users/{idUser}/unban",
    response_model=UserBanStatusResponse,
    summary="Unban a user",
    description="Unban a user. Reserved to moderators.",
)
async def unban_user(
    idUser: int,
    db: AsyncSession = Depends(get_db),
    moderator_id: int = Depends(get_current_user_id),
    _moderator=Depends(require_role(["MODERATOR"])),
):
    user = await UserController.unban_user(db, moderator_id, idUser)
    return {
        "idUser": user.idUser,
        "banned": user.banned,
        "detail": "User unbanned",
    }
