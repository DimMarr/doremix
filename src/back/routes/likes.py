from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from controllers.like import LikeController
from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User

router = APIRouter(prefix="/tracks", tags=["Likes"])


@router.post(
    "/{track_id}/like",
    summary="Like a track",
    description="Adds a track to the user's liked tracks.",
)
async def like_track(
    track_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await LikeController.like_track(db, track_id, user)


@router.delete(
    "/{track_id}/like",
    summary="Unlike a track",
    description="Removes a track from the user's liked tracks.",
)
async def unlike_track(
    track_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await LikeController.unlike_track(db, track_id, user)


@router.get(
    "/{track_id}/like",
    summary="Get like status",
    description="Returns whether the current user has liked a track.",
)
async def get_like_status(
    track_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await LikeController.get_like_status(db, track_id, user)
