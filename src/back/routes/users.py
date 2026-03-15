from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
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
    response_model=list[UserSchema],
    summary="List all users",
    description="Returns the complete list of registered users.",
)
async def get_users(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    return await UserController.get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=UserSchema,
    summary="Get a user",
    description="Returns the detailed information of a user based on their ID.",
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await UserController.get_user(db, user_id)


@router.get(
    "/{user_id}/playlists",
    response_model=list[PlaylistSchema],
    summary="Get user playlists",
    description="Returns the list of playlists associated with a specific user.",
)
async def get_user_playlists(user_id: int, db: AsyncSession = Depends(get_db)):
    return await UserController.get_user_playlists(db, user_id)
