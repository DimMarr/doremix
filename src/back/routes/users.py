from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from controllers import UserController
from schemas import UserSchema, PlaylistSchema
from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


# =========================
# GET routes
# =========================
@router.get(
    "/",
    response_model=List[UserSchema],
    summary="List all users",
    description="Returns the complete list of registered users.",
)
async def get_users(db: AsyncSession = Depends(get_db)):
    users = await UserController.get_all_users(db)
    return users


@router.get(
    "/{idUser}",
    response_model=UserSchema,
    summary="Get a user by ID",
    description="Returns the detailed information of a user based on its ID.",
)
async def get_user(idUser: int, db: AsyncSession = Depends(get_db)):
    user = await UserController.get_user(db, idUser)
    return user
